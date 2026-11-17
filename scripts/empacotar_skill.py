#!/usr/bin/env python3
"""Empacota a skill em ``dist/engenharia-economica-software.skill`` (ZIP) para upload no Claude.ai.

O arquivo .skill é um ZIP cuja raiz é a pasta da skill (SKILL.md, scripts/, references/, assets/).
A pasta evals/ fica de fora, porque só serve para testes.

Uso::

    python scripts/empacotar_skill.py
"""

from __future__ import annotations

import os
import sys
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOME = "engenharia-economica-software"
FONTE = os.path.join(RAIZ, ".agents", "skills", NOME)
DESTINO = os.path.join(RAIZ, "dist", NOME + ".skill")


def main() -> int:
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    total = 0
    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as zf:
        for pasta, dirs, nomes in os.walk(FONTE):
            dirs[:] = sorted(d for d in dirs if d not in ("__pycache__", "evals"))
            for nome in sorted(nomes):
                if nome.endswith(".pyc"):
                    continue
                caminho = os.path.join(pasta, nome)
                arcname = os.path.join(NOME, os.path.relpath(caminho, FONTE)).replace(os.sep, "/")
                zf.write(caminho, arcname)
                total += 1
    print(f"{total} arquivos em {os.path.relpath(DESTINO, RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
