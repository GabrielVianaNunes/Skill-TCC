#!/usr/bin/env python3
"""Viabilidade (Aulas 6 e 8): VPL, TIR robusta, TIRM, Payback simples e descontado, IL, ROI e CAUE.

Convenção de fluxo: ``fluxos[0]`` ocorre na data zero (investimento, normalmente negativo) e
``fluxos[t]`` no fim do período ``t``. A taxa deve estar no mesmo período dos fluxos.

A TIR é calculada de forma robusta: o script conta as trocas de sinal (regra de Descartes),
varre o VPL numa grade de taxas de -99% a 1000% por período, isola cada mudança de sinal e
refina por bissecção até 1e-12. O resultado traz um ``status`` explícito:

* ``unica``: uma raiz real (caso convencional);
* ``multiplas``: mais de uma raiz; a TIR não serve como critério, use VPL e TIRM;
* ``sem_raiz``: nenhuma taxa zera o VPL (por exemplo, fluxos todos com o mesmo sinal).

Assim o script nunca devolve um número falso quando a TIR não existe ou não é única.

Uso::

    python calc_vpl_tir.py --exemplo > fluxo.json
    python calc_vpl_tir.py --entrada fluxo.json --formato md
"""

from __future__ import annotations

import sys

from _comum import anos_meses, brl, executar_cli, num, pct, tabela_md


def vpl(taxa: float, fluxos: list[float]) -> float:
    """VPL = soma de F_t / (1 + i)^t, com t a partir de 0."""
    return sum(f / (1.0 + taxa) ** t for t, f in enumerate(fluxos))


def descontar(taxa: float, fluxos: list[float]) -> list[float]:
    """Lista de valores presentes de cada fluxo."""
    return [f / (1.0 + taxa) ** t for t, f in enumerate(fluxos)]


def trocas_de_sinal(fluxos: list[float]) -> int:
    """Número de trocas de sinal da sequência (zeros ignorados): limite superior de raízes positivas."""
    sinais = [1 if f > 0 else -1 for f in fluxos if f != 0]
    return sum(1 for a, b in zip(sinais, sinais[1:]) if a != b)


def _grade_taxas() -> list[float]:
    """Grade de busca: passo de 0,1 p.p. entre -99% e 100% e de 1 p.p. entre 100% e 1000%."""
    grade = [-0.99 + k * 0.001 for k in range(0, 1990)]
    grade += [1.0 + k * 0.01 for k in range(0, 901)]
    return grade


