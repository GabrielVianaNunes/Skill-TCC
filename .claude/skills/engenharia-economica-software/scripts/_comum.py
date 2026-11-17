"""Funções utilitárias compartilhadas pelos scripts da skill engenharia-economica-software.

Somente biblioteca padrão do Python (3.9 ou superior). Este módulo cuida de:

* formatação numérica no padrão brasileiro (R$ 1.234,56 e 12,34%);
* leitura de entrada JSON (arquivo ou entrada padrão) e escrita de saída JSON ou Markdown;
* um analisador de argumentos padronizado, para que todos os scripts tenham a mesma interface:
  ``--entrada ARQUIVO`` (ou ``-`` para stdin), ``--formato json|md``, ``--saida`` e ``--exemplo``.

Nenhuma função aqui faz cálculo financeiro; os cálculos ficam nos scripts ``calc_*``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Any, Callable, Iterable

__all__ = [
    "brl", "pct", "num", "anos_meses", "ler_json", "emitir",
    "tabela_md", "criar_parser", "executar_cli", "arred",
]


def _agrupar_milhar(inteiro: str) -> str:
    """Insere pontos como separador de milhar em uma string de dígitos."""
    partes = []
    while len(inteiro) > 3:
        partes.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    partes.insert(0, inteiro)
    return ".".join(partes)


def num(valor: float | None, casas: int = 2) -> str:
    """Formata um número no padrão pt-BR (1.234,56). ``None`` vira 'n/d'."""
    if valor is None or (isinstance(valor, float) and (math.isnan(valor) or math.isinf(valor))):
        return "n/d"
    negativo = valor < 0 and round(abs(valor), casas) != 0
    texto = f"{abs(valor):.{casas}f}"
    if casas > 0:
        inteiro, decimal = texto.split(".")
        corpo = f"{_agrupar_milhar(inteiro)},{decimal}"
    else:
        corpo = _agrupar_milhar(texto)
    return ("-" if negativo else "") + corpo


def brl(valor: float | None, casas: int = 2) -> str:
    """Formata valor monetário em reais: ``brl(-1234.5) == '-R$ 1.234,50'``."""
    if valor is None:
        return "n/d"
    texto = num(valor, casas)
    if texto.startswith("-"):
        return "-R$ " + texto[1:]
    return "R$ " + texto


def pct(taxa: float | None, casas: int = 2) -> str:
    """Formata uma taxa decimal como percentual pt-BR: ``pct(0.1047) == '10,47%'``."""
    if taxa is None:
        return "n/d"
    return num(taxa * 100.0, casas) + "%"


def anos_meses(anos: float | None) -> str:
    """Converte prazo fracionário em anos para texto, por exemplo '2,60 anos (31,2 meses)'."""
    if anos is None:
        return "não recupera no horizonte"
    return f"{num(anos, 2)} anos ({num(anos * 12.0, 1)} meses)"


def arred(obj: Any, casas: int = 6) -> Any:
    """Arredonda recursivamente floats de dicionários e listas (para JSON estável)."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, casas)
    if isinstance(obj, dict):
        return {k: arred(v, casas) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [arred(v, casas) for v in obj]
    return obj


def ler_json(caminho: str | None) -> Any:
    """Lê JSON de um arquivo; ``'-'`` ou ``None`` lê da entrada padrão."""
    if caminho in (None, "-"):
        return json.load(sys.stdin)
    with open(caminho, "r", encoding="utf-8") as arq:
        return json.load(arq)


def tabela_md(cabecalho: list[str], linhas: Iterable[Iterable[Any]]) -> str:
    """Monta uma tabela Markdown simples a partir de cabeçalho e linhas já formatadas."""
    saida = ["| " + " | ".join(cabecalho) + " |", "|" + "|".join("---" for _ in cabecalho) + "|"]
    for linha in linhas:
        saida.append("| " + " | ".join(str(c) for c in linha) + " |")
    return "\n".join(saida)


def emitir(resultado: dict, formato: str, renderizar_md: Callable[[dict], str] | None = None) -> str:
    """Converte o resultado em texto JSON (padrão) ou Markdown (se houver renderizador)."""
    if formato == "md" and renderizar_md is not None:
        return renderizar_md(resultado)
    return json.dumps(arred(resultado), ensure_ascii=False, indent=2)


def criar_parser(descricao: str, exemplo: dict) -> argparse.ArgumentParser:
    """Cria o analisador de argumentos comum a todos os scripts."""
    parser = argparse.ArgumentParser(
        description=descricao,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exemplo de entrada (use --exemplo para imprimir):\n"
        + json.dumps(exemplo, ensure_ascii=False, indent=2),
    )
    parser.add_argument("--entrada", "-e", default=None,
                        help="arquivo JSON de entrada ('-' para ler da entrada padrão)")
    parser.add_argument("--formato", "-f", choices=["json", "md"], default="json",
                        help="formato da saída (padrão: json)")
    parser.add_argument("--saida", "-o", default=None, help="arquivo de saída (padrão: tela)")
    parser.add_argument("--exemplo", action="store_true", help="imprime um JSON de entrada de exemplo e sai")
    return parser


def _configurar_utf8() -> None:
    """Garante saída UTF-8 no console (no Windows o padrão pode ser cp1252)."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def executar_cli(descricao: str, exemplo: dict, calcular: Callable[[dict], dict],
                 renderizar_md: Callable[[dict], str] | None = None, argv: list[str] | None = None) -> int:
    """Fluxo padrão de linha de comando: lê JSON, calcula, emite JSON ou Markdown."""
    _configurar_utf8()
    parser = criar_parser(descricao, exemplo)
    args = parser.parse_args(argv)
    if args.exemplo:
        print(json.dumps(exemplo, ensure_ascii=False, indent=2))
        return 0
    if args.entrada is None and sys.stdin.isatty():
        parser.error("informe --entrada ARQUIVO.json (ou '-' para stdin); veja --exemplo")
    dados = ler_json(args.entrada)
    try:
        resultado = calcular(dados)
    except (KeyError, ValueError, TypeError) as erro:
        print(json.dumps({"erro": str(erro)}, ensure_ascii=False), file=sys.stderr)
        return 2
    texto = emitir(resultado, args.formato, renderizar_md)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8", newline="\n") as arq:
            arq.write(texto + "\n")
    else:
        print(texto)
    return 0
