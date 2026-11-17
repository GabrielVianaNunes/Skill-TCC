#!/usr/bin/env python3
"""Custo, preço e valor em TI (Aula 4): custos diretos e indiretos, markup, margem e valor percebido.

Fórmulas (ver references/formulas.md, seção Aula 4):

* taxa horária com encargos = salário mensal * (1 + encargos) / horas produtivas no mês;
* custo direto = soma(horas * taxa horária);
* custo indireto = soma(valor do recurso compartilhado * fração de rateio);
* preço por markup sobre custo = custo * (1 + markup);
* preço por margem sobre o preço = custo / (1 - margem);
* preço com tributos e margem (markup divisor) = custo / (1 - tributos - despesas - margem);
* preço mínimo (margem zero, só cobre custo e tributos) = custo / (1 - tributos);
* conversões: margem = markup / (1 + markup) e markup = margem / (1 - margem).

O valor percebido pelo cliente define o teto da negociação; o preço mínimo define o piso.

Uso::

    python calc_custos_preco.py --exemplo > custos.json
    python calc_custos_preco.py --entrada custos.json --formato md
"""

from __future__ import annotations

import sys

from _comum import brl, executar_cli, pct, tabela_md


def taxa_horaria(salario_mensal: float, encargos: float, horas_produtivas_mes: float) -> float:
    """Custo da hora com encargos: salário * (1 + encargos) / horas produtivas."""
    return salario_mensal * (1.0 + encargos) / horas_produtivas_mes


def markup_para_margem(markup: float) -> float:
    """Margem sobre o preço equivalente a um markup sobre o custo."""
    return markup / (1.0 + markup)


def margem_para_markup(margem: float) -> float:
    """Markup sobre o custo equivalente a uma margem sobre o preço."""
    return margem / (1.0 - margem)


def preco_markup(custo: float, markup: float) -> float:
    """Preço = custo * (1 + markup)."""
    return custo * (1.0 + markup)


def preco_margem(custo: float, margem: float) -> float:
    """Preço = custo / (1 - margem)."""
    return custo / (1.0 - margem)


def preco_markup_divisor(custo: float, tributos: float, margem: float, despesas: float = 0.0) -> float:
    """Preço que cobre tributos e despesas proporcionais e entrega a margem desejada."""
    divisor = 1.0 - tributos - despesas - margem
    if divisor <= 0:
        raise ValueError("tributos + despesas + margem devem somar menos de 100%")
    return custo / divisor


def preco_minimo(custo: float, tributos: float) -> float:
    """Piso de preço: cobre o custo total e os tributos sobre o preço, com margem zero."""
    return custo / (1.0 - tributos)


def calcular(dados: dict) -> dict:
    """Calcula custo total, preços por método e a comparação com o valor percebido."""
    itens_diretos = []
    for membro in dados.get("equipe", []):
        if "taxa_hora" in membro:
            taxa = membro["taxa_hora"]
        else:
            taxa = taxa_horaria(membro["salario_mensal"], membro.get("encargos", 0.0),
                                membro.get("horas_produtivas_mes", 160.0))
        itens_diretos.append({"papel": membro["papel"], "horas": membro["horas"], "taxa_hora": taxa,
                              "custo": membro["horas"] * taxa})
    itens_indiretos = [{"descricao": i["descricao"], "valor": i["valor"], "rateio": i.get("rateio", 1.0),
                        "custo": i["valor"] * i.get("rateio", 1.0)} for i in dados.get("indiretos", [])]
    direto = sum(i["custo"] for i in itens_diretos)
    indireto = sum(i["custo"] for i in itens_indiretos)
    custo = direto + indireto
    tributos = dados.get("tributos_sobre_preco", 0.0)
    margem = dados.get("margem_sobre_preco", 0.20)
    despesas = dados.get("despesas_sobre_preco", 0.0)
    markup = dados.get("markup", margem_para_markup(margem))
    precos = {
        "markup_sobre_custo": preco_markup(custo, markup),
        "margem_sobre_preco": preco_margem(custo, margem),
        "markup_divisor_com_tributos": preco_markup_divisor(custo, tributos, margem, despesas),
        "preco_minimo": preco_minimo(custo, tributos),
    }
    resultado = {"diretos": itens_diretos, "indiretos": itens_indiretos, "custo_direto": direto,
                 "custo_indireto": indireto, "custo_total": custo, "markup": markup,
                 "margem_equivalente_ao_markup": markup_para_margem(markup), "margem": margem,
                 "tributos": tributos, "precos": precos}
    valor = dados.get("valor_percebido")
    if valor is not None:
        ref = precos["markup_divisor_com_tributos"]
        resultado["valor_percebido"] = {
            "valor": valor,
            "preco_referencia": ref,
            "captura_de_valor": ref / valor,
            "faixa_negociacao": [precos["preco_minimo"], valor],
            "leitura": ("o preço por custo fica abaixo do valor percebido: há espaço para precificar por valor"
                        if ref < valor else
                        "o preço por custo supera o valor percebido: reduza custo ou reposicione a oferta"),
        }
    return resultado


def renderizar_md(r: dict) -> str:
    """Tabelas de custo e de preço."""
    linhas = [[i["papel"], f"{i['horas']:g}", brl(i["taxa_hora"]), brl(i["custo"])] for i in r["diretos"]]
    linhas += [[i["descricao"] + " (indireto)", "", f"rateio {pct(i['rateio'])}", brl(i["custo"])] for i in r["indiretos"]]
    linhas.append(["**Custo total**", "", "", f"**{brl(r['custo_total'])}**"])
    partes = [tabela_md(["Item", "Horas", "Taxa", "Custo"], linhas), ""]
    p = r["precos"]
    partes.append(tabela_md(["Método de preço", "Preço"], [
        [f"Markup sobre custo ({pct(r['markup'])}, margem equivalente {pct(r['margem_equivalente_ao_markup'])})",
         brl(p["markup_sobre_custo"])],
        [f"Margem sobre preço ({pct(r['margem'])})", brl(p["margem_sobre_preco"])],
        [f"Markup divisor (tributos {pct(r['tributos'])} + margem)", brl(p["markup_divisor_com_tributos"])],
        ["Preço mínimo (margem zero)", brl(p["preco_minimo"])],
    ]))
    if "valor_percebido" in r:
        v = r["valor_percebido"]
        partes.append(f"\nValor percebido: {brl(v['valor'])}; captura de valor do preço de referência: "
                      f"{pct(v['captura_de_valor'])}; faixa de negociação: {brl(v['faixa_negociacao'][0])} a "
                      f"{brl(v['faixa_negociacao'][1])}. Leitura: {v['leitura']}.")
    return "\n".join(partes)


EXEMPLO = {
    "equipe": [{"papel": "Desenvolvedor", "horas": 100, "salario_mensal": 5000, "encargos": 0.8,
                "horas_produtivas_mes": 150}],
    "indiretos": [{"descricao": "Infraestrutura compartilhada", "valor": 2000, "rateio": 0.25}],
    "markup": 0.5, "margem_sobre_preco": 0.2, "tributos_sobre_preco": 0.06, "valor_percebido": 15000,
}

if __name__ == "__main__":
    sys.exit(executar_cli(__doc__.splitlines()[0], EXEMPLO, calcular, renderizar_md))
