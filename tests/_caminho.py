"""Coloca a pasta scripts/ da skill no sys.path para os testes importarem os módulos."""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(RAIZ, ".agents", "skills", "engenharia-economica-software", "scripts")
EXEMPLOS = os.path.join(RAIZ, "examples")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
