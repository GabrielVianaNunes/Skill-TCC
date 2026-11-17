"""Testes de custo, preço e valor (Aula 4) e de depreciação e tributos (Aulas 6 e 8)."""

import unittest

import _caminho  # noqa: F401
import calc_custos_preco as c
import calc_depreciacao_tributos as d


class TestCustosPreco(unittest.TestCase):
    def test_taxa_horaria(self):
        # 5000 x 1,8 / 150 = 60,00
        self.assertAlmostEqual(c.taxa_horaria(5000, 0.8, 150), 60.0)

    def test_markup_e_margem(self):
        self.assertAlmostEqual(c.preco_markup(100, 0.5), 150.0)
        self.assertAlmostEqual(c.preco_margem(100, 0.2), 125.0)
        self.assertAlmostEqual(c.markup_para_margem(0.5), 1 / 3)
        self.assertAlmostEqual(c.margem_para_markup(0.2), 0.25)

    def test_markup_divisor(self):
        # 100 / (1 - 0,10 - 0,20) = 142,857
        self.assertAlmostEqual(c.preco_markup_divisor(100, 0.10, 0.20), 142.857143, places=5)
        with self.assertRaises(ValueError):
            c.preco_markup_divisor(100, 0.5, 0.6)

    def test_preco_minimo(self):
        self.assertAlmostEqual(c.preco_minimo(94, 0.06), 100.0)

    def test_calcular(self):
        r = c.calcular({"equipe": [{"papel": "Dev", "horas": 100, "taxa_hora": 60}],
                        "indiretos": [{"descricao": "Infra", "valor": 2000, "rateio": 0.25}],
                        "margem_sobre_preco": 0.2, "tributos_sobre_preco": 0.0, "valor_percebido": 13000})
        self.assertAlmostEqual(r["custo_total"], 6500.0)
        self.assertAlmostEqual(r["precos"]["margem_sobre_preco"], 8125.0)
        self.assertAlmostEqual(r["valor_percebido"]["captura_de_valor"], 0.625)


class TestDepreciacao(unittest.TestCase):
    def test_linear(self):
        self.assertEqual(d.depreciacao_linear(10000, 5), [2000.0] * 5)

    def test_linear_residual(self):
        self.assertEqual(d.depreciacao_linear(10000, 4, 2000), [2000.0] * 4)

    def test_soma_digitos(self):
        # soma = 15: 5/15, 4/15, 3/15, 2/15, 1/15 de 10000
        q = d.depreciacao_soma_digitos(10000, 5)
        esperado = [3333.3333, 2666.6667, 2000.0, 1333.3333, 666.6667]
        for a, b in zip(q, esperado):
            self.assertAlmostEqual(a, b, places=3)
        self.assertAlmostEqual(sum(q), 10000.0)

    def test_taxa_20_vida_5(self):
        self.assertEqual(d.taxa_anual_para_vida(0.20), 5)

    def test_escudo_fiscal(self):
        self.assertAlmostEqual(d.escudo_fiscal(2000, 0.34), 680.0)

    def test_fluxo_apos_impostos(self):
        # (100000 - 60000 - 2000) x 0,66 + 2000 = 27080 = 40000 x 0,66 + 680
        r = d.fluxo_apos_impostos(100000, 60000, 2000, 0.34)
        self.assertAlmostEqual(r["fluxo_caixa"], 27080.0)
        self.assertAlmostEqual(r["fluxo_caixa"], 40000 * 0.66 + 680)

    def test_simples(self):
        self.assertAlmostEqual(d.imposto_simples(100000, 0.06), 6000.0)
        # (180000 x 11,2% - 9360) / 180000 = 6,0%
        self.assertAlmostEqual(d.aliquota_efetiva_simples(180000, 0.112, 9360), 0.06, places=10)

    def test_presumido(self):
        # base 32000; IRPJ 4800; CSLL 2880; faturamento 5650 => 13330
        r = d.imposto_presumido(100000, 0.32, 0.15, 0.09, 0.0565)
        self.assertAlmostEqual(r["total"], 13330.0)


if __name__ == "__main__":
    unittest.main()
