#!/usr/bin/env python3
"""Depreciação de ativos de TI e efeito dos tributos no fluxo de caixa (Aulas 6 e 8).

Métodos de depreciação:

* linear: D = (custo - residual) / vida;
* soma dos dígitos dos anos (SDA): D_t = (custo - residual) * (vida - t + 1) / [vida(vida+1)/2].

Fluxo de caixa após impostos (lucro real, didático):
FC = (Receita - Custos - Depreciação) * (1 - t) + Depreciação = (Receita - Custos)(1 - t) + t * D.
O termo ``t * D`` é o escudo fiscal da depreciação.

Regimes de tributação são parâmetros de entrada, nunca fatos: Simples Nacional (alíquota efetiva
sobre a receita) e Lucro Presumido (presunção sobre a receita mais tributos sobre faturamento).
Nesses dois regimes a depreciação não reduz a base de cálculo, logo o escudo fiscal é zero.
Os valores de referência ficam em references/aliquotas.md e devem ser validados com um contador.

Uso::

    python calc_depreciacao_tributos.py --exemplo > dep.json
    python calc_depreciacao_tributos.py --entrada dep.json --formato md
"""

from __future__ import annotations

import sys

from _comum import brl, executar_cli, pct, tabela_md


def depreciacao_linear(custo: float, vida: int, residual: float = 0.0) -> list[float]:
    """Quotas anuais iguais: (custo - residual) / vida."""
    quota = (custo - residual) / vida
    return [quota] * vida


def depreciacao_soma_digitos(custo: float, vida: int, residual: float = 0.0) -> list[float]:
    """Quotas decrescentes pela soma dos dígitos dos anos."""
    soma = vida * (vida + 1) / 2.0
    base = custo - residual
    return [base * (vida - t + 1) / soma for t in range(1, vida + 1)]


def taxa_anual_para_vida(taxa_anual: float) -> int:
    """Converte taxa anual de depreciação (ex.: 0,20) em vida útil em anos (ex.: 5)."""
    return int(round(1.0 / taxa_anual))


def escudo_fiscal(depreciacao: float, aliquota_ir: float) -> float:
    """Economia de imposto gerada pela depreciação: t * D (só em regime de lucro real)."""
    return depreciacao * aliquota_ir


def fluxo_apos_impostos(receita: float, custos: float, depreciacao: float, aliquota_ir: float) -> dict:
    """Fluxo operacional após IR em lucro real, com prejuízo tratado sem crédito (conservador)."""
    lair = receita - custos - depreciacao
    imposto = max(lair, 0.0) * aliquota_ir
    return {"lair": lair, "imposto": imposto, "lucro_liquido": lair - imposto,
            "fluxo_caixa": lair - imposto + depreciacao,
            "escudo_fiscal": escudo_fiscal(depreciacao, aliquota_ir) if lair > 0 else 0.0}


def imposto_simples(receita: float, aliquota_efetiva: float) -> float:
    """Simples Nacional: imposto = receita * alíquota efetiva (parâmetro informado)."""
    return receita * aliquota_efetiva


def aliquota_efetiva_simples(rbt12: float, aliquota_nominal: float, parcela_deduzir: float) -> float:
    """Alíquota efetiva do Simples: (RBT12 * Aliq - PD) / RBT12. Valores da faixa: validar."""
    return (rbt12 * aliquota_nominal - parcela_deduzir) / rbt12


def imposto_presumido(receita: float, presuncao: float, irpj: float, csll: float,
                      tributos_faturamento: float, adicional_irpj: float = 0.0,
                      limite_adicional: float = 240000.0) -> dict:
    """Lucro Presumido (serviços): IRPJ e CSLL sobre a base presumida + tributos sobre faturamento.

    ``tributos_faturamento`` agrega PIS, COFINS e ISS (ou seus sucessores na transição da
    reforma tributária). Todos os percentuais são parâmetros a validar.
    """
    base = receita * presuncao
    ir = base * irpj + max(base - limite_adicional, 0.0) * adicional_irpj
    cs = base * csll
    fat = receita * tributos_faturamento
    total = ir + cs + fat
    return {"base_presumida": base, "irpj": ir, "csll": cs, "tributos_faturamento": fat,
            "total": total, "carga_efetiva": total / receita if receita else 0.0}


