"""Testes de VPL, TIR, TIRM, Payback, IL e CAUE (Aulas 6 e 8) com valores clássicos de livro.

Conferência manual do caso -1000, 300, 400, 500, 600 a 10%:
  300/1,1 = 272,7273; 400/1,21 = 330,5785; 500/1,331 = 375,6574; 600/1,4641 = 409,8081
  soma = 1388,7713, VPL = 388,7713
  acumulado simples: -700, -300, +200 => payback = 2 + 300/500 = 2,6
  acumulado descontado: -727,27, -396,69, -21,04, +388,77 => 3 + 21,0368/409,8080 = 3,0513
  TIRM a 10%: VF = 300 x 1,331 + 400 x 1,21 + 500 x 1,1 + 600 = 2033,3; (2,0333)^(1/4) - 1 = 19,4127%
"""

import unittest

import _caminho  # noqa: F401
import calc_vpl_tir as v

FLUXO = [-1000, 300, 400, 500, 600]


class TestVpl(unittest.TestCase):
    def test_vpl_classico(self):
        self.assertAlmostEqual(v.vpl(0.10, FLUXO), 388.7713, places=4)

    def test_vpl_taxa_zero(self):
        self.assertAlmostEqual(v.vpl(0.0, FLUXO), 800.0)

    def test_indice_lucratividade(self):
        self.assertAlmostEqual(v.indice_lucratividade(0.10, FLUXO), 1.388771, places=6)

    def test_caue(self):
        # VP 1000 a 10% em 5 anos: 1000 x 0,263797 = 263,80
        self.assertAlmostEqual(v.caue(1000, 0.10, 5), 263.7975, places=4)

    def test_roi(self):
        self.assertAlmostEqual(v.roi(1500, 1000), 0.5)
        self.assertAlmostEqual(v.roi_fluxos(FLUXO), 0.8)


class TestTir(unittest.TestCase):
    def test_tir_classica_23_38(self):
        r = v.tir([-1000, 500, 500, 500])
        self.assertEqual(r["status"], "unica")
        self.assertAlmostEqual(r["tir"], 0.233752, places=6)

    def test_tir_zera_vpl(self):
        r = v.tir(FLUXO)
        self.assertEqual(r["status"], "unica")
        self.assertAlmostEqual(r["tir"], 0.248884, places=5)
        self.assertAlmostEqual(v.vpl(r["tir"], FLUXO), 0.0, places=6)

    def test_tir_um_periodo(self):
        self.assertAlmostEqual(v.tir([-100, 110])["tir"], 0.10, places=9)

    def test_multiplas_raizes(self):
        # -100 + 230/(1+r) - 132/(1+r)^2 = 0 tem raízes 10% e 20%
        r = v.tir([-100, 230, -132])
        self.assertEqual(r["status"], "multiplas")
        self.assertIsNone(r["tir"])
        self.assertEqual(len(r["raizes"]), 2)
        self.assertAlmostEqual(r["raizes"][0], 0.10, places=7)
        self.assertAlmostEqual(r["raizes"][1], 0.20, places=7)

    def test_sem_raiz_mesmo_sinal(self):
        r = v.tir([100, 200, 300])
        self.assertEqual(r["status"], "sem_raiz")
        self.assertIsNone(r["tir"])

    def test_sem_raiz_com_troca(self):
        # -100 + 150x - 100x^2 nunca zera (discriminante negativo)
        r = v.tir([-100, 150, -100])
        self.assertEqual(r["status"], "sem_raiz")
        self.assertEqual(r["trocas_sinal"], 2)

    def test_tir_negativa(self):
        # -100 + 50x + 40x^2 = 0 => x = (-50 + raiz(18500)) / 80 = 1,075184 => r = 1/x - 1 = -6,9926%
        r = v.tir([-100, 50, 40])
        self.assertEqual(r["status"], "unica")
        self.assertAlmostEqual(r["tir"], -0.069926, places=5)

    def test_trocas_de_sinal(self):
        self.assertEqual(v.trocas_de_sinal([-1, 0, 2, -3, 4]), 3)

    def test_tirm(self):
        self.assertAlmostEqual(v.tirm(FLUXO, 0.10, 0.10), 0.194127, places=5)


class TestPayback(unittest.TestCase):
    def test_simples(self):
        r = v.payback(FLUXO)
        self.assertAlmostEqual(r["anos"], 2.6, places=10)

    def test_descontado(self):
        r = v.payback(FLUXO, 0.10)
        self.assertAlmostEqual(r["anos"], 3.051335, places=5)

    def test_descontado_maior_que_simples(self):
        self.assertGreater(v.payback(FLUXO, 0.10)["anos"], v.payback(FLUXO)["anos"])

    def test_nao_recupera(self):
        r = v.payback([-1000, 100, 100])
        self.assertIsNone(r["anos"])
        self.assertEqual(r["status"], "nao_recupera")

    def test_saldo_que_volta_a_ficar_negativo(self):
        # acumulado: -100, +20, -30, +70 => usa o último negativo (t = 2): 2 + 30/100 = 2,3
        r = v.payback([-100, 120, -50, 100])
        self.assertAlmostEqual(r["anos"], 2.3)
        self.assertTrue(r["saldo_oscilou"])


class TestAnalisar(unittest.TestCase):
    def test_pacote(self):
        r = v.analisar(0.10, FLUXO)
        self.assertEqual(r["decisao"], "viável (VPL > 0)")
        self.assertAlmostEqual(r["vpl_anualizado"], v.caue(r["vpl"], 0.10, 4))


if __name__ == "__main__":
    unittest.main()
