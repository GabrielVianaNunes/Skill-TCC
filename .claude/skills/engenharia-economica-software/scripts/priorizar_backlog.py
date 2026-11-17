#!/usr/bin/env python3
"""Priorização econômica de backlog e princípio "bom o suficiente" (Aulas 10, 11 e 12).

Para cada item o script calcula:

* razão Valor/Esforço (valor de 1 a 10 dividido pelas horas) e o quadrante da matriz
  Valor x Esforço (ganho rápido, projeto estratégico, preenchimento, evitar);
* WSJF = (valor de negócio + criticidade no tempo + redução de risco) / tamanho, com
  tamanho em dias ideais (horas / 8);
* ICE = impacto x confiança x facilidade (cada um de 1 a 10);
* custo = horas x taxa horária; custo de atraso mensal = valor anual / 12;
* VPL do item = valor anual x fator de série [1 - (1+i)^-n] / i - custo.

Regra "bom o suficiente": um item só entra se o ganho marginal (VPL do item) for positivo,
ou seja, se o benefício adicional superar o custo adicional. Itens com VPL positivo são
selecionados pela razão Valor/Esforço até a capacidade do ciclo; o resto vai para o próximo ciclo.

Uso::

    python priorizar_backlog.py --exemplo > backlog.json
    python priorizar_backlog.py --entrada backlog.json --formato md
"""

from __future__ import annotations

import math
import sys

from _comum import brl, executar_cli, num, tabela_md
from calc_tvm import fator_vp_serie


def facilidade_padrao(horas: float) -> float:
    """Facilidade de 1 a 10 derivada do esforço: 10 - 1,25 * log2(horas), limitada a [1, 10]."""
    return max(1.0, min(10.0, 10.0 - 1.25 * math.log2(max(horas, 1.0))))


def quadrante(valor: float, horas: float, limiar_valor: float, limiar_horas: float) -> str:
    """Classificação na matriz Valor x Esforço."""
    alto_valor = valor >= limiar_valor
    baixo_esforco = horas <= limiar_horas
    if alto_valor and baixo_esforco:
        return "ganho rápido"
    if alto_valor:
        return "projeto estratégico"
    if baixo_esforco:
        return "preenchimento"
    return "evitar"


def bom_o_suficiente(niveis: list[dict]) -> dict:
    """Escolhe o nível de qualidade onde o ganho marginal ainda supera o custo marginal.

    ``niveis`` traz, em ordem crescente de qualidade, ``custo`` e ``beneficio`` acumulados.
    Para no último nível cujo benefício marginal >= custo marginal.
    """
    escolhido = 0
    marginais = []
    for k in range(1, len(niveis)):
        dc = niveis[k]["custo"] - niveis[k - 1]["custo"]
        db = niveis[k]["beneficio"] - niveis[k - 1]["beneficio"]
        marginais.append({"nivel": niveis[k].get("nome", k), "custo_marginal": dc, "beneficio_marginal": db})
        if db >= dc and escolhido == k - 1:
            escolhido = k
    return {"nivel_escolhido": niveis[escolhido].get("nome", escolhido), "indice": escolhido, "marginais": marginais}


