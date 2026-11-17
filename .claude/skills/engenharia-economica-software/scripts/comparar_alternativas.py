#!/usr/bin/env python3
"""Comparação de alternativas mutuamente exclusivas (Aulas 1, 2, 10 e 11).

Casos típicos: on-premises x nuvem, manter legado x refatorar x aposentar, comprar x construir.

* Vidas iguais: escolha pelo maior VPL à TMA.
* Vidas diferentes: escolha pelo maior VPL anualizado, isto é, o CAUE com sinal
  (VPL * i(1+i)^n / [(1+i)^n - 1]); equivale a repetir cada alternativa até o MMC das vidas.
* Alternativas só de custo: os VPLs são negativos e vence o menos negativo (menor custo anual).
* Custo de oportunidade de escolher X = indicador da melhor - indicador de X.
* Matriz de decisão ponderada (opcional): soma de peso x nota, pesos somando 1.

Uso::

    python comparar_alternativas.py --exemplo > alt.json
    python comparar_alternativas.py --entrada alt.json --formato md
"""

from __future__ import annotations

import sys

from _comum import brl, executar_cli, num, tabela_md
from calc_vpl_tir import caue, descrever_tir, tir, vpl


def comparar(tma: float, alternativas: list[dict]) -> dict:
    """Calcula VPL, CAUE e TIR de cada alternativa e indica a escolha econômica."""
    resultados = []
    for alt in alternativas:
        fluxos = [float(f) for f in alt["fluxos"]]
        vida = int(alt.get("vida", len(fluxos) - 1))
        valor = vpl(tma, fluxos)
        resultados.append({"nome": alt["nome"], "descricao": alt.get("descricao", ""), "fluxos": fluxos,
                           "vida": vida, "vpl": valor, "caue": caue(valor, tma, vida), "tir": tir(fluxos)})
    vidas = {r["vida"] for r in resultados}
    criterio = "vpl" if len(vidas) == 1 else "caue"
    melhor = max(resultados, key=lambda r: r[criterio])
    for r in resultados:
        r["custo_oportunidade"] = melhor[criterio] - r[criterio]
    return {"tma": tma, "criterio": criterio, "alternativas": resultados, "escolha": melhor["nome"],
            "justificativa": ("vidas iguais: maior VPL" if criterio == "vpl"
                              else "vidas diferentes: maior VPL anualizado (CAUE)")}


def matriz_decisao(criterios: list[dict], notas: dict[str, dict[str, float]]) -> dict:
    """Matriz ponderada: pontuação = soma(peso * nota). Pesos são normalizados para somar 1."""
    soma_pesos = sum(c["peso"] for c in criterios)
    pontuacoes = {}
    for alt, notas_alt in notas.items():
        pontuacoes[alt] = sum(c["peso"] / soma_pesos * notas_alt[c["nome"]] for c in criterios)
    vencedora = max(pontuacoes, key=pontuacoes.get)
    return {"criterios": criterios, "notas": notas, "pontuacoes": pontuacoes, "vencedora": vencedora}


def calcular(dados: dict) -> dict:
    """Entrada: {"tma", "alternativas": [{"nome", "fluxos", "vida"?}], "criterios"?, "notas"?}."""
    r = comparar(float(dados["tma"]), dados["alternativas"])
    if "criterios" in dados and "notas" in dados:
        r["matriz"] = matriz_decisao(dados["criterios"], dados["notas"])
    return r


def _tir_texto(resultado_tir: dict) -> str:
    """TIR curta; em fluxos só de custo (sem troca de sinal) a TIR não se aplica."""
    if resultado_tir["status"] == "sem_raiz" and resultado_tir["trocas_sinal"] == 0:
        return "não se aplica (fluxo só de custos)"
    return descrever_tir(resultado_tir)


def renderizar_md(r: dict) -> str:
    """Tabela comparativa e, se houver, matriz de decisão."""
    linhas = [[a["nome"], a["vida"], brl(a["vpl"]), brl(a["caue"]), _tir_texto(a["tir"]),
               brl(a["custo_oportunidade"])] for a in r["alternativas"]]
    partes = [tabela_md(["Alternativa", "Vida", "VPL", "VPL anualizado (CAUE)", "TIR",
                         "Custo de oportunidade"], linhas),
              f"\nEscolha econômica: **{r['escolha']}** ({r['justificativa']})."]
    if "matriz" in r:
        m = r["matriz"]
        nomes = [c["nome"] for c in m["criterios"]]
        cab = ["Alternativa"] + [f"{c['nome']} (peso {num(c['peso'], 2)})" for c in m["criterios"]] + ["Pontuação"]
        lin = [[alt] + [num(m["notas"][alt][n], 1) for n in nomes] + [num(m["pontuacoes"][alt], 2)]
               for alt in m["notas"]]
        partes.append("\n" + tabela_md(cab, lin) + f"\n\nVencedora na matriz ponderada: **{m['vencedora']}**.")
    return "\n".join(partes)


EXEMPLO = {
    "tma": 0.10,
    "alternativas": [
        {"nome": "Servidor próprio", "fluxos": [-12000, -1500, -1500, -1500, -1500, -1500]},
        {"nome": "Nuvem paga", "fluxos": [0, -3000, -3000, -3000]},
    ],
    "criterios": [{"nome": "custo", "peso": 0.5}, {"nome": "risco", "peso": 0.3}, {"nome": "esforço", "peso": 0.2}],
    "notas": {"Servidor próprio": {"custo": 5, "risco": 6, "esforço": 4},
              "Nuvem paga": {"custo": 7, "risco": 7, "esforço": 8}},
}

if __name__ == "__main__":
    sys.exit(executar_cli(__doc__.splitlines()[0], EXEMPLO, calcular, renderizar_md))
