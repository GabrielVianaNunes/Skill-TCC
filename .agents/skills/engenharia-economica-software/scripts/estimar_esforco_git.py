#!/usr/bin/env python3
"""Estimativa de esforço (horas) a partir do histórico de commits, com faixa mínimo, provável e máximo.

Não existe apontamento de horas na maioria dos projetos acadêmicos; este script deriva uma
estimativa rastreável do histórico do repositório. A saída deve ser rotulada como
"estimativa derivada do histórico do repositório", nunca como medição.

Entrada: CSV com cabeçalho ``data_hora,autor`` (ISO 8601, um commit sem merge por linha). Gere com::

    git log --no-merges --reverse --format='%ad,%an' --date=format:'%Y-%m-%dT%H:%M:%S'

(e troque nomes por iniciais, se o repositório for público).

Heurística, por mês m:

1. Sessões: commits do mesmo autor separados por até ``intervalo_sessao_horas`` formam uma
   sessão; duração = último - primeiro commit + ``preparo_sessao_horas``. É um piso observável.
2. Dias ativos: pares (autor, dia) com commit, multiplicados por horas por dia ativo.
3. Horas_m(cenário) = max(sessões_m, dias_m * horas_dia[cenário]) * fator_sem_commit[cenário],
   em que o fator cobre análise, testes, reuniões e documentação que não geram commit.

Opcionalmente estima o trabalho anterior ao primeiro commit (base importada) por
produtividade em linhas por hora: horas = linhas / produtividade (alta, provável, baixa).

Uso::

    python estimar_esforco_git.py --exemplo
    python estimar_esforco_git.py --entrada esforco.json --formato md
"""

from __future__ import annotations

import csv
import datetime as dt
import os
import sys
from collections import defaultdict

from _comum import criar_parser, emitir, ler_json, num, tabela_md

CENARIOS = ("min", "provavel", "max")


def ler_commits(caminho: str) -> list[tuple[dt.datetime, str]]:
    """Lê o CSV ``data_hora,autor`` e devolve a lista ordenada por data."""
    with open(caminho, "r", encoding="utf-8") as arq:
        linhas = [(dt.datetime.fromisoformat(l["data_hora"]), l["autor"]) for l in csv.DictReader(arq)]
    return sorted(linhas)


def sessoes(commits: list[tuple[dt.datetime, str]], intervalo_h: float = 3.0, preparo_h: float = 1.0) -> list[dict]:
    """Agrupa commits em sessões por autor e calcula a duração de cada sessão."""
    por_autor: dict[str, list[dt.datetime]] = defaultdict(list)
    for quando, autor in commits:
        por_autor[autor].append(quando)
    resultado = []
    for autor, datas in por_autor.items():
        datas.sort()
        inicio = fim = datas[0]
        n = 1
        for quando in datas[1:]:
            if (quando - fim).total_seconds() <= intervalo_h * 3600:
                fim, n = quando, n + 1
            else:
                resultado.append({"autor": autor, "inicio": inicio, "fim": fim, "commits": n})
                inicio = fim = quando
                n = 1
        resultado.append({"autor": autor, "inicio": inicio, "fim": fim, "commits": n})
    for s in resultado:
        s["horas"] = (s["fim"] - s["inicio"]).total_seconds() / 3600.0 + preparo_h
    return sorted(resultado, key=lambda s: s["inicio"])


def estimar(commits: list[tuple[dt.datetime, str]], params: dict) -> dict:
    """Aplica a heurística e devolve a tabela mensal e os totais por cenário."""
    h_dia = params.get("horas_por_dia_ativo", {"min": 4, "provavel": 6, "max": 8})
    fator = params.get("fator_trabalho_sem_commit", {"min": 1.0, "provavel": 1.5, "max": 2.0})
    lista_sessoes = sessoes(commits, params.get("intervalo_sessao_horas", 3.0), params.get("preparo_sessao_horas", 1.0))
    meses: dict[str, dict] = defaultdict(lambda: {"commits": 0, "dias": set(), "horas_sessoes": 0.0,
                                                  "sessoes": 0, "autores": defaultdict(int)})
    for quando, autor in commits:
        m = meses[quando.strftime("%Y-%m")]
        m["commits"] += 1
        m["dias"].add((quando.date(), autor))
        m["autores"][autor] += 1
    for s in lista_sessoes:
        m = meses[s["inicio"].strftime("%Y-%m")]
        m["horas_sessoes"] += s["horas"]
        m["sessoes"] += 1
    tabela = []
    totais = {c: 0.0 for c in CENARIOS}
    for chave in sorted(meses):
        m = meses[chave]
        dias = len(m["dias"])
        linha = {"mes": chave, "commits": m["commits"], "dias_ativos": dias, "sessoes": m["sessoes"],
                 "horas_sessoes": m["horas_sessoes"], "commits_por_autor": dict(m["autores"])}
        for c in CENARIOS:
            linha[f"horas_{c}"] = max(m["horas_sessoes"], dias * h_dia[c]) * fator[c]
            totais[c] += linha[f"horas_{c}"]
        tabela.append(linha)
    return {"meses": tabela, "totais": totais, "total_commits": len(commits),
            "total_dias_ativos": sum(l["dias_ativos"] for l in tabela),
            "total_horas_sessoes": sum(l["horas_sessoes"] for l in tabela),
            "parametros": {"horas_por_dia_ativo": h_dia, "fator_trabalho_sem_commit": fator,
                           "intervalo_sessao_horas": params.get("intervalo_sessao_horas", 3.0),
                           "preparo_sessao_horas": params.get("preparo_sessao_horas", 1.0)},
            "rotulo": "estimativa derivada do histórico do repositório (não é medição de horas)"}


