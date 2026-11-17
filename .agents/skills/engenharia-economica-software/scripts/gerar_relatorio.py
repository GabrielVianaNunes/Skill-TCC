#!/usr/bin/env python3
"""Orquestrador: gera a valoração completa de um projeto de software a partir de um JSON.

Executa, nesta ordem, os módulos da skill (estimar_esforco_git, calc_custos_preco,
calc_depreciacao_tributos, calc_vpl_tir, sensibilidade, calc_gva, comparar_alternativas,
priorizar_backlog e metricas_produto) e escreve um relatório Markdown com as seções exigidas:
sumário executivo, premissas, I Fluxo de Caixa, II VPL, III TIR, IV Payback, sensibilidade e
cenários, V GVA, VI modelo de negócio, decisões de engenharia, backlog, riscos e limitações.

Modelo econômico (valores reais, fluxos anuais, t = 0 na implantação):

* Leitura A (ativo a partir de hoje): F_0 = -implantação; F_t = benefícios_t - OpEx_t.
* Leitura B (viabilidade total): igual à A, com F_0 acrescido do custo econômico do desenvolvimento.
* Cenários: pessimista usa o mínimo de cada fator de benefício e o máximo de cada fator de custo;
  otimista faz o inverso; base usa o valor provável. Parâmetros com ``sentido_fixo`` (por exemplo,
  número de usuários) usam o mesmo valor em benefício e custo, para manter coerência.

O esquema da entrada está em references/esquema-entrada.md e um modelo em assets/modelo_entrada.json.

Uso::

    python gerar_relatorio.py --entrada projeto.json --saida-md relatorio.md --saida-json relatorio.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import calc_custos_preco as ccp
import calc_depreciacao_tributos as cdt
import calc_gva
import comparar_alternativas as calt
import estimar_esforco_git as eeg
import metricas_produto as mp
import priorizar_backlog as pb
import sensibilidade as sens
from _comum import anos_meses, arred, brl, num, pct, tabela_md
from calc_tvm import anual_para_mensal, compor_tma, fator_vp_serie
from calc_vpl_tir import analisar, descrever_tir, vpl

CENARIOS = ("pessimista", "base", "otimista")
AQUI = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(AQUI, "..", "assets", "proposta_executiva_template.md")


# ------------------------------------------------------------------ parâmetros e cenários
def valor_param(params: dict, nome: str, cenario: str, sentido: str) -> float:
    """Valor de um parâmetro no cenário, conforme o sentido (beneficio ou custo)."""
    spec = params[nome]
    if not isinstance(spec, dict):
        return float(spec)
    if cenario == "base":
        return float(spec["provavel"])
    sentido = spec.get("sentido_fixo", sentido)
    desfavoravel = "min" if sentido == "beneficio" else "max"
    favoravel = "max" if sentido == "beneficio" else "min"
    return float(spec[desfavoravel] if cenario == "pessimista" else spec[favoravel])


def avaliar_qtd(expr, params: dict, cenario: str, sentido: str) -> float:
    """Aceita número ou expressão simples 'k*parametro'."""
    if isinstance(expr, (int, float)):
        return float(expr)
    total = 1.0
    for termo in str(expr).split("*"):
        termo = termo.strip()
        try:
            total *= float(termo)
        except ValueError:
            total *= valor_param(params, termo, cenario, sentido)
    return total


def componentes(itens: list[dict], params: dict, cenario: str, sentido: str) -> list[dict]:
    """Valor anual de cada componente = produto dos fatores x multiplicador."""
    saida = []
    for it in itens:
        valor = float(it.get("multiplicador", 1))
        for f in it["fatores"]:
            valor *= valor_param(params, f, cenario, sentido)
        saida.append({"nome": it["nome"], "anual": valor})
    return saida


# ------------------------------------------------------------------ modelo principal
def custo_desenvolvimento(dados: dict, esforco: dict, cenario: str) -> dict:
    """Horas (histórico do git + base importada) x taxa horária + custos indiretos rateados."""
    chave = {"pessimista": "max", "base": "provavel", "otimista": "min"}[cenario]
    horas_git = esforco["totais"][chave]
    base = esforco.get("base_importada")
    horas_base = base[f"horas_{chave}"] if base else 0.0
    taxa = valor_param(dados["parametros"], "taxa_hora_dev", cenario, "custo")
    custos = ccp.calcular({
        "equipe": [{"papel": "Desenvolvimento antes do primeiro commit (base importada)", "horas": horas_base, "taxa_hora": taxa},
                   {"papel": "Desenvolvimento registrado no git", "horas": horas_git, "taxa_hora": taxa}],
        "indiretos": dados.get("custos_indiretos_desenvolvimento", []),
    })
    return {"horas_git": horas_git, "horas_base": horas_base, "horas_total": horas_git + horas_base,
            "taxa_hora": taxa, "custo_direto": custos["custo_direto"], "custo_indireto": custos["custo_indireto"],
            "total": custos["custo_total"], "detalhe": custos}


def implantacao(dados: dict, cenario: str) -> list[dict]:
    """Itens de implantação: horas x taxa (parâmetro) ou valor fixo."""
    params = dados["parametros"]
    itens = []
    for it in dados.get("implantacao", []):
        if "valor" in it:
            valor = float(it["valor"])
            horas = None
        else:
            horas = avaliar_qtd(it["horas"], params, cenario, "custo")
            valor = horas * valor_param(params, it["taxa"], cenario, "custo")
        itens.append({"descricao": it["descricao"], "horas": horas, "valor": valor, "taxa": it.get("taxa")})
    return itens


def modelo(dados: dict, esforco: dict, cenario: str) -> dict:
    """Monta componentes, fluxos das leituras A e B e indicadores para um cenário."""
    p = dados["parametros"]
    n = int(dados["premissas"]["horizonte_anos"])
    rampa = dados.get("rampa_adocao", [1.0] * n)
    ben = componentes(dados["beneficios"], p, cenario, "beneficio")
    opx = componentes(dados["opex"], p, cenario, "custo")
    impl = implantacao(dados, cenario)
    dev = custo_desenvolvimento(dados, esforco, cenario)
    ben_t = [sum(b["anual"] for b in ben) * rampa[t] for t in range(n)]
    opx_t = [sum(o["anual"] for o in opx)] * n
    inv_a = sum(i["valor"] for i in impl)
    inv_b = inv_a + dev["total"]
    liq = [b - c for b, c in zip(ben_t, opx_t)]
    return {"cenario": cenario, "beneficios": ben, "opex": opx, "implantacao": impl, "desenvolvimento": dev,
            "beneficios_t": ben_t, "opex_t": opx_t, "investimento_a": inv_a, "investimento_b": inv_b,
            "fluxo_a": [-inv_a] + liq, "fluxo_b": [-inv_b] + liq, "rampa": rampa}


def horas_equilibrio(dados: dict, mod: dict, tma: float, leitura: str) -> float | None:
    """Horas economizadas por usuário/mês que zeram o VPL (o VPL é linear nesse parâmetro)."""
    p = dados["parametros"]
    if "horas_economizadas_usuario_mes" not in p:
        return None
    h0 = valor_param(p, "horas_economizadas_usuario_mes", "base", "beneficio")
    por_hora = valor_param(p, "usuarios", "base", "beneficio") * valor_param(p, "custo_hora_equipe", "base", "beneficio") * 12
    derivada = sum(por_hora * mod["rampa"][t] / (1 + tma) ** (t + 1) for t in range(len(mod["rampa"])))
    v = vpl(tma, mod["fluxo_" + leitura])
    return h0 - v / derivada


# ------------------------------------------------------------------ GVA
def gva(dados: dict, esforco: dict) -> dict | None:
    """GVA ágil reconstruído: VA por pontos entregues, CR pelas horas estimadas do git."""
    g = dados.get("gva")
    if not g:
        return None
    taxa = valor_param(dados["parametros"], "taxa_hora_dev", "base", "custo")
    horas_mes = {m["mes"]: m["horas_provavel"] for m in esforco["meses"]}
    total_pts = sum(pk["pontos"] for pk in g["pacotes"])
    periodos = []
    for mes in g["meses"]:
        pts = sum(pk["pontos"] for pk in g["pacotes"] if pk.get("mes_concluido") == mes)
        periodos.append({"nome": g.get("rotulos", {}).get(mes, mes), "pontos_concluidos": pts,
                         "ac": horas_mes.get(mes, 0.0) * taxa})
    r = calc_gva.calcular({"bac": g["bac_horas"] * taxa, "pontos_totais": total_pts,
                           "sprints_planejadas": g["sprints_planejadas"], "periodos": periodos,
                           "duracao_planejada": g.get("duracao_planejada_meses", g["sprints_planejadas"])})
    r["pontos_totais"] = total_pts
    r["taxa_hora"] = taxa
    r["pacotes"] = g["pacotes"]
    r["bac_horas"] = g["bac_horas"]
    r["bac_nota"] = g.get("bac_nota", "")
    return r


# ------------------------------------------------------------------ modelo de negócio
def negocio(dados: dict, base: dict, tma_real: float) -> dict | None:
    """Três opções: uso interno, SaaS multi-laboratório e implantação com suporte."""
    mn = dados.get("modelo_negocio")
    if not mn:
        return None
    p = dados["parametros"]
    n = int(dados["premissas"]["horizonte_anos"])
    taxa = valor_param(p, "taxa_hora_dev", "base", "custo")
    tma_neg = (1 + tma_real) * (1 + dados["premissas"].get("premio_risco_negocio", 0.0)) - 1
    tma_neg_m = anual_para_mensal(tma_neg)
    trib = mn.get("tributos_simples_aliquota_efetiva", 0.0)
    valor_lab_ano = sum(b["anual"] for b in base["beneficios"])
    opcoes = {}

    # Opção 1: uso interno (perspectiva da instituição, leitura A).
    opcoes["Uso interno institucional"] = {"fluxos": base["fluxo_a"], "taxa": tma_real,
                                           "descricao": "Economia de horas e riscos evitados no próprio laboratório (leitura A)."}

    # Opção 2: SaaS.
    s = mn["saas"]
    cv = s["custo_variavel_mensal_cliente"]["infra"] + s["custo_variavel_mensal_cliente"]["horas_suporte"] * taxa
    fixo = s["custos_fixos_anuais"]["infra"] + s["custos_fixos_anuais"]["horas_manutencao_mes"] * 12 * taxa
    ref_clientes = s.get("clientes_referencia_rateio", 8)
    preco_custo = ccp.calcular({"equipe": [], "indiretos": [
        {"descricao": "Custo variável por cliente-mês", "valor": cv, "rateio": 1.0},
        {"descricao": f"Custo fixo mensal rateado por {ref_clientes} clientes", "valor": fixo / 12, "rateio": 1 / ref_clientes}],
        "margem_sobre_preco": s["margem_desejada"], "tributos_sobre_preco": trib,
        "valor_percebido": valor_lab_ano / 12})
    preco_valor = valor_lab_ano / 12 * s["captura_valor"]
    preco = s["preco_mensal"]
    margem_bruta = (preco - cv - preco * trib) / preco
    metricas = mp.calcular({"arpa_mensal": preco, "margem_bruta": margem_bruta, "churn_mensal": s["churn_mensal"],
                            "cac": s["cac"], "taxa_mensal": tma_neg_m, "novos_por_ano": s["novos_por_ano"]})
    capex = s["capex_horas"] * taxa + s.get("capex_outros", 0.0)
    fluxo_saas, linhas_saas = [-capex], []
    for ano, proj in enumerate(metricas["projecao"], start=1):
        receita = proj["receita"]
        cliente_meses = receita / preco
        tributos = receita * trib
        variavel = cliente_meses * cv
        aquisicao = proj["novos"] * s["cac"]
        liquido = receita - tributos - variavel - fixo - aquisicao
        fluxo_saas.append(liquido)
        linhas_saas.append({"ano": ano, "receita": receita, "tributos": tributos, "variavel": variavel, "fixo": fixo,
                            "aquisicao": aquisicao, "liquido": liquido, "ativos_fim": proj["ativos_fim"]})
    opcoes["SaaS multi-laboratório"] = {"fluxos": fluxo_saas, "taxa": tma_neg, "descricao": s["capex_descricao"]}

    # Opção 3: implantação + suporte (uma instância por laboratório, sem multi-tenancy).
    im = mn["implantacao_suporte"]
    fixo_im = im["custos_fixos_anuais"]["horas_manutencao_mes"] * 12 * taxa
    proj_im = mp.projetar_assinaturas(im["novos_por_ano"], im["churn_mensal"], im["mensalidade_suporte"])
    capex_im = im["capex_horas"] * taxa + im.get("capex_outros", 0.0)
    fluxo_im, linhas_im = [-capex_im], []
    for ano, proj in enumerate(proj_im, start=1):
        rec_supp = proj["receita"]
        rec_impl = proj["novos"] * im["taxa_implantacao"]
        receita = rec_supp + rec_impl
        custo_supp = rec_supp / im["mensalidade_suporte"] * im["horas_suporte_mes_cliente"] * taxa
        custo_impl = proj["novos"] * im["horas_implantacao"] * taxa
        aquisicao = proj["novos"] * im["cac"]
        tributos = receita * trib
        liquido = receita - tributos - custo_supp - custo_impl - fixo_im - aquisicao
        fluxo_im.append(liquido)
        linhas_im.append({"ano": ano, "receita": receita, "tributos": tributos, "variavel": custo_supp + custo_impl,
                          "fixo": fixo_im, "aquisicao": aquisicao, "liquido": liquido, "ativos_fim": proj["ativos_fim"]})
    opcoes["Implantação e suporte (instância por laboratório)"] = {"fluxos": fluxo_im, "taxa": tma_neg,
                                                                    "descricao": im["capex_descricao"]}
    metricas_im = mp.calcular({"arpa_mensal": im["mensalidade_suporte"],
                               "margem_bruta": (im["mensalidade_suporte"] * (1 - trib) - im["horas_suporte_mes_cliente"] * taxa) / im["mensalidade_suporte"],
                               "churn_mensal": im["churn_mensal"], "cac": im["cac"], "taxa_mensal": tma_neg_m})

    for nome, o in opcoes.items():
        o["analise"] = analisar(o["taxa"], o["fluxos"])
    # Matriz de decisão: nota de VPL normalizada de 0 a 10 entre as opções.
    vpls = {k: o["analise"]["vpl"] for k, o in opcoes.items()}
    lo, hi = min(vpls.values()), max(vpls.values())
    notas = {k: dict(v) for k, v in mn["notas"].items()}
    for k in notas:
        notas[k]["VPL"] = 10.0 if hi == lo else 10.0 * (vpls[k] - lo) / (hi - lo)
    matriz = calt.matriz_decisao(mn["criterios"], notas)

    # Tributos no ano 5 da opção SaaS: Simples x Presumido x Real (escudo fiscal da amortização do CapEx).
    ano5 = linhas_saas[-1]
    custos_ano5 = ano5["variavel"] + ano5["fixo"] + ano5["aquisicao"]
    amortizacao = capex * 0.20 if n >= 5 else 0.0
    regimes = cdt.calcular({"ativos": [], "tributos": {
        "receita": ano5["receita"], "custos": custos_ano5, "depreciacao": amortizacao,
        "aliquota_ir_csll": mn.get("aliquota_ir_csll_lucro_real", 0.34),
        "simples_aliquota_efetiva": trib, "presumido": mn["presumido"]}})
    return {"tma_negocio": tma_neg, "tma_negocio_mensal": tma_neg_m, "valor_percebido_lab_ano": valor_lab_ano,
            "saas": {"custo_variavel_cliente_mes": cv, "custo_fixo_ano": fixo, "precificacao_custo": preco_custo,
                     "preco_valor": preco_valor, "preco_adotado": preco, "margem_bruta": margem_bruta,
                     "metricas": metricas, "linhas": linhas_saas, "capex": capex},
            "implantacao_suporte": {"linhas": linhas_im, "capex": capex_im, "metricas": metricas_im},
            "opcoes": opcoes, "matriz": matriz, "regimes_ano5_saas": regimes, "amortizacao_capex": amortizacao,
            "notas": {"licenca": mn.get("nota_licenca", ""), "multitenancy": mn.get("nota_multitenancy", "")}}


# ------------------------------------------------------------------ cálculo completo
def calcular(dados: dict, base_dir: str = "") -> dict:
    """Executa todos os módulos e devolve um dicionário com todos os resultados."""
    pr = dados["premissas"]
    t = pr["tma"]
    tma = compor_tma(t["taxa_base"], t.get("premios"), t.get("inflacao"))
    tma_real = tma["tma_real"]
    n = int(pr["horizonte_anos"])
    esforco = eeg.calcular({**dados["esforco"], "_base_dir": base_dir})
    modelos = {c: modelo(dados, esforco, c) for c in CENARIOS}
    base = modelos["base"]
    analises = {c: {"A": analisar(tma_real, m["fluxo_a"]), "B": analisar(tma_real, m["fluxo_b"])}
                for c, m in modelos.items()}
    # Sensibilidade (tornado ±20%) nas duas leituras.
    sensib = {}
    for leitura, inv in (("A", base["investimento_a"]), ("B", base["investimento_b"])):
        sensib[leitura] = sens.calcular({"taxa": tma_real, "investimento": inv, "beneficios": base["beneficios_t"],
                                         "custos": base["opex_t"], "variacao": 0.20})
    # VPL ao longo da faixa de TMA nominal informada.
    faixa = []
    for nominal in t.get("faixa_nominal", []):
        real = (1 + nominal) / (1 + t["inflacao"]) - 1
        faixa.append({"tma_nominal": nominal, "tma_real": real, "vpl_a": vpl(real, base["fluxo_a"]),
                      "vpl_b": vpl(real, base["fluxo_b"])})
    equilibrio = {"A": horas_equilibrio(dados, base, tma_real, "a"), "B": horas_equilibrio(dados, base, tma_real, "b")}

    # Depreciação dos ativos de TI.
    depreciacao = cdt.calcular({"ativos": dados.get("ativos_ti", [])})

    # Alternativas de infraestrutura (lives diferentes => CAUE).
    infra = None
    if "alternativas_infra" in dados:
        ai = dados["alternativas_infra"]
        alts = [{"nome": o["nome"], "fluxos": [-o["investimento"]] + [-o["anual"]] * o["vida"], "vida": o["vida"]}
                for o in ai["opcoes"]]
        infra = calt.calcular({"tma": tma_real, "alternativas": alts, "criterios": ai["criterios"], "notas": ai["notas"]})
        infra["notas_opcoes"] = {o["nome"]: o.get("nota", "") for o in ai["opcoes"]}

    # Construir (já construído) x comprar LIMS: só custos, benefícios supostos iguais.
    cvc = None
    if "construir_vs_comprar" in dados:
        cv = dados["construir_vs_comprar"]
        # Horas da equipe usuária (treinamento e carga inicial) ocorrem em qualquer das duas opções.
        staff = sum(i["valor"] for i in base["implantacao"] if i.get("taxa") == cv.get("parametro_equipe", "custo_hora_equipe"))
        proprio = [-base["investimento_a"]] + [-c for c in base["opex_t"]]
        lims = [-(cv["lims_implantacao"] + staff)] + [-cv["lims_assinatura_mensal"] * 12] * n
        cvc = calt.calcular({"tma": tma_real, "alternativas": [
            {"nome": "Sistema próprio (implantar e manter)", "fluxos": proprio},
            {"nome": "LIMS de mercado (licenciar)", "fluxos": lims}]})
        cvc["descricao"] = cv["descricao"]
        cvc["nota"] = cv.get("nota", "")

    # Manter, refatorar ou aposentar componentes.
    aposentadoria = []
    for comp in dados.get("aposentadoria", []):
        alts = [{"nome": o["nome"], "fluxos": [-o["investimento"]] + [o["anual"]] * n} for o in comp["opcoes"]]
        r = calt.calcular({"tma": tma_real, "alternativas": alts})
        r["componente"] = comp["componente"]
        r["notas_opcoes"] = {o["nome"]: o.get("nota", "") for o in comp["opcoes"]}
        aposentadoria.append(r)

    # Backlog: substitui referências ao modelo e prioriza.
    backlog = None
    if "backlog" in dados:
        b = json.loads(json.dumps(dados["backlog"]))
        liquido_ano2 = base["beneficios_t"][1] - base["opex_t"][1] if n > 1 else 0.0
        for it in b["itens"]:
            if it.get("valor_anual") == "$beneficio_liquido_ano2":
                it["valor_anual"] = liquido_ano2
        b["taxa_hora"] = valor_param(dados["parametros"], "taxa_hora_dev", "base", "custo")
        b["tma"] = tma_real
        b["horizonte_anos"] = n
        backlog = pb.priorizar(b)
        if "niveis_qualidade_testes_interface" in b:
            backlog["bom_o_suficiente"] = pb.bom_o_suficiente(b["niveis_qualidade_testes_interface"])
            backlog["niveis"] = b["niveis_qualidade_testes_interface"]

    resultado = {
        "meta": dados["meta"], "tma": tma, "tma_real": tma_real, "horizonte_anos": n, "esforco": esforco,
        "modelos": modelos, "analises": analises, "sensibilidade": sensib, "faixa_tma": faixa,
        "equilibrio_horas_usuario_mes": equilibrio, "depreciacao": depreciacao, "infra": infra,
        "construir_vs_comprar": cvc, "aposentadoria": aposentadoria, "backlog": backlog,
        "gva": gva(dados, esforco),
    }
    resultado["negocio"] = negocio(dados, base, tma_real)
    return resultado


# ------------------------------------------------------------------ Markdown
def _tir_curta(a: dict) -> str:
    return descrever_tir(a["tir"]) if a["tir"]["status"] != "sem_raiz" else "inexistente (sem troca de sinal)"


def _pb(a: dict, chave: str) -> str:
    return anos_meses(a[chave]["anos"])


def resumo_template(r: dict, dados: dict) -> str:
    """Preenche assets/proposta_executiva_template.md com os resultados."""
    with open(TEMPLATE, "r", encoding="utf-8") as arq:
        texto = arq.read()
    a, b = r["analises"]["base"]["A"], r["analises"]["base"]["B"]
    base = r["modelos"]["base"]
    g = r.get("gva")
    neg = r.get("negocio")
    eq = r["equilibrio_horas_usuario_mes"]
    tem_h = "horas_economizadas_usuario_mes" in dados["parametros"]
    h0 = valor_param(dados["parametros"], "horas_economizadas_usuario_mes", "base", "beneficio") if tem_h else None
    inicio = (f"implantar o sistema em produção (Leitura A com VPL de {brl(a['vpl'])} e payback descontado de "
              f"{_pb(a, 'payback_descontado')})." if a["vpl"] > 0 else
              f"não implantar nas condições atuais (Leitura A com VPL de {brl(a['vpl'])}); revise custos ou escopo.")
    recomendacao = (
        inicio + " Como investimento total (Leitura B), o uso interno isolado "
        + ("se paga no horizonte" if b["vpl"] > 0 else "não recupera o custo econômico do desenvolvimento em "
           f"{r['horizonte_anos']} anos") + f" (VPL {brl(b['vpl'])}); a recuperação depende de ampliar o uso "
        "ou de um modelo de negócio externo (seção VI).")
    just = (f"O benefício anual em regime é de {brl(base['beneficios_t'][-1])} contra OpEx de {brl(base['opex_t'][-1])}, "
            f"um ganho líquido de {brl(base['beneficios_t'][-1] - base['opex_t'][-1])} por ano. Sobre o investimento de implantação "
            f"de {brl(base['investimento_a'])}, o ROI descontado em {r['horizonte_anos']} anos é {pct(a['roi_descontado'])}."
            + (f" Para a Leitura B zerar o VPL seriam necessárias {num(eq['B'], 1)} h economizadas por usuário/mês "
               f"(hipótese base: {num(h0, 1)} h); para a Leitura A bastam {num(eq['A'], 1)} h." if tem_h else ""))
    resumo_gva = "não informado"
    if g:
        f = g["final"]
        resumo_gva = (f"Na última data de status ({f['nome']}), IDC (CPI) = {num(f['cpi'], 3)} e IDP (SPI) = {num(f['spi'], 3)}: "
                      f"{f['leitura']} EAC (BAC/IDC) = {brl(f['eac_cpi'])} para um BAC reconstruído de {brl(f['bac'])}.")
    resumo_neg = "não avaliado"
    if neg:
        ops = neg["opcoes"]
        resumo_neg = ("; ".join(f"{k}: VPL {brl(o['analise']['vpl'])}" for k, o in ops.items())
                      + f". Vencedora na matriz ponderada: {neg['matriz']['vencedora']}.")
    hip = ("custo da hora da equipe do laboratório, horas economizadas por usuário, número de usuários, horas de "
           "manutenção, taxa horária de desenvolvimento e TMA. Todas aparecem com faixa e forma de validação.")
    proximos = ("(1) confirmar a TMA vigente e a taxa horária com a instituição; (2) colocar em produção e medir horas "
                "economizadas por 3 meses; (3) executar os itens 'fazer neste ciclo' do backlog; (4) só avaliar a oferta "
                "externa depois de formalizar o acordo de licença.")
    trocas = {
        "sistema": dados["meta"]["sistema"], "descricao": dados["meta"]["descricao"], "situacao": dados["meta"]["situacao"],
        "recomendacao": recomendacao, "tma_real": pct(r["tma_real"]),
        "inv_a": brl(base["investimento_a"]), "inv_b": brl(base["investimento_b"]),
        "vpl_a": brl(a["vpl"]), "vpl_b": brl(b["vpl"]), "tir_a": _tir_curta(a), "tir_b": _tir_curta(b),
        "tirm_a": pct(a["tirm"]), "tirm_b": pct(b["tirm"]),
        "pb_a": _pb(a, "payback_simples"), "pb_b": _pb(b, "payback_simples"),
        "pbd_a": _pb(a, "payback_descontado"), "pbd_b": _pb(b, "payback_descontado"),
        "il_a": num(a["indice_lucratividade"], 2), "il_b": num(b["indice_lucratividade"], 2),
        "vpl_a_pess": brl(r["analises"]["pessimista"]["A"]["vpl"]), "vpl_a_otim": brl(r["analises"]["otimista"]["A"]["vpl"]),
        "vpl_b_pess": brl(r["analises"]["pessimista"]["B"]["vpl"]), "vpl_b_otim": brl(r["analises"]["otimista"]["B"]["vpl"]),
        "justificativa_roi": just, "resumo_gva": resumo_gva, "resumo_negocio": resumo_neg,
        "hipoteses_chave": hip, "proximos_passos": proximos,
    }
    for chave, valor in trocas.items():
        texto = texto.replace("{{" + chave + "}}", valor)
    return texto.strip()


def tabela_fluxo(m: dict, a: dict, leitura: str) -> str:
    """Tabela do fluxo de caixa anual com VP e acumulados."""
    n = len(m["beneficios_t"])
    inv = m["investimento_" + leitura.lower()]
    cab = ["Linha"] + [f"Ano {t}" for t in range(n + 1)]
    linhas = []
    for comp in m["beneficios"]:
        linhas.append([f"(+) {comp['nome']}", brl(0)] + [brl(comp["anual"] * m["rampa"][t]) for t in range(n)])
    for comp in m["opex"]:
        linhas.append([f"(-) {comp['nome']}", brl(0)] + [brl(-comp["anual"]) for _ in range(n)])
    linhas.append(["(-) Investimento (CapEx e implantação" + (" + desenvolvimento" if leitura == "B" else "") + ")",
                   brl(-inv)] + [brl(0)] * n)
    linhas.append(["**Fluxo líquido**"] + [f"**{brl(f)}**" for f in a["fluxos"]])
    linhas.append(["Acumulado simples"] + [brl(x) for x in a["payback_simples"]["acumulado"]])
    linhas.append(["VP do fluxo"] + [brl(x) for x in a["vp_fluxos"]])
    linhas.append(["Acumulado descontado"] + [brl(x) for x in a["payback_descontado"]["acumulado"]])
    return tabela_md(cab, linhas)


def renderizar_md(r: dict, dados: dict) -> str:
    """Relatório Markdown completo."""
    meta = r["meta"]
    base = r["modelos"]["base"]
    an = r["analises"]
    A, B = an["base"]["A"], an["base"]["B"]
    tma = r["tma"]
    p = dados["parametros"]
    L: list[str] = []
    L.append(f"# {meta['titulo']}\n")
    L.append(f"**Autores:** {' e '.join(meta['autores'])}  ")
    L.append(f"**Curso:** {meta['curso']}  ")
    L.append(f"**Componente curricular:** {meta['componente']}. **Docente:** {meta['docente']}  ")
    L.append(f"**Data-base:** {meta['data_base']}. **Moeda:** {meta['moeda']}.  ")
    L.append("**Gerado por:** skill `engenharia-economica-software` (`scripts/gerar_relatorio.py`), a partir de "
             f"`{dados.get('_arquivo_entrada', 'entrada JSON')}`. Os números são reproduzíveis executando o mesmo comando.\n")
    L.append(resumo_template(r, dados) + "\n")

    # Contexto
    L.append("## 1. Contexto e fatos medidos\n")
    L.append(meta["descricao"] + " " + meta["situacao"] + "\n")
    L.append(tabela_md(["Fato", "Valor (medido no repositório)"], [[f["item"], f["valor"]] for f in dados.get("fatos_medidos", [])]) + "\n")

    # Premissas
    L.append("## 2. Premissas e hipóteses\n")
    L.append("Cada linha diz de onde o número vem. **Origem** usa quatro rótulos: *medido no git* (fato verificável), "
             "*estimado* (derivado por heurística documentada), *hipótese de mercado* (valor típico a cotar) e "
             "*hipótese do grupo* (julgamento dos autores). Nenhuma hipótese foi apresentada como medição.\n")
    linhas = [
        ["Taxa de referência (base da TMA)", pct(tma["taxa_base"]), "", "", "hipótese do grupo",
         "Substituir pela taxa vigente (por exemplo, Selic ou custo de capital da instituição) informada pelo usuário"],
        ["Prêmios de risco", ", ".join(f"{k}: {pct(v)}" for k, v in tma["premios"].items()), "", "", "hipótese do grupo",
         "Discutir com a gestão o risco aceito para projetos internos"],
        ["Inflação anual esperada", pct(tma["inflacao"]), "", "", "hipótese de mercado", "Usar a expectativa de mercado vigente (boletim Focus)"],
        ["TMA nominal composta", pct(tma["tma_nominal"]), pct(dados["premissas"]["tma"]["faixa_nominal"][0]),
         pct(dados["premissas"]["tma"]["faixa_nominal"][1]), "estimado", "(1 + base) x (1 + prêmio) - 1"],
        ["TMA real (Fisher), usada no desconto", pct(r["tma_real"]), "", "", "estimado", "(1 + nominal) / (1 + inflação) - 1"],
        ["Horizonte", f"{r['horizonte_anos']} anos", "", "", "hipótese do grupo", "Vida útil esperada antes de reescrita relevante"],
        ["Rampa de adoção", ", ".join(pct(x, 0) for x in base["rampa"]), "", "", "hipótese do grupo", "Medir uso real no 1º ano"],
        ["Tributos no uso interno", pct(dados["premissas"].get("tributos_uso_interno", 0.0)), "", "", "hipótese do grupo",
         "Uso institucional sem receita tributável; validar o enquadramento da instituição com a contabilidade"],
    ]
    for nome, spec in p.items():
        if isinstance(spec, dict):
            fmt = (lambda v: pct(v)) if spec.get("unidade", "").startswith(("fração", "probabilidade")) else (lambda v: num(v, 2))
            linhas.append([f"{spec.get('descricao', nome)} ({spec.get('unidade', '')})", fmt(spec["provavel"]),
                           fmt(spec["min"]), fmt(spec["max"]), spec.get("origem", ""), spec.get("como_validar", "")])
    e = r["esforco"]
    linhas.append(["Esforço registrado no git (h)", num(e["totais"]["provavel"], 0), num(e["totais"]["min"], 0),
                   num(e["totais"]["max"], 0), "estimado (medido no git + heurística)", "Comparar com registros das sprints, se existirem"])
    if e.get("base_importada"):
        bi = e["base_importada"]
        linhas.append(["Esforço da base importada (h)", num(bi["horas_provavel"], 0), num(bi["horas_min"], 0),
                       num(bi["horas_max"], 0), "estimado",
                       dados["esforco"]["base_importada"].get("como_validar", "Confrontar com o cronograma do período anterior ao repositório")])
    L.append(tabela_md(["Premissa", "Base (provável)", "Mínimo", "Máximo", "Origem", "Como validar"], linhas) + "\n")
    L.append(f"Derivação da taxa horária: {p['taxa_hora_dev'].get('derivacao', '')}.\n")
    L.append(f"Composição da TMA: TMA nominal = (1 + {pct(tma['taxa_base'])}) x (1 + {pct(sum(tma['premios'].values()))}) - 1 = "
             f"{pct(tma['tma_nominal'])}; TMA real = (1 + {pct(tma['tma_nominal'])}) / (1 + {pct(tma['inflacao'])}) - 1 = "
             f"{pct(r['tma_real'])} a.a. (equivalente a {pct(anual_para_mensal(r['tma_real']), 4)} a.m.). Como todos os fluxos "
             "estão em preços constantes, o desconto usa a taxa real (consistência de Fisher).\n")

    # Esforço e custo
    L.append("## 3. Esforço e custo de desenvolvimento\n")
    if "meses_informados" in dados["esforco"]:
        L.append("**Horas informadas pelo usuário** (apontamento ou estimativa externa), sem derivação do git.\n")
    else:
        L.append("**Estimativa derivada do histórico do repositório.** Não há apontamento de horas; o esforço foi reconstruído "
             "dos commits sem merge. " + dados["esforco"].get("nota_metodo", "") + " "
             f"Heurística: horas do mês = max(horas em sessões, dias ativos x horas por dia) x fator de trabalho sem commit; "
             "horas por dia ativo de " + "/".join(num(e['parametros']['horas_por_dia_ativo'][c], 0) for c in ("min", "provavel", "max"))
             + " (mínimo/provável/máximo), fator de trabalho sem commit de "
             + "/".join(num(e['parametros']['fator_trabalho_sem_commit'][c], 1) for c in ("min", "provavel", "max")) + ", "
             f"sessão = commits com intervalo de até {num(e['parametros']['intervalo_sessao_horas'], 0)} h + "
             f"{num(e['parametros']['preparo_sessao_horas'], 0)} h de preparo.\n")
    L.append(eeg.renderizar_md(e) + "\n")
    if e.get("base_importada"):
        bi = e["base_importada"]
        L.append(f"Base importada: {num(bi['linhas'], 0)} linhas a {bi['produtividade']['alta']}, {bi['produtividade']['provavel']} e "
                 f"{bi['produtividade']['baixa']} linhas/h resultam em {num(bi['horas_min'], 0)} h (mínimo), "
                 f"{num(bi['horas_provavel'], 0)} h (provável) e {num(bi['horas_max'], 0)} h (máximo).\n")
    linhas = []
    for c in CENARIOS:
        d = r["modelos"][c]["desenvolvimento"]
        linhas.append([c, num(d["horas_total"], 0), brl(d["taxa_hora"]), brl(d["custo_direto"]), brl(d["custo_indireto"]), brl(d["total"])])
    L.append(tabela_md(["Cenário", "Horas totais", "Taxa horária", "Custo direto", "Custo indireto (rateio)", "Custo econômico do desenvolvimento"], linhas) + "\n")
    L.append("O custo de desenvolvimento é **econômico** (custo de oportunidade das horas a preço de mercado), não um desembolso: "
             "o trabalho foi acadêmico. Por isso ele aparece só na Leitura B.\n")
    L.append("**Depreciação de ativos de TI.** A taxa fiscal usual para computadores e periféricos no Brasil é 20% a.a. "
             "(vida de 5 anos), a conferir na regra vigente com um contador (ver `references/aliquotas.md`).\n")
    L.append(cdt.renderizar_md(r["depreciacao"]) + "\n")
    L.append("**Implantação (investimento da Leitura A, cenário base):**\n")
    L.append(tabela_md(["Item", "Horas", "Valor"], [[i["descricao"], num(i["horas"], 0) if i["horas"] is not None else "",
                                                     brl(i["valor"])] for i in base["implantacao"]]
                       + [["**Total**", "", f"**{brl(base['investimento_a'])}**"]]) + "\n")

    # I Fluxo de caixa
    L.append("## I. Fluxo de Caixa\n")
    L.append("Fluxos anuais em valores reais, t = 0 na implantação, cenário base. Benefícios do ano 1 multiplicados pela rampa de adoção.\n")
    L.append("### Leitura A: valoração do ativo a partir de hoje (desenvolvimento como custo afundado)\n")
    L.append(tabela_fluxo(base, A, "A") + "\n")
    L.append("### Leitura B: viabilidade total (desenvolvimento como investimento inicial)\n")
    L.append(tabela_fluxo(base, B, "B") + "\n")

    # II VPL
    L.append("## II. VPL (Valor Presente Líquido)\n")
    L.append(f"VPL = soma de F_t / (1 + i)^t, com i = TMA real de {pct(r['tma_real'])} a.a.\n")
    linhas = []
    for c in CENARIOS:
        a_, b_ = an[c]["A"], an[c]["B"]
        linhas.append([c, brl(a_["vpl"]), a_["decisao"], brl(b_["vpl"]), b_["decisao"]])
    L.append(tabela_md(["Cenário", "VPL Leitura A", "Decisão A", "VPL Leitura B", "Decisão B"], linhas) + "\n")
    L.append("Os cenários pessimista e otimista combinam todos os extremos ao mesmo tempo (teste de estresse); a probabilidade "
             "conjunta é baixa, por isso a decisão se apoia no cenário base, na sensibilidade e no ponto de equilíbrio.\n")
    L.append(tabela_md(["TMA nominal", "TMA real", "VPL A", "VPL B"],
                       [[pct(f["tma_nominal"]), pct(f["tma_real"]), brl(f["vpl_a"]), brl(f["vpl_b"])] for f in r["faixa_tma"]]) + "\n")
    L.append(f"VPL anualizado (benefício anual uniforme equivalente) do cenário base: A = {brl(A['vpl_anualizado'])}/ano; "
             f"B = {brl(B['vpl_anualizado'])}/ano.\n")

    # III TIR
    L.append("## III. TIR (Taxa Interna de Retorno)\n")
    L.append("A TIR é obtida por varredura de -99% a 1000% e bissecção, com contagem de trocas de sinal; quando não existe "
             "ou não é única, o script informa o status em vez de um número.\n")
    linhas = []
    for c in CENARIOS:
        for leitura in ("A", "B"):
            a_ = an[c][leitura]
            linhas.append([c, leitura, a_["tir"]["status"], _tir_curta(a_), pct(a_["tirm"]), a_["tir"]["trocas_sinal"],
                           "supera a TMA" if a_["tir"]["tir"] is not None and a_["tir"]["tir"] > r["tma_real"] else
                           ("abaixo da TMA" if a_["tir"]["tir"] is not None else "decidir pelo VPL")])
    L.append(tabela_md(["Cenário", "Leitura", "Status", "TIR real", "TIRM", "Trocas de sinal", "Comparação"], linhas) + "\n")
    L.append(f"TIR nominal equivalente (Fisher) no cenário base, Leitura A: "
             f"{pct((1 + A['tir']['tir']) * (1 + tma['inflacao']) - 1) if A['tir']['tir'] is not None else 'n/d'}.\n")

    # IV Payback
    L.append("## IV. Payback\n")
    L.append("Interpolação linear dentro do ano: payback = k + |acumulado_k| / fluxo_(k+1), onde k é o último ano com saldo negativo.\n")
    linhas = []
    for c in CENARIOS:
        for leitura in ("A", "B"):
            a_ = an[c][leitura]
            linhas.append([c, leitura, _pb(a_, "payback_simples"), _pb(a_, "payback_descontado"),
                           num(a_["indice_lucratividade"], 3), pct(a_["roi_descontado"])])
    L.append(tabela_md(["Cenário", "Leitura", "Payback simples", "Payback descontado", "Índice de lucratividade", "ROI descontado"], linhas) + "\n")
    L.append("O payback descontado é sempre maior ou igual ao simples, porque cada entrada futura vale menos hoje.\n")

    # Sensibilidade
    L.append("## Sensibilidade, cenários e ponto de equilíbrio\n")
    for leitura in ("A", "B"):
        L.append(f"### Tornado da Leitura {leitura} (±20%, uma variável por vez)\n")
        L.append(sens.renderizar_md(r["sensibilidade"][leitura]) + "\n")
    L.append(tabela_md(["Cenário", "Investimento A", "Investimento B", "Benefício anual em regime", "OpEx anual"],
                       [[c, brl(r["modelos"][c]["investimento_a"]), brl(r["modelos"][c]["investimento_b"]),
                         brl(r["modelos"][c]["beneficios_t"][-1]), brl(r["modelos"][c]["opex_t"][-1])] for c in CENARIOS]) + "\n")
    eq = r["equilibrio_horas_usuario_mes"]
    if eq["A"] is not None:
        L.append(f"**Ponto de equilíbrio em horas economizadas:** mantidos os demais parâmetros do cenário base, o VPL da Leitura A "
             f"zera com {num(eq['A'], 2)} h por usuário/mês e o da Leitura B com {num(eq['B'], 2)} h por usuário/mês "
             f"(hipótese base: {num(valor_param(p, 'horas_economizadas_usuario_mes', 'base', 'beneficio'), 1)} h).\n")

    # V GVA
    g = r.get("gva")
    if g:
        L.append("## V. Métricas de eficiência ágil via GVA (EVM)\n")
        L.append("**Reconstrução retrospectiva, sem medição contemporânea.** " + dados["gva"].get("nota_registro", "") + " O plano de referência "
                 f"(VP) foi reconstruído: {g['bac_nota']} BAC = {num(g['bac_horas'], 0)} h x {brl(g['taxa_hora'])} = {brl(g['bac'])}, "
                 f"distribuído uniformemente em {dados['gva']['sprints_planejadas']} períodos. O VA usa pontos "
                 f"de história atribuídos retrospectivamente aos pacotes entregues ({g['pontos_totais']} pontos no total), com o mês de "
                 "conclusão tirado do git. O CR usa as horas prováveis da seção 3 x taxa horária base.\n")
        L.append(tabela_md(["Pacote", "Pontos", "Concluído em"],
                           [[f"{pk['id']}: {pk['nome']}", pk["pontos"], pk["mes_concluido"] or "pendente"] for pk in g["pacotes"]]) + "\n")
        L.append(calc_gva.renderizar_md(g) + "\n")
        L.append("Leitura por período: " + " ".join(f"{pp['nome']}: {pp['leitura']}" for pp in g["periodos"]) + "\n")

    # VI Modelo de negócio
    neg = r.get("negocio")
    if neg:
        L.append("## VI. Proposta de modelo de negócio\n")
        L.append(f"{neg['notas']['licenca']} {neg['notas']['multitenancy']}\n")
        L.append(f"As opções externas são avaliadas à TMA real de negócio de {pct(neg['tma_negocio'])} a.a. (TMA real + prêmio de risco de "
                 f"novo negócio), equivalente a {pct(neg['tma_negocio_mensal'], 3)} a.m. O uso interno usa a TMA institucional.\n")
        s = neg["saas"]
        pc = s["precificacao_custo"]
        L.append("### Precificação: markup sobre custo x valor percebido (opção SaaS)\n")
        L.append(tabela_md(["Referência de preço mensal por laboratório", "Valor"], [
            ["Custo variável por cliente (infra + suporte)", brl(s["custo_variavel_cliente_mes"])],
            ["Custo total por cliente com rateio do fixo", brl(pc["custo_total"])],
            ["Preço mínimo (cobre custo e tributos)", brl(pc["precos"]["preco_minimo"])],
            [f"Preço por markup divisor (tributos {pct(pc['tributos'])} + margem {pct(pc['margem'])})", brl(pc["precos"]["markup_divisor_com_tributos"])],
            ["Valor percebido (benefício base de um laboratório / 12)", brl(neg["valor_percebido_lab_ano"] / 12)],
            ["Preço por captura de valor", brl(s["preco_valor"])],
            ["**Preço adotado na projeção**", f"**{brl(s['preco_adotado'])}**"],
            ["Margem bruta por cliente após tributos", pct(s["margem_bruta"])],
        ]) + "\n")
        L.append("### Métricas de produto digital\n")
        L.append("SaaS multi-laboratório:\n")
        L.append(mp.renderizar_md(s["metricas"]) + "\n")
        L.append("Implantação e suporte (contrato de suporte como recorrência):\n")
        L.append(mp.renderizar_md(neg["implantacao_suporte"]["metricas"]) + "\n")
        for nome, chave in (("SaaS multi-laboratório", "saas"), ("Implantação e suporte (instância por laboratório)", "implantacao_suporte")):
            linhas_n = neg[chave]["linhas"]
            L.append(f"### Fluxo da opção {nome}\n")
            L.append(f"CapEx inicial: {brl(neg[chave]['capex'])} ({neg['opcoes'][nome]['descricao']}).\n")
            L.append(tabela_md(["Ano", "Receita", "Tributos", "Custos variáveis", "Custos fixos", "Aquisição (CAC)", "Fluxo líquido", "Clientes no fim"],
                               [[x["ano"], brl(x["receita"]), brl(-x["tributos"]), brl(-x["variavel"]), brl(-x["fixo"]),
                                 brl(-x["aquisicao"]), brl(x["liquido"]), num(x["ativos_fim"], 2)] for x in linhas_n]) + "\n")
        L.append("### Comparação das opções\n")
        L.append(tabela_md(["Opção", "Taxa", "VPL", "TIR", "Payback descontado", "IL"],
                           [[k, pct(o["taxa"]), brl(o["analise"]["vpl"]), _tir_curta(o["analise"]),
                             _pb(o["analise"], "payback_descontado"), num(o["analise"]["indice_lucratividade"], 2)]
                            for k, o in neg["opcoes"].items()]) + "\n")
        m = neg["matriz"]
        nomes = [c["nome"] for c in m["criterios"]]
        L.append(tabela_md(["Opção"] + [f"{c['nome']} (peso {num(c['peso'], 2)})" for c in m["criterios"]] + ["Pontuação"],
                           [[k] + [num(m["notas"][k][n_], 1) for n_ in nomes] + [num(m["pontuacoes"][k], 2)] for k in m["notas"]]) + "\n")
        L.append(f"Nota de VPL normalizada de 0 a 10 entre as opções; demais notas são julgamento do grupo. **Recomendação:** "
                 f"{m['vencedora']}.\n")
        rg = neg["regimes_ano5_saas"]
        L.append("### Tributos e escudo fiscal (opção SaaS, ano 5, parâmetros a validar)\n")
        L.append(f"Amortização anual do CapEx a 20% a.a.: {brl(neg['amortizacao_capex'])}. No Simples Nacional e no Lucro Presumido a base é a "
                 "receita, então não há escudo fiscal; no Lucro Real o escudo é t x D.\n")
        L.append(cdt.renderizar_md(rg) + "\n")

    # Decisões de engenharia
    L.append("## Decisões de engenharia como decisões econômicas\n")
    if r.get("infra"):
        L.append("### Infraestrutura: on-premises x nuvem\n")
        L.append(dados["alternativas_infra"]["descricao"] + " Vidas diferentes, logo a comparação usa o VPL anualizado (CAUE).\n")
        L.append(calt.renderizar_md(r["infra"]) + "\n")
        L.append(tabela_md(["Opção", "Premissas"], [[k, v] for k, v in r["infra"]["notas_opcoes"].items()]) + "\n")
    if r.get("construir_vs_comprar"):
        cv = r["construir_vs_comprar"]
        L.append("### Construir x comprar: sistema próprio x LIMS de mercado\n")
        L.append(cv["descricao"] + " " + cv["nota"] + "\n")
        L.append(calt.renderizar_md(cv) + "\n")
    if r.get("aposentadoria"):
        L.append("### Manter, refatorar ou aposentar componentes\n")
        for comp in r["aposentadoria"]:
            L.append(f"**{comp['componente']}**\n")
            L.append(calt.renderizar_md(comp) + "\n")
            L.append(tabela_md(["Opção", "Premissa"], [[k, v] for k, v in comp["notas_opcoes"].items()]) + "\n")

    # Backlog
    bk = r.get("backlog")
    if bk:
        L.append("## Priorização do backlog (Valor x Esforço) e princípio bom o suficiente\n")
        L.append(f"Valor de 1 a 10 e horas estimadas pelo grupo; custo a {brl(dados['parametros']['taxa_hora_dev']['provavel'])}/h; "
                 f"VPL do item = valor anual x {num(bk['fator_serie'], 4)} (fator de série a {pct(r['tma_real'])} em "
                 f"{r['horizonte_anos']} anos) - custo. Capacidade do próximo ciclo: {num(bk['capacidade_horas'], 0)} h.\n")
        L.append(pb.renderizar_md(bk) + "\n")
        L.append(tabela_md(["Id", "Justificativa"], [[i["id"], i.get("justificativa", "")] for i in sorted(bk["itens"], key=lambda x: x["id"])]) + "\n")
        if "bom_o_suficiente" in bk:
            bs = bk["bom_o_suficiente"]
            L.append("**Bom o suficiente em testes de interface:** benefício e custo acumulados (VP, R$) por nível de cobertura.\n")
            L.append(tabela_md(["Nível", "Custo acumulado", "Benefício acumulado"],
                               [[n_["nome"], brl(n_["custo"]), brl(n_["beneficio"])] for n_ in bk["niveis"]]) + "\n")
            L.append(tabela_md(["Passo para", "Custo marginal", "Benefício marginal"],
                               [[m_["nivel"], brl(m_["custo_marginal"]), brl(m_["beneficio_marginal"])] for m_ in bs["marginais"]]) + "\n")
            L.append(f"Nível escolhido: **{bs['nivel_escolhido']}**. Depois dele, cada real adicional compra menos de um real de benefício.\n")
        nao = [i for i in bk["itens"] if not i["decisao"].startswith("fazer")]
        L.append("**O que não fazer agora:** " + "; ".join(f"{i['id']} ({i['titulo']}): {i['decisao']}" for i in nao) + ".\n")

    # Riscos
    L.append("## Riscos e hipóteses (transparência)\n")
    L.append(tabela_md(["Risco", "Probabilidade", "Impacto", "Variável do modelo", "Mitigação"],
                       [[x["risco"], x["probabilidade"], x["impacto"], x["variavel"], x["mitigacao"]] for x in dados.get("riscos", [])]) + "\n")

    # Limitações
    L.append("## Limitações\n")
    L.append("- O sistema ainda não está em produção: nenhum benefício foi medido; todos são hipóteses com faixa.\n"
             "- O esforço é estimativa derivada do histórico do repositório; commits agrupados e trabalho sem commit tornam a faixa larga.\n"
             "- O plano de referência do GVA foi reconstruído depois do fato; IDC e IDP servem para aprendizado, não para auditoria.\n"
             "- Preços de infraestrutura, de LIMS e alíquotas são parâmetros configuráveis, não cotações oficiais.\n"
             "- Valores reais (sem inflação) e sem valor residual no fim do horizonte, o que é conservador.\n"
             "- O modelo de negócio externo depende de acordo de licença com a instituição e, no caso SaaS, de multi-tenancy.\n")
    L.append("Fórmulas: `references/formulas.md`. Alíquotas e parâmetros a validar: `references/aliquotas.md`.\n")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    """CLI: --entrada, --saida-md, --saida-json."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                     epilog="Modelo de entrada: assets/modelo_entrada.json")
    parser.add_argument("--entrada", "-e", required=True, help="JSON do projeto")
    parser.add_argument("--saida-md", default=None, help="arquivo Markdown do relatório (padrão: tela)")
    parser.add_argument("--saida-json", default=None, help="arquivo JSON com todos os resultados")
    args = parser.parse_args(argv)
    with open(args.entrada, "r", encoding="utf-8") as arq:
        dados = json.load(arq)
    resultado = calcular(dados, os.path.dirname(os.path.abspath(args.entrada)))
    dados["_arquivo_entrada"] = args.entrada.replace(os.sep, "/")
    texto = renderizar_md(resultado, dados)
    if args.saida_md:
        with open(args.saida_md, "w", encoding="utf-8", newline="\n") as arq:
            arq.write(texto)
    else:
        print(texto)
    if args.saida_json:
        with open(args.saida_json, "w", encoding="utf-8", newline="\n") as arq:
            json.dump(arred(resultado), arq, ensure_ascii=False, indent=2)
            arq.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