def priorizar(dados: dict) -> dict:
    """Calcula as métricas, ordena por Valor/Esforço e aplica a regra de capacidade e VPL."""
    taxa_hora = dados.get("taxa_hora", 0.0)
    tma = dados.get("tma", 0.10)
    horizonte = int(dados.get("horizonte_anos", 5))
    capacidade = dados.get("capacidade_horas")
    limiar_valor = dados.get("limiar_valor", 6)
    limiar_horas = dados.get("limiar_horas", 16)
    fator = fator_vp_serie(tma, horizonte)
    itens = []
    for it in dados["itens"]:
        horas = float(it["esforco_horas"])
        valor = float(it["valor"])
        custo = horas * taxa_hora
        valor_anual = float(it.get("valor_anual", 0.0))
        facil = it.get("facilidade", facilidade_padrao(horas))
        conf = it.get("confianca", 7)
        cod = valor + it.get("criticidade_tempo", valor) + it.get("reducao_risco", 0)
        itens.append({
            **it,
            "custo": custo,
            "razao_valor_esforco": valor / horas,
            "quadrante": quadrante(valor, horas, limiar_valor, limiar_horas),
            "wsjf": cod / max(horas / 8.0, 0.25),
            "ice": valor * conf * facil,
            "facilidade": facil,
            "custo_atraso_mensal": valor_anual / 12.0,
            "vpl_item": valor_anual * fator - custo,
        })
    itens.sort(key=lambda x: (-x["razao_valor_esforco"], x["esforco_horas"]))
    usadas = 0.0
    for pos, it in enumerate(itens, start=1):
        it["posicao"] = pos
        if it.get("decisao_fixa"):
            it["decisao"] = it["decisao_fixa"]
        elif it["vpl_item"] <= 0:
            it["decisao"] = "não fazer agora (bom o suficiente: ganho marginal menor que o custo)"
        elif capacidade is None or usadas + it["esforco_horas"] <= capacidade:
            it["decisao"] = "fazer neste ciclo"
            usadas += it["esforco_horas"]
        else:
            it["decisao"] = "próximo ciclo (VPL positivo, sem capacidade agora)"
    ranking_wsjf = [i["id"] for i in sorted(itens, key=lambda x: -x["wsjf"])]
    ranking_ice = [i["id"] for i in sorted(itens, key=lambda x: -x["ice"])]
    return {"itens": itens, "horas_comprometidas": usadas, "capacidade_horas": capacidade,
            "fator_serie": fator, "ranking_valor_esforco": [i["id"] for i in itens],
            "ranking_wsjf": ranking_wsjf, "ranking_ice": ranking_ice}


def calcular(dados: dict) -> dict:
    """Entrada com ``itens`` (backlog) e/ou ``niveis`` (análise de bom o suficiente)."""
    resultado = priorizar(dados) if "itens" in dados else {}
    if "niveis" in dados:
        resultado["bom_o_suficiente"] = bom_o_suficiente(dados["niveis"])
    return resultado


def renderizar_md(r: dict) -> str:
    """Tabela de ranking com decisão."""
    partes = []
    if "itens" in r:
        linhas = [[i["posicao"], i["id"], i["titulo"], num(i["valor"], 0), num(i["esforco_horas"], 0),
                   num(i["razao_valor_esforco"], 3), i["quadrante"], num(i["wsjf"], 2), num(i["ice"], 0),
                   brl(i["vpl_item"]), i["decisao"]] for i in r["itens"]]
        partes.append(tabela_md(["#", "Id", "Item", "Valor", "Horas", "Valor/Esforço", "Quadrante", "WSJF", "ICE",
                                 "VPL do item", "Decisão"], linhas))
        partes.append(f"\nHoras comprometidas no ciclo: {num(r['horas_comprometidas'], 0)} de "
                      f"{num(r['capacidade_horas'], 0) if r['capacidade_horas'] else 'sem limite'}.")
        partes.append("Ranking WSJF: " + ", ".join(r["ranking_wsjf"]) + ". Ranking ICE: " + ", ".join(r["ranking_ice"]) + ".")
    if "bom_o_suficiente" in r:
        b = r["bom_o_suficiente"]
        partes.append(f"\nNível 'bom o suficiente': {b['nivel_escolhido']}.")
    return "\n".join(partes)


EXEMPLO = {
    "taxa_hora": 60, "tma": 0.10, "horizonte_anos": 5, "capacidade_horas": 40,
    "itens": [
        {"id": "A", "titulo": "Correção pequena de alto valor", "valor": 8, "esforco_horas": 4, "valor_anual": 2000},
        {"id": "B", "titulo": "Módulo novo grande", "valor": 7, "esforco_horas": 80, "valor_anual": 3000},
        {"id": "C", "titulo": "Ajuste cosmético", "valor": 2, "esforco_horas": 6, "valor_anual": 50},
    ],
    "niveis": [{"nome": "60% cobertura", "custo": 0, "beneficio": 0},
               {"nome": "70% cobertura", "custo": 1000, "beneficio": 2500},
               {"nome": "80% cobertura", "custo": 2500, "beneficio": 3500},
               {"nome": "90% cobertura", "custo": 5500, "beneficio": 4000}],
}

if __name__ == "__main__":
    sys.exit(executar_cli(__doc__.splitlines()[0], EXEMPLO, calcular, renderizar_md))
