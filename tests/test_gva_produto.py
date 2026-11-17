"""Testes de GVA/EVM (Aula 9) e de métricas de produto digital (CAC, LTV, churn)."""

import unittest

import _caminho  # noqa: F401
import calc_gva as g
import metricas_produto as m


class TestGva(unittest.TestCase):
    def setUp(self):
        # Caso clássico: BAC 1000, VP 500, VA 400, CR 450
        self.i = g.indicadores(1000, 500, 400, 450)

    def test_variacoes(self):
        self.assertAlmostEqual(self.i["cv"], -50)
        self.assertAlmostEqual(self.i["sv"], -100)

    def test_indices(self):
        self.assertAlmostEqual(self.i["cpi"], 400 / 450)
        self.assertAlmostEqual(self.i["spi"], 0.8)

    def test_tres_eac(self):
        self.assertAlmostEqual(self.i["eac_cpi"], 1125.0)
        self.assertAlmostEqual(self.i["eac_orcado"], 1050.0)
        # 450 + 600 / (0,8889 x 0,8) = 450 + 843,75 = 1293,75
        self.assertAlmostEqual(self.i["eac_cpi_spi"], 1293.75)

    def test_etc_vac_tcpi(self):
        self.assertAlmostEqual(self.i["etc"], 675.0)
        self.assertAlmostEqual(self.i["vac"], -125.0)
        self.assertAlmostEqual(self.i["tcpi_bac"], 600 / 550)

    def test_agil(self):
        # 20 pontos, 4 sprints, BAC 1000: sprint 1 entrega 4 pontos e gasta 300
        r = g.calcular({"bac": 1000, "pontos_totais": 20, "sprints_planejadas": 4,
                        "periodos": [{"pontos_concluidos": 4, "ac": 300}, {"pontos_concluidos": 6, "ac": 200}]})
        p1, p2 = r["periodos"]
        self.assertAlmostEqual(p1["ev"], 200.0)
        self.assertAlmostEqual(p1["pv"], 250.0)
        self.assertAlmostEqual(p2["ev"], 500.0)
        self.assertAlmostEqual(p2["ac"], 500.0)
        self.assertAlmostEqual(p2["cpi"], 1.0)
        self.assertAlmostEqual(p2["spi"], 1.0)

    def test_acumulado_e_duracao(self):
        r = g.calcular({"bac": 1000, "acumulado": True, "duracao_planejada": 4,
                        "periodos": [{"pv": 500, "ev": 400, "ac": 450}]})
        self.assertAlmostEqual(r["duracao_estimada"], 5.0)


class TestProduto(unittest.TestCase):
    def test_churn_cac(self):
        self.assertAlmostEqual(m.churn(5, 100), 0.05)
        self.assertAlmostEqual(m.cac(12000, 30), 400.0)

    def test_ltv(self):
        # 100 x 0,8 / 0,05 = 1600; descontado 80 / 0,06 = 1333,33
        self.assertAlmostEqual(m.ltv(100, 0.8, 0.05), 1600.0)
        self.assertAlmostEqual(m.ltv(100, 0.8, 0.05, 0.01), 1333.3333, places=4)

    def test_ltv_descontado_igual_serie(self):
        # Confere a fórmula fechada contra a soma explícita da série
        soma = sum(80 * 0.95 ** (t - 1) / 1.01 ** t for t in range(1, 3000))
        self.assertAlmostEqual(m.ltv(100, 0.8, 0.05, 0.01), soma, places=6)

    def test_payback_cac(self):
        self.assertAlmostEqual(m.payback_cac(400, 100, 0.8), 5.0)

    def test_projecao_sem_churn(self):
        # 12 novos no ano, 1 por mês, sem churn: ativos 1..12, receita = 78 x preço
        r = m.projetar_assinaturas([12], 0.0, 10.0)
        self.assertAlmostEqual(r[0]["ativos_fim"], 12.0)
        self.assertAlmostEqual(r[0]["receita"], 780.0)


if __name__ == "__main__":
    unittest.main()
