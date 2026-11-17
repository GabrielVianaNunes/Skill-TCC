"""Testes do validador de frontmatter (analisador YAML próprio) e da consistência do repositório."""

import os
import subprocess
import sys
import unittest

import _caminho

sys.path.insert(0, os.path.join(_caminho.RAIZ, "scripts"))
import validate_skill as vs  # noqa: E402


class TestFrontmatter(unittest.TestCase):
    def test_valido(self):
        fm, corpo = vs.analisar_frontmatter('---\nname: abc-def\ndescription: "Faz x: y"\nmetadata:\n  versao: "1"\n---\ncorpo')
        self.assertEqual(fm["name"], "abc-def")
        self.assertEqual(fm["description"], "Faz x: y")
        self.assertEqual(fm["metadata"], {"versao": "1"})
        self.assertEqual(corpo, "corpo")

    def test_sem_fechamento(self):
        with self.assertRaises(ValueError):
            vs.analisar_frontmatter("---\nname: a\n")

    def test_dois_pontos_sem_aspas(self):
        with self.assertRaises(ValueError):
            vs.analisar_frontmatter("---\nname: a\ndescription: faz x: y\n---\n")

    def test_tabulacao(self):
        with self.assertRaises(ValueError):
            vs.analisar_frontmatter("---\nmetadata:\n\tversao: 1\n---\n")

    def test_chave_duplicada(self):
        with self.assertRaises(ValueError):
            vs.analisar_frontmatter("---\nname: a\nname: b\n---\n")


class TestRepositorio(unittest.TestCase):
    def test_validador_passa(self):
        proc = subprocess.run([sys.executable, os.path.join(_caminho.RAIZ, "scripts", "validate_skill.py")],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stdout)


if __name__ == "__main__":
    unittest.main()
