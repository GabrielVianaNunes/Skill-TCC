"""Testes de valor do dinheiro no tempo (Aulas 3 e 5) com resultados conferidos à mão."""

import unittest

import _caminho  # noqa: F401
import calc_tvm as t


class TestEquivalencia(unittest.TestCase):
    def test_valor_futuro(self):
        # 1000 x 1,1^3 = 1000 x 1,331 = 1331,00
        self.assertAlmostEqual(t.valor_futuro(1000, 0.10, 3), 1331.0, places=6)

    def test_valor_presente(self):
        self.assertAlmostEqual(t.valor_presente(1331, 0.10, 3), 1000.0, places=6)

    def test_pmt_price(self):
        # 10000 x 0,01 / (1 - 1,01^-12) = 888,4879
        self.assertAlmostEqual(t.pmt(10000, 0.01, 12), 888.4879, places=4)

    def test_pmt_antecipada(self):
        self.assertAlmostEqual(t.pmt(10000, 0.01, 12, antecipada=True), 888.4879 / 1.01, places=4)

    def test_vp_serie(self):
        # 100/1,1 + 100/1,21 + 100/1,331 = 248,6852
        self.assertAlmostEqual(t.vp_serie(100, 0.10, 3), 248.6852, places=4)

    def test_vf_serie(self):
        # 100 x (1,1^3 - 1) / 0,1 = 331,00
        self.assertAlmostEqual(t.vf_serie(100, 0.10, 3), 331.0, places=6)

    def test_taxa_zero(self):
        self.assertAlmostEqual(t.vp_serie(100, 0.0, 5), 500.0)
        self.assertAlmostEqual(t.pmt(1200, 0.0, 12), 100.0)

    def test_perpetuidade(self):
        self.assertAlmostEqual(t.perpetuidade(100, 0.10), 1000.0)
        self.assertAlmostEqual(t.perpetuidade(100, 0.10, 0.02), 1250.0)
        with self.assertRaises(ValueError):
            t.perpetuidade(100, 0.02, 0.05)

    def test_n_periodos(self):
        self.assertAlmostEqual(t.n_periodos(1000, 1331, 0.10), 3.0, places=9)


class TestTaxas(unittest.TestCase):
    def test_mensal_para_anual(self):
        # 1,01^12 - 1 = 12,6825%
        self.assertAlmostEqual(t.mensal_para_anual(0.01), 0.126825, places=6)

    def test_anual_para_mensal(self):
        # 1,12^(1/12) - 1 = 0,9489%
        self.assertAlmostEqual(t.anual_para_mensal(0.12), 0.009489, places=6)

    def test_ida_e_volta(self):
        self.assertAlmostEqual(t.anual_para_mensal(t.mensal_para_anual(0.015)), 0.015, places=12)

    def test_nominal_efetiva(self):
        # 12% a.a. capitalizados mensalmente = 12,6825% efetivos
        self.assertAlmostEqual(t.nominal_para_efetiva(0.12, 12), 0.126825, places=6)
        self.assertAlmostEqual(t.efetiva_para_nominal(0.126825030, 12), 0.12, places=8)

    def test_fisher(self):
        # 1,1025 / 1,05 - 1 = 5%
        self.assertAlmostEqual(t.taxa_real(0.1025, 0.05), 0.05, places=12)
        self.assertAlmostEqual(t.taxa_nominal(0.05, 0.05), 0.1025, places=12)

    def test_tma_composta(self):
        # 1,11 x 1,04 - 1 = 15,44%; 1,1544 / 1,045 - 1 = 10,4689%
        r = t.compor_tma(0.11, {"risco": 0.04}, 0.045)
        self.assertAlmostEqual(r["tma_nominal"], 0.1544, places=10)
        self.assertAlmostEqual(r["tma_real"], 0.104689, places=6)

    def test_tma_aditiva(self):
        r = t.compor_tma(0.10, {"a": 0.03, "b": 0.02}, metodo="aditivo")
        self.assertAlmostEqual(r["tma_nominal"], 0.15)

    def test_wacc(self):
        # 60% x 15% + 40% x 10% x (1 - 34%) = 9% + 2,64% = 11,64%
        self.assertAlmostEqual(t.wacc(600, 400, 0.15, 0.10, 0.34), 0.1164, places=10)


class TestCli(unittest.TestCase):
    def test_calcular_lista(self):
        r = t.calcular({"operacoes": [{"tipo": "vf", "vp": 100, "taxa": 0.1, "n": 1}]})
        self.assertAlmostEqual(r["resultados"][0]["resultado"], 110.0)

    def test_tipo_invalido(self):
        with self.assertRaises(ValueError):
            t.calcular({"operacoes": [{"tipo": "xyz"}]})


if __name__ == "__main__":
    unittest.main()