def _bisseccao(fluxos: list[float], a: float, b: float, tol: float = 1e-12, max_iter: int = 300) -> float:
    """Bissecção clássica em [a, b] com VPL(a) e VPL(b) de sinais opostos."""
    fa = vpl(a, fluxos)
    for _ in range(max_iter):
        m = (a + b) / 2.0
        fm = vpl(m, fluxos)
        if fm == 0 or (b - a) / 2.0 < tol:
            return m
        if (fa < 0) == (fm < 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2.0


def tir(fluxos: list[float]) -> dict:
    """TIR com detecção de ausência de raiz e de múltiplas raízes.

    Devolve ``{"status", "tir", "raizes", "trocas_sinal", "mensagem"}``. ``tir`` só é preenchida
    quando há exatamente uma raiz.
    """
    trocas = trocas_de_sinal(fluxos)
    if trocas == 0:
        return {"status": "sem_raiz", "tir": None, "raizes": [], "trocas_sinal": 0,
                "mensagem": "Todos os fluxos têm o mesmo sinal: não existe taxa que zere o VPL."}
    grade = _grade_taxas()
    raizes: list[float] = []
    anterior_taxa, anterior_vpl = grade[0], vpl(grade[0], fluxos)
    for taxa in grade[1:]:
        atual = vpl(taxa, fluxos)
        if anterior_vpl == 0:
            raizes.append(anterior_taxa)
        elif (anterior_vpl < 0) != (atual < 0) and atual != 0:
            raizes.append(_bisseccao(fluxos, anterior_taxa, taxa))
        anterior_taxa, anterior_vpl = taxa, atual
    if anterior_vpl == 0:
        raizes.append(anterior_taxa)
    raizes = sorted({round(r, 10) for r in raizes})
    if not raizes:
        return {"status": "sem_raiz", "tir": None, "raizes": [], "trocas_sinal": trocas,
                "mensagem": "Há trocas de sinal, mas nenhuma taxa entre -99% e 1000% zera o VPL."}
    if len(raizes) > 1:
        return {"status": "multiplas", "tir": None, "raizes": raizes, "trocas_sinal": trocas,
                "mensagem": "Fluxo não convencional com múltiplas TIRs: decida pelo VPL e use a TIRM."}
    return {"status": "unica", "tir": raizes[0], "raizes": raizes, "trocas_sinal": trocas,
            "mensagem": "TIR única."}


def tirm(fluxos: list[float], taxa_financiamento: float, taxa_reinvestimento: float) -> float | None:
    """TIR modificada: [VF(positivos, reinvestimento) / VP(negativos, financiamento)]^(1/n) - 1."""
    n = len(fluxos) - 1
    vp_neg = sum(-f / (1.0 + taxa_financiamento) ** t for t, f in enumerate(fluxos) if f < 0)
    vf_pos = sum(f * (1.0 + taxa_reinvestimento) ** (n - t) for t, f in enumerate(fluxos) if f > 0)
    if vp_neg == 0 or vf_pos == 0 or n == 0:
        return None
    return (vf_pos / vp_neg) ** (1.0 / n) - 1.0


def payback(fluxos: list[float], taxa: float | None = None) -> dict:
    """Payback com interpolação linear dentro do período.

    Simples quando ``taxa`` é None; descontado quando há taxa. Usa o último período com
    saldo acumulado negativo (k) e interpola: payback = k + |acumulado_k| / fluxo_{k+1}.
    Assim o resultado é o prazo a partir do qual o saldo não volta a ficar negativo.
    """
    serie = descontar(taxa, fluxos) if taxa is not None else list(fluxos)
    acumulado, total = [], 0.0
    for f in serie:
        total += f
        acumulado.append(total)
    negativos = [t for t, a in enumerate(acumulado) if a < 0]
    if not negativos:
        return {"anos": 0.0, "status": "imediato", "acumulado": acumulado}
    k = negativos[-1]
    if k == len(serie) - 1:
        return {"anos": None, "status": "nao_recupera", "acumulado": acumulado}
    fracao = -acumulado[k] / serie[k + 1]
    voltou = any(a >= 0 for a in acumulado[:k])
    return {"anos": k + fracao, "status": "recupera", "periodo_inteiro": k, "fracao": fracao,
            "acumulado": acumulado, "saldo_oscilou": voltou}


def indice_lucratividade(taxa: float, fluxos: list[float]) -> float | None:
    """IL = VP dos fluxos de t = 1..n dividido pelo investimento |F0|. Aceitar se IL > 1."""
    if fluxos[0] >= 0:
        return None
    return sum(descontar(taxa, fluxos)[1:]) / -fluxos[0]


def roi(ganho: float, custo: float) -> float:
    """ROI = (ganho - custo) / custo."""
    return (ganho - custo) / custo


def roi_fluxos(fluxos: list[float], taxa: float | None = None) -> float | None:
    """ROI sobre o horizonte: (entradas - saídas) / saídas; descontado se houver taxa."""
    serie = descontar(taxa, fluxos) if taxa is not None else fluxos
    saidas = -sum(f for f in serie if f < 0)
    entradas = sum(f for f in serie if f > 0)
    return None if saidas == 0 else (entradas - saidas) / saidas


def caue(valor_presente: float, taxa: float, n: int) -> float:
    """Custo (ou benefício) anual uniforme equivalente: VP * i(1+i)^n / [(1+i)^n - 1]."""
    if taxa == 0:
        return valor_presente / n
    return valor_presente * taxa * (1.0 + taxa) ** n / ((1.0 + taxa) ** n - 1.0)


def analisar(taxa: float, fluxos: list[float], taxa_financiamento: float | None = None,
             taxa_reinvestimento: float | None = None) -> dict:
    """Pacote completo de indicadores de viabilidade para um fluxo de caixa."""
    resultado_tir = tir(fluxos)
    valor = vpl(taxa, fluxos)
    return {
        "taxa": taxa,
        "fluxos": fluxos,
        "vp_fluxos": descontar(taxa, fluxos),
        "vpl": valor,
        "tir": resultado_tir,
        "tirm": tirm(fluxos, taxa if taxa_financiamento is None else taxa_financiamento,
                     taxa if taxa_reinvestimento is None else taxa_reinvestimento),
        "payback_simples": payback(fluxos),
        "payback_descontado": payback(fluxos, taxa),
        "indice_lucratividade": indice_lucratividade(taxa, fluxos),
        "roi_nominal": roi_fluxos(fluxos),
        "roi_descontado": roi_fluxos(fluxos, taxa),
        "vpl_anualizado": caue(valor, taxa, len(fluxos) - 1) if len(fluxos) > 1 else None,
        "decisao": "viável (VPL > 0)" if valor > 0 else ("indiferente (VPL = 0)" if valor == 0 else "inviável (VPL < 0)"),
    }


def descrever_tir(resultado_tir: dict) -> str:
    """Texto curto para a TIR conforme o status."""
    if resultado_tir["status"] == "unica":
        return pct(resultado_tir["tir"])
    if resultado_tir["status"] == "multiplas":
        return "múltiplas: " + ", ".join(pct(r) for r in resultado_tir["raizes"])
    return "inexistente (" + resultado_tir["mensagem"] + ")"


def calcular(dados: dict) -> dict:
    """Entrada: {"taxa": 0.10, "fluxos": [...], "taxa_financiamento"?, "taxa_reinvestimento"?}."""
    return analisar(float(dados["taxa"]), [float(f) for f in dados["fluxos"]],
                    dados.get("taxa_financiamento"), dados.get("taxa_reinvestimento"))


def renderizar_md(r: dict) -> str:
    """Relatório Markdown curto com o fluxo descontado e os indicadores."""
    linhas = []
    acum_s = r["payback_simples"]["acumulado"]
    acum_d = r["payback_descontado"]["acumulado"]
    for t, (f, v) in enumerate(zip(r["fluxos"], r["vp_fluxos"])):
        linhas.append([t, brl(f), brl(v), brl(acum_s[t]), brl(acum_d[t])])
    partes = [tabela_md(["Período", "Fluxo", "VP do fluxo", "Acumulado simples", "Acumulado descontado"], linhas), ""]
    partes.append(tabela_md(["Indicador", "Valor"], [
        ["Taxa (TMA)", pct(r["taxa"])],
        ["VPL", brl(r["vpl"])],
        ["TIR", descrever_tir(r["tir"])],
        ["TIRM", pct(r["tirm"])],
        ["Payback simples", anos_meses(r["payback_simples"]["anos"])],
        ["Payback descontado", anos_meses(r["payback_descontado"]["anos"])],
        ["Índice de lucratividade", num(r["indice_lucratividade"], 4)],
        ["ROI descontado", pct(r["roi_descontado"])],
        ["VPL anualizado (CAUE)", brl(r["vpl_anualizado"])],
        ["Decisão", r["decisao"]],
    ]))
    return "\n".join(partes)


EXEMPLO = {"taxa": 0.10, "fluxos": [-1000, 300, 400, 500, 600]}

if __name__ == "__main__":
    sys.exit(executar_cli(__doc__.splitlines()[0], EXEMPLO, calcular, renderizar_md))
