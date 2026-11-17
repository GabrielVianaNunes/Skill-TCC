"""Testes de ponta a ponta: estimativa de esforço pelo git, formatação pt-BR e relatório do TCC."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

import _caminho
import estimar_esforco_git as eeg
import gerar_relatorio as gr
from _comum import brl, num, pct
from calc_vpl_tir import vpl


class TestFormatacao(unittest.TestCase):
    def test_brl(self):
        self.assertEqual(brl(1234.5), "R$ 1.234,50")
        self.assertEqual(brl(-1234567.891), "-R$ 1.234.567,89")
        self.assertEqual(brl(0.004), "R$ 0,00")

    def test_pct_num(self):
        self.assertEqual(pct(0.104689), "10,47%")
        self.assertEqual(num(1000000, 0), "1.000.000")


class TestEsforcoGit(unittest.TestCase):
    def test_sessoes_e_dias(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = os.path.join(tmp, "log.csv")
            with open(caminho, "w", encoding="utf-8") as arq:
                arq.write("data_hora,autor\n2026-01-10T09:00:00,A\n2026-01-10T11:00:00,A\n"
                          "2026-01-10T20:00:00,A\n2026-01-11T10:00:00,B\n")
            r = eeg.calcular({"arquivo_log": caminho, "horas_por_dia_ativo": {"min": 4, "provavel": 6, "max": 8},
                              "fator_trabalho_sem_commit": {"min": 1, "provavel": 1.5, "max": 2}})
        mes = r["meses"][0]
        # Sessões: A 9h-11h (2 + 1 = 3 h), A 20h (1 h), B 10h (1 h) = 5 h; dias ativos (autor, dia) = 2
        self.assertAlmostEqual(mes["horas_sessoes"], 5.0)
        self.assertEqual(mes["dias_ativos"], 2)
        self.assertAlmostEqual(mes["horas_min"], 8.0)        # max(5, 2 x 4) x 1
        self.assertAlmostEqual(mes["horas_provavel"], 18.0)  # max(5, 2 x 6) x 1,5
        self.assertAlmostEqual(mes["horas_max"], 32.0)       # max(5, 2 x 8) x 2

    def test_base_importada(self):
        b = eeg.estimar_base_importada(3000, {"alta": 30, "provavel": 20, "baixa": 10})
        self.assertEqual((b["horas_min"], b["horas_provavel"], b["horas_max"]), (100, 150, 300))

    def test_log_do_tcc(self):
        r = eeg.calcular({"arquivo_log": os.path.join(_caminho.EXEMPLOS, "tcc-git-log.csv")})
        # 211 commits sem merge, 25 dias distintos com commit (fatos medidos no repositório)
        self.assertEqual(r["total_commits"], 211)
        self.assertEqual(r["total_dias_ativos"], 25)


class TestRelatorioTcc(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(_caminho.EXEMPLOS, "tcc-input.json"), encoding="utf-8") as arq:
            cls.dados = json.load(arq)
        cls.dados["_arquivo_entrada"] = "examples/tcc-input.json"
        cls.r = gr.calcular(cls.dados, _caminho.EXEMPLOS)
        cls.md = gr.renderizar_md(cls.r, cls.dados)

    def test_secoes_obrigatorias(self):
        for titulo in ("## Sumário executivo", "## I. Fluxo de Caixa", "## II. VPL", "## III. TIR", "## IV. Payback",
                       "## V. Métricas de eficiência ágil via GVA", "## VI. Proposta de modelo de negócio",
                       "## 2. Premissas e hipóteses", "## Riscos e hipóteses", "Tornado"):
            self.assertIn(titulo, self.md)

    def test_vpl_coerente_com_fluxo(self):
        a = self.r["analises"]["base"]["A"]
        self.assertAlmostEqual(a["vpl"], vpl(self.r["tma_real"], self.r["modelos"]["base"]["fluxo_a"]))

    def test_leitura_b_menor_que_a(self):
        base = self.r["analises"]["base"]
        dif = base["A"]["vpl"] - base["B"]["vpl"]
        # A diferença é exatamente o custo do desenvolvimento (ocorre em t = 0)
        self.assertAlmostEqual(dif, self.r["modelos"]["base"]["desenvolvimento"]["total"], places=6)

    def test_payback_descontado_maior_ou_igual(self):
        a = self.r["analises"]["base"]["A"]
        self.assertGreaterEqual(a["payback_descontado"]["anos"], a["payback_simples"]["anos"])

    def test_equilibrio_zera_vpl(self):
        dados = json.loads(json.dumps(self.dados))
        h = self.r["equilibrio_horas_usuario_mes"]["B"]
        dados["parametros"]["horas_economizadas_usuario_mes"]["provavel"] = h
        r2 = gr.calcular(dados, _caminho.EXEMPLOS)
        self.assertAlmostEqual(r2["analises"]["base"]["B"]["vpl"], 0.0, places=4)

    def test_sem_travessao(self):
        self.assertNotIn(chr(0x2014), self.md)
        self.assertNotIn(chr(0x2013), self.md)

    def test_modelo_generico(self):
        with open(os.path.join(_caminho.SCRIPTS, "..", "assets", "modelo_entrada.json"), encoding="utf-8") as arq:
            dados = json.load(arq)
        md = gr.renderizar_md(gr.calcular(dados, ""), dados)
        self.assertIn("## IV. Payback", md)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            saida = os.path.join(tmp, "r.md")
            proc = subprocess.run([sys.executable, os.path.join(_caminho.SCRIPTS, "gerar_relatorio.py"),
                                   "--entrada", os.path.join(_caminho.EXEMPLOS, "tcc-input.json"), "--saida-md", saida],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with open(saida, encoding="utf-8") as arq:
                self.assertIn("## VI. Proposta de modelo de negócio", arq.read())

    def test_relatorio_versionado_atualizado(self):
        with open(os.path.join(_caminho.EXEMPLOS, "tcc-valuation-report.md"), encoding="utf-8") as arq:
            self.assertEqual(arq.read(), self.md, "examples/tcc-valuation-report.md está desatualizado: gere de novo")


if __name__ == "__main__":
    unittest.main()
