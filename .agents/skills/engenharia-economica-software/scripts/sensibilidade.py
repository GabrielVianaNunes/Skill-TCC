#!/usr/bin/env python3
"""Sensibilidade, cenários e ponto de equilíbrio (Aula 7).

Modelo de fluxo usado: F_0 = -investimento e F_t = benefícios_t - custos_t (t = 1..n).

* Tornado: varia uma variável por vez (TMA, benefícios, custos operacionais e investimento)
  em -X% e +X% (padrão 20%) e ordena pela amplitude do VPL.
* Cenários: aplica multiplicadores simultâneos (pessimista, base, otimista).
* Ponto de equilíbrio econômico: multiplicador dos benefícios que zera o VPL,
  m* = [VP(custos) + investimento] / VP(benefícios), e a TMA de equilíbrio (= TIR).
* Ponto de equilíbrio contábil em unidades: Q* = custos fixos / (preço - custo variável unitário).

Uso::

    python sensibilidade.py --exemplo > sens.json
    python sensibilidade.py --entrada sens.json --formato md
"""

from __future__ import annotations

import sys

from _comum import brl, executar_cli, num, pct, tabela_md
from calc_vpl_tir import tir, vpl

VARIAVEIS = ("taxa", "beneficios", "custos", "investimento")
ROTULOS = {"taxa": "TMA", "beneficios": "Benefícios / receitas", "custos": "Custos operacionais (OpEx)",
           "investimento": "Investimento inicial"}


def montar_fluxos(investimento: float, beneficios: list[float], custos: list[float],
                  fatores: dict[str, float] | None = None) -> list[float]:
    """Monta o fluxo aplicando multiplicadores às componentes."""
    f = {"beneficios": 1.0, "custos": 1.0, "investimento": 1.0, **(fatores or {})}
    return [-investimento * f["investimento"]] + [b * f["beneficios"] - c * f["custos"]
                                                   for b, c in zip(beneficios, custos)]


def vpl_modelo(dados: dict, fatores: dict[str, float] | None = None) -> float:
    """VPL do modelo com multiplicadores (inclusive sobre a taxa)."""
    fatores = fatores or {}
    taxa = dados["taxa"] * fatores.get("taxa", 1.0)
    return vpl(taxa, montar_fluxos(dados["investimento"], dados["beneficios"], dados["custos"], fatores))


def tornado(dados: dict, variacao: float = 0.20) -> list[dict]:
    """Uma variável por vez em (1 - variação) e (1 + variação); ordenado por amplitude."""
    linhas = []
    for var in VARIAVEIS:
        baixo = vpl_modelo(dados, {var: 1.0 - variacao})
        alto = vpl_modelo(dados, {var: 1.0 + variacao})
        linhas.append({"variavel": var, "rotulo": ROTULOS[var], "vpl_menos": baixo, "vpl_mais": alto,
                       "amplitude": abs(alto - baixo)})
    return sorted(linhas, key=lambda x: -x["amplitude"])


def equilibrio_beneficios(dados: dict) -> float | None:
    """Multiplicador dos benefícios que zera o VPL (solução exata, o VPL é linear nele)."""
    taxa = dados["taxa"]
    vp_b = vpl(taxa, [0.0] + list(dados["beneficios"]))
    vp_c = vpl(taxa, [0.0] + list(dados["custos"]))
    return None if vp_b == 0 else (vp_c + dados["investimento"]) / vp_b


def ponto_equilibrio_unidades(custos_fixos: float, preco: float, custo_variavel: float) -> float:
    """Q* = CF / (p - cv); exige margem de contribuição unitária positiva."""
    margem = preco - custo_variavel
    if margem <= 0:
        raise ValueError("margem de contribuição unitária não positiva: não há ponto de equilíbrio")
    return custos_fixos / margem


def calcular(dados: dict) -> dict:
    """Base, tornado, cenários e pontos de equilíbrio."""
    variacao = dados.get("variacao", 0.20)
    base_fluxos = montar_fluxos(dados["investimento"], dados["beneficios"], dados["custos"])
    r = {"vpl_base": vpl(dados["taxa"], base_fluxos), "fluxos_base": base_fluxos, "variacao": variacao,
         "tornado": tornado(dados, variacao), "multiplicador_equilibrio_beneficios": equilibrio_beneficios(dados),
         "tma_equilibrio": tir(base_fluxos)}
    cenarios = {}
    for nome, fatores in dados.get("cenarios", {}).items():
        fl = montar_fluxos(dados["investimento"], dados["beneficios"], dados["custos"], fatores)
        cenarios[nome] = {"fatores": fatores, "fluxos": fl, "vpl": vpl(dados["taxa"] * fatores.get("taxa", 1.0), fl)}
    if cenarios:
        r["cenarios"] = cenarios
    if "equilibrio_unidades" in dados:
        e = dados["equilibrio_unidades"]
        r["ponto_equilibrio_unidades"] = ponto_equilibrio_unidades(e["custos_fixos"], e["preco"], e["custo_variavel"])
    return r


def renderizar_md(r: dict) -> str:
    """Tornado, cenários e equilíbrio em Markdown."""
    v = pct(r["variacao"], 0)
    linhas = [[t["rotulo"], brl(t["vpl_menos"]), brl(t["vpl_mais"]), brl(t["amplitude"])] for t in r["tornado"]]
    partes = [f"VPL base: {brl(r['vpl_base'])}\n",
              tabela_md(["Variável", f"VPL com -{v}", f"VPL com +{v}", "Amplitude"], linhas)]
    if "cenarios" in r:
        partes.append("\n" + tabela_md(["Cenário", "VPL"], [[k, brl(c["vpl"])] for k, c in r["cenarios"].items()]))
    m = r["multiplicador_equilibrio_beneficios"]
    if m is not None and m <= 1:
        partes.append(f"\nOs benefícios podem cair até {pct(1 - m)} antes de o VPL zerar "
                      f"(multiplicador de equilíbrio {num(m, 4)}).")
    elif m is not None:
        partes.append(f"\nOs benefícios precisam subir {pct(m - 1)} para o VPL zerar "
                      f"(multiplicador de equilíbrio {num(m, 4)}).")
    if "ponto_equilibrio_unidades" in r:
        partes.append(f"Ponto de equilíbrio contábil: {num(r['ponto_equilibrio_unidades'], 2)} unidades.")
    return "\n".join(partes)


EXEMPLO = {
    "taxa": 0.10, "investimento": 1000, "beneficios": [500, 500, 500], "custos": [100, 100, 100],
    "variacao": 0.20,
    "cenarios": {"pessimista": {"beneficios": 0.8, "custos": 1.2, "investimento": 1.2},
                 "base": {}, "otimista": {"beneficios": 1.2, "custos": 0.8, "investimento": 0.9}},
    "equilibrio_unidades": {"custos_fixos": 10000, "preco": 50, "custo_variavel": 30},
}

if __name__ == "__main__":
    sys.exit(executar_cli(__doc__.splitlines()[0], EXEMPLO, calcular, renderizar_md))
