#!/usr/bin/env python3
"""Métricas de produtos digitais (Aulas 6 e 8): CAC, LTV, churn, LTV/CAC, payback de CAC e projeção de assinaturas.

Fórmulas (período mensal):

* churn = clientes perdidos no mês / clientes no início do mês;
* vida média do cliente = 1 / churn (meses);
* CAC = (gastos de marketing + vendas no período) / novos clientes no período;
* LTV simples = ARPA * margem bruta / churn;
* LTV descontado = ARPA * margem bruta / (i + churn), com i = TMA mensal
  (soma da série infinita ARPA*m*(1-c)^(t-1)/(1+i)^t);
* LTV/CAC (referência de mercado usual: 3 ou mais) e payback de CAC = CAC / (ARPA * margem) meses.

A projeção de assinaturas usa a recorrência ativos_m = ativos_(m-1) * (1 - churn) + novos_m,
com valores esperados (frações de cliente são aceitas por serem médias).

Uso::

    python metricas_produto.py --exemplo > produto.json
    python metricas_produto.py --entrada produto.json --formato md
"""

from __future__ import annotations

import sys

from _comum import brl, executar_cli, num, pct, tabela_md


def churn(perdidos: float, clientes_inicio: float) -> float:
    """Taxa de cancelamento do período."""
    return perdidos / clientes_inicio


def cac(gasto_aquisicao: float, novos_clientes: float) -> float:
    """Custo de aquisição de cliente."""
    return gasto_aquisicao / novos_clientes


def ltv(arpa: float, margem_bruta: float, churn_mensal: float, taxa_mensal: float = 0.0) -> float:
    """LTV = ARPA * margem / (i + churn); com i = 0 vira a fórmula simples."""
    return arpa * margem_bruta / (taxa_mensal + churn_mensal)


def payback_cac(cac_valor: float, arpa: float, margem_bruta: float) -> float:
    """Meses de margem necessários para recuperar o CAC."""
    return cac_valor / (arpa * margem_bruta)


def projetar_assinaturas(novos_por_ano: list[float], churn_mensal: float, preco_mensal: float,
                         clientes_iniciais: float = 0.0) -> list[dict]:
    """Projeção mensal agregada por ano: clientes ativos, novos, perdidos e receita."""
    ativos = clientes_iniciais
    anos = []
    for novos_ano in novos_por_ano:
        receita = perdidos = 0.0
        novos_mes = novos_ano / 12.0
        for _ in range(12):
            saem = ativos * churn_mensal
            ativos = ativos - saem + novos_mes
            perdidos += saem
            receita += ativos * preco_mensal
        anos.append({"novos": novos_ano, "perdidos": perdidos, "ativos_fim": ativos, "receita": receita})
    return anos


def calcular(dados: dict) -> dict:
    """Calcula as métricas unitárias e, se informado, projeta as assinaturas."""
    c = dados.get("churn_mensal")
    if c is None:
        c = churn(dados["perdidos_mes"], dados["clientes_inicio_mes"])
    custo_aq = dados.get("cac")
    if custo_aq is None:
        custo_aq = cac(dados["gasto_aquisicao"], dados["novos_clientes"])
    arpa, margem = dados["arpa_mensal"], dados["margem_bruta"]
    i = dados.get("taxa_mensal", 0.0)
    r = {
        "churn_mensal": c,
        "vida_media_meses": 1.0 / c,
        "cac": custo_aq,
        "ltv_simples": ltv(arpa, margem, c),
        "ltv_descontado": ltv(arpa, margem, c, i),
        "taxa_mensal": i,
        "payback_cac_meses": payback_cac(custo_aq, arpa, margem),
    }
    r["ltv_cac"] = r["ltv_descontado"] / custo_aq
    r["leitura"] = ("relação saudável (LTV/CAC >= 3)" if r["ltv_cac"] >= 3 else
                    "relação frágil (LTV/CAC < 3): reduza CAC, aumente retenção ou preço")
    if "novos_por_ano" in dados:
        r["projecao"] = projetar_assinaturas(dados["novos_por_ano"], c, arpa, dados.get("clientes_iniciais", 0.0))
    return r


def renderizar_md(r: dict) -> str:
    """Tabela de métricas unitárias e projeção."""
    partes = [tabela_md(["Métrica", "Valor"], [
        ["Churn mensal", pct(r["churn_mensal"])],
        ["Vida média do cliente", num(r["vida_media_meses"], 1) + " meses"],
        ["CAC", brl(r["cac"])],
        ["LTV simples", brl(r["ltv_simples"])],
        [f"LTV descontado (i = {pct(r['taxa_mensal'], 3)} a.m.)", brl(r["ltv_descontado"])],
        ["LTV/CAC", num(r["ltv_cac"], 2)],
        ["Payback do CAC", num(r["payback_cac_meses"], 1) + " meses"],
        ["Leitura", r["leitura"]],
    ])]
    if "projecao" in r:
        linhas = [[k + 1, num(a["novos"], 1), num(a["perdidos"], 2), num(a["ativos_fim"], 2), brl(a["receita"])]
                  for k, a in enumerate(r["projecao"])]
        partes.append("\n" + tabela_md(["Ano", "Novos", "Perdidos", "Ativos no fim", "Receita"], linhas))
    return "\n".join(partes)


EXEMPLO = {"arpa_mensal": 100, "margem_bruta": 0.8, "churn_mensal": 0.05, "cac": 400, "taxa_mensal": 0.01,
           "novos_por_ano": [12, 12]}

if __name__ == "__main__":
    sys.exit(executar_cli(__doc__.splitlines()[0], EXEMPLO, calcular, renderizar_md))
