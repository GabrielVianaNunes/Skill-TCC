"""Testes de decisão (Aulas 1, 2, 7, 10, 11 e 12): alternativas, sensibilidade, backlog e bom o suficiente."""

import unittest

import _caminho  # noqa: F401
import comparar_alternativas as ca
import priorizar_backlog as pb
import sensibilidade as s
from calc_tvm import fator_vp_serie


class TestAlternativas(unittest.TestCase):
    def test_vidas_iguais_usa_vpl(self):
        r = ca.comparar(0.10, [{"nome": "A", "fluxos": [-100, 60, 60]}, {"nome": "B", "fluxos": [-100, 0, 125]}])
        self.assertEqual(r["criterio"], "vpl")
        # A: -100 + 54,545 + 49,587 = 4,132; B: -100 + 103,306 = 3,306
        self.assertEqual(r["escolha"], "A")

    def test_vidas_diferentes_usa_caue(self):
        # Clássico: máquina X (-1000, vida 2, -100/ano) x Y (-1500, vida 3, -80/ano) a 10%
        r = ca.comparar(0.10, [{"nome": "X", "fluxos": [-1000, -100, -100]},
                               {"nome": "Y", "fluxos": [-1500, -80, -80, -80]}])
        self.assertEqual(r["criterio"], "caue")
        x = [a for a in r["alternativas"] if a["nome"] == "X"][0]
        # 1000 x 0,576190 + 100 = 676,19
        self.assertAlmostEqual(x["caue"], -676.1905, places=3)
        y = [a for a in r["alternativas"] if a["nome"] == "Y"][0]
        # 1500 x 0,402115 + 80 = 683,17 (custo anual maior)
        self.assertAlmostEqual(y["caue"], -683.1722, places=3)
        self.assertEqual(r["escolha"], "X")
        # O VPL puro escolheria X também aqui, mas com vidas diferentes só o CAUE é comparável.
        self.assertAlmostEqual(y["custo_oportunidade"], 683.1722 - 676.1905, places=3)

    def test_matriz(self):
        m = ca.matriz_decisao([{"nome": "c", "peso": 2}, {"nome": "r", "peso": 2}],
                              {"P": {"c": 8, "r": 4}, "Q": {"c": 5, "r": 6}})
        self.assertAlmostEqual(m["pontuacoes"]["P"], 6.0)
        self.assertEqual(m["vencedora"], "P")


class TestSensibilidade(unittest.TestCase):
    DADOS = {"taxa": 0.10, "investimento": 1000, "beneficios": [500, 500, 500], "custos": [100, 100, 100]}

    def test_base(self):
        # 400 x 2,486852 - 1000 = -5,259
        self.assertAlmostEqual(s.vpl_modelo(self.DADOS), -5.2592, places=3)

    def test_tornado_ordenado(self):
        t = s.tornado(self.DADOS)
        amps = [x["amplitude"] for x in t]
        self.assertEqual(amps, sorted(amps, reverse=True))
        self.assertEqual(t[0]["variavel"], "beneficios")

    def test_equilibrio_beneficios(self):
        mult = s.equilibrio_beneficios(self.DADOS)
        self.assertAlmostEqual(s.vpl_modelo(self.DADOS, {"beneficios": mult}), 0.0, places=8)

    def test_equilibrio_unidades(self):
        self.assertAlmostEqual(s.ponto_equilibrio_unidades(10000, 50, 30), 500.0)
        with self.assertRaises(ValueError):
            s.ponto_equilibrio_unidades(10000, 30, 30)


class TestBacklog(unittest.TestCase):
    def test_wsjf_e_quadrante(self):
        r = pb.priorizar({"taxa_hora": 50, "tma": 0.10, "horizonte_anos": 5, "itens": [
            {"id": "x", "titulo": "x", "valor": 8, "esforco_horas": 16, "criticidade_tempo": 5, "reducao_risco": 3,
             "valor_anual": 1000}]})
        it = r["itens"][0]
        # (8 + 5 + 3) / (16/8) = 8
        self.assertAlmostEqual(it["wsjf"], 8.0)
        self.assertEqual(it["quadrante"], "ganho rápido")
        self.assertAlmostEqual(it["vpl_item"], 1000 * fator_vp_serie(0.10, 5) - 800)

    def test_ordem_e_capacidade(self):
        r = pb.priorizar({"taxa_hora": 10, "capacidade_horas": 10, "itens": [
            {"id": "a", "titulo": "a", "valor": 9, "esforco_horas": 8, "valor_anual": 500},
            {"id": "b", "titulo": "b", "valor": 9, "esforco_horas": 3, "valor_anual": 500},
            {"id": "c", "titulo": "c", "valor": 1, "esforco_horas": 1, "valor_anual": 0}]})
        self.assertEqual(r["ranking_valor_esforco"], ["b", "a", "c"])
        dec = {i["id"]: i["decisao"] for i in r["itens"]}
        self.assertTrue(dec["b"].startswith("fazer"))
        self.assertTrue(dec["a"].startswith("próximo"))
        self.assertTrue(dec["c"].startswith("não fazer"))

    def test_bom_o_suficiente(self):
        r = pb.bom_o_suficiente([{"nome": "0", "custo": 0, "beneficio": 0},
                                 {"nome": "1", "custo": 1000, "beneficio": 2500},
                                 {"nome": "2", "custo": 2500, "beneficio": 3500},
                                 {"nome": "3", "custo": 5500, "beneficio": 4000}])
        self.assertEqual(r["nivel_escolhido"], "1")


if __name__ == "__main__":
    unittest.main()
