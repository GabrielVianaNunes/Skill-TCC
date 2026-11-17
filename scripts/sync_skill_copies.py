#!/usr/bin/env python3
"""Mantém a cópia da skill em .claude/skills/ idêntica à fonte em .agents/skills/.

A fonte única é ``.agents/skills/engenharia-economica-software`` (padrão aberto Agent Skills).
O Claude Code lê skills de projeto em ``.claude/skills/``; no Windows usamos cópia, não link
simbólico, porque links exigem privilégio e o Git nem sempre os preserva.

Uso::

    python scripts/sync_skill_copies.py           # copia a fonte para .claude/skills/
    python scripts/sync_skill_copies.py --check   # só verifica; sai com código 1 se diferir
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOME = "engenharia-economica-software"
FONTE = os.path.join(RAIZ, ".agents", "skills", NOME)
DESTINOS = [os.path.join(RAIZ, ".claude", "skills", NOME)]
IGNORAR = shutil.ignore_patterns("__pycache__", "*.pyc", "results")


def listar(base: str) -> set[str]:
    """Caminhos relativos de todos os arquivos (sem caches)."""
    arquivos = set()
    for pasta, dirs, nomes in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", "results")]
        for nome in nomes:
            if not nome.endswith(".pyc"):
                arquivos.add(os.path.relpath(os.path.join(pasta, nome), base).replace(os.sep, "/"))
    return arquivos


def diferencas(fonte: str, destino: str) -> list[str]:
    """Lista arquivos ausentes, sobrando ou com conteúdo diferente."""
    if not os.path.isdir(destino):
        return ["(cópia inexistente)"]
    a, b = listar(fonte), listar(destino)
    difs = [f"falta na cópia: {x}" for x in sorted(a - b)] + [f"sobra na cópia: {x}" for x in sorted(b - a)]
    for rel in sorted(a & b):
        if not filecmp.cmp(os.path.join(fonte, rel), os.path.join(destino, rel), shallow=False):
            difs.append(f"conteúdo diferente: {rel}")
    return difs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="apenas verifica se as cópias estão iguais")
    args = parser.parse_args()
    erro = False
    for destino in DESTINOS:
        if args.check:
            difs = diferencas(FONTE, destino)
            if difs:
                erro = True
                print(f"[DIFERENTE] {os.path.relpath(destino, RAIZ)}")
                for d in difs:
                    print("  " + d)
            else:
                print(f"[OK] {os.path.relpath(destino, RAIZ)} idêntica à fonte")
        else:
            if os.path.isdir(destino):
                shutil.rmtree(destino)
            shutil.copytree(FONTE, destino, ignore=IGNORAR)
            print(f"[COPIADO] {os.path.relpath(FONTE, RAIZ)} -> {os.path.relpath(destino, RAIZ)}")
    return 1 if erro else 0


if __name__ == "__main__":
    sys.exit(main())