def estimar_base_importada(linhas: float, produtividade: dict) -> dict:
    """Horas do código anterior ao primeiro commit: linhas / produtividade (linhas por hora)."""
    return {"linhas": linhas, "produtividade": produtividade,
            "horas_min": linhas / produtividade["alta"],
            "horas_provavel": linhas / produtividade["provavel"],
            "horas_max": linhas / produtividade["baixa"]}


def horas_informadas(meses: list[dict]) -> dict:
    """Alternativa sem git: usa horas por mês informadas pelo usuário (apontamento ou estimativa)."""
    tabela = []
    for m in meses:
        tabela.append({"mes": m["mes"], "commits": m.get("commits", 0), "dias_ativos": m.get("dias_ativos", 0),
                       "sessoes": 0, "horas_sessoes": 0.0, "horas_min": m["horas_min"],
                       "horas_provavel": m["horas_provavel"], "horas_max": m["horas_max"]})
    totais = {c: sum(m[f"horas_{c}"] for m in tabela) for c in CENARIOS}
    return {"meses": tabela, "totais": totais, "total_commits": sum(m["commits"] for m in tabela),
            "total_dias_ativos": sum(m["dias_ativos"] for m in tabela), "total_horas_sessoes": 0.0,
            "parametros": {"horas_por_dia_ativo": {c: 0 for c in CENARIOS},
                           "fator_trabalho_sem_commit": {c: 1.0 for c in CENARIOS},
                           "intervalo_sessao_horas": 0, "preparo_sessao_horas": 0},
            "rotulo": "horas informadas pelo usuário (não derivadas do git)"}


def calcular(dados: dict) -> dict:
    """Entrada: {"arquivo_log": csv, parâmetros, "base_importada"?} ou {"meses_informados": [...]}."""
    if "meses_informados" in dados:
        r = horas_informadas(dados["meses_informados"])
        if "base_importada" in dados:
            b = dados["base_importada"]
            r["base_importada"] = estimar_base_importada(b["linhas"], b["produtividade_linhas_hora"])
        return r
    caminho = dados["arquivo_log"]
    if not os.path.isabs(caminho):
        caminho = os.path.join(dados.get("_base_dir", ""), caminho)
    commits = ler_commits(caminho)
    excluir = set(dados.get("excluir_datas", []))
    commits = [c for c in commits if c[0].date().isoformat() not in excluir]
    r = estimar(commits, dados)
    if "base_importada" in dados:
        b = dados["base_importada"]
        r["base_importada"] = estimar_base_importada(b["linhas"], b["produtividade_linhas_hora"])
    return r


def renderizar_md(r: dict) -> str:
    """Tabela mensal com a faixa de horas."""
    linhas = [[m["mes"], m["commits"], m["dias_ativos"], num(m["horas_sessoes"], 1), num(m["horas_min"], 1),
               num(m["horas_provavel"], 1), num(m["horas_max"], 1)] for m in r["meses"]]
    t = r["totais"]
    linhas.append(["**Total**", r["total_commits"], r["total_dias_ativos"], num(r["total_horas_sessoes"], 1),
                   num(t["min"], 1), num(t["provavel"], 1), num(t["max"], 1)])
    texto = tabela_md(["Mês", "Commits", "Dias ativos", "Horas em sessões (piso)", "Mínimo (h)", "Provável (h)",
                       "Máximo (h)"], linhas)
    return texto + f"\n\nRótulo: {r['rotulo']}."


EXEMPLO = {
    "arquivo_log": "tcc-git-log.csv",
    "excluir_datas": ["2026-05-25"],
    "intervalo_sessao_horas": 3, "preparo_sessao_horas": 1,
    "horas_por_dia_ativo": {"min": 4, "provavel": 6, "max": 8},
    "fator_trabalho_sem_commit": {"min": 1.0, "provavel": 1.5, "max": 2.0},
    "base_importada": {"linhas": 36722, "produtividade_linhas_hora": {"alta": 45, "provavel": 30, "baixa": 20}},
}


def main(argv: list[str] | None = None) -> int:
    """CLI própria: resolve o caminho do CSV relativo ao arquivo JSON de entrada."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
    import json
    parser = criar_parser(__doc__.splitlines()[0], EXEMPLO)
    args = parser.parse_args(argv)
    if args.exemplo:
        print(json.dumps(EXEMPLO, ensure_ascii=False, indent=2))
        return 0
    dados = ler_json(args.entrada)
    if args.entrada not in (None, "-"):
        dados["_base_dir"] = os.path.dirname(os.path.abspath(args.entrada))
    texto = emitir(calcular(dados), args.formato, renderizar_md)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8", newline="\n") as arq:
            arq.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