def calcular(dados: dict) -> dict:
    """Calcula depreciação dos ativos e, se houver, o efeito tributário por regime."""
    ativos = []
    for ativo in dados.get("ativos", []):
        vida = ativo.get("vida_anos") or taxa_anual_para_vida(ativo["taxa_anual"])
        residual = ativo.get("residual", 0.0)
        ativos.append({
            "nome": ativo["nome"], "custo": ativo["custo"], "vida_anos": vida,
            "linear": depreciacao_linear(ativo["custo"], vida, residual),
            "soma_digitos": depreciacao_soma_digitos(ativo["custo"], vida, residual),
        })
    resultado = {"ativos": ativos}
    trib = dados.get("tributos")
    if trib:
        receita, custos = trib["receita"], trib["custos"]
        dep = trib.get("depreciacao", sum(a["linear"][0] for a in ativos))
        resultado["lucro_real"] = fluxo_apos_impostos(receita, custos, dep, trib.get("aliquota_ir_csll", 0.34))
        if "simples_aliquota_efetiva" in trib:
            imp = imposto_simples(receita, trib["simples_aliquota_efetiva"])
            resultado["simples"] = {"imposto": imp, "fluxo_caixa": receita - custos - imp, "escudo_fiscal": 0.0}
        if "presumido" in trib:
            p = trib["presumido"]
            imp = imposto_presumido(receita, p["presuncao"], p["irpj"], p["csll"], p["tributos_faturamento"],
                                    p.get("adicional_irpj", 0.0))
            resultado["presumido"] = {**imp, "fluxo_caixa": receita - custos - imp["total"], "escudo_fiscal": 0.0}
    return resultado


def renderizar_md(r: dict) -> str:
    """Tabelas de depreciação e comparação de regimes."""
    partes = []
    for a in r["ativos"]:
        linhas = [[t + 1, brl(l), brl(s)] for t, (l, s) in enumerate(zip(a["linear"], a["soma_digitos"]))]
        partes.append(f"**{a['nome']}** (custo {brl(a['custo'])}, vida {a['vida_anos']} anos)\n")
        partes.append(tabela_md(["Ano", "Linear", "Soma dos dígitos"], linhas) + "\n")
    if "lucro_real" in r:
        lr = r["lucro_real"]
        linhas = [["Lucro real", brl(lr["imposto"]), brl(lr["fluxo_caixa"]), brl(lr["escudo_fiscal"])]]
        if "simples" in r:
            linhas.append(["Simples Nacional", brl(r["simples"]["imposto"]), brl(r["simples"]["fluxo_caixa"]), brl(0)])
        if "presumido" in r:
            p = r["presumido"]
            linhas.append([f"Lucro Presumido (carga {pct(p['carga_efetiva'])})", brl(p["total"]),
                           brl(p["fluxo_caixa"]), brl(0)])
        partes.append(tabela_md(["Regime", "Tributos", "Fluxo de caixa", "Escudo fiscal"], linhas))
    return "\n".join(partes)


EXEMPLO = {
    "ativos": [{"nome": "Notebook de desenvolvimento", "custo": 5000, "taxa_anual": 0.20}],
    "tributos": {"receita": 100000, "custos": 60000, "aliquota_ir_csll": 0.34,
                 "simples_aliquota_efetiva": 0.06,
                 "presumido": {"presuncao": 0.32, "irpj": 0.15, "csll": 0.09, "tributos_faturamento": 0.0565}},
}

if __name__ == "__main__":
    sys.exit(executar_cli(__doc__.splitlines()[0], EXEMPLO, calcular, renderizar_md))
