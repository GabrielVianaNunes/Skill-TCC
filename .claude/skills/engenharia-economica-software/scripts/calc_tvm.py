#!/usr/bin/env python3
"""Valor do dinheiro no tempo (Aulas 3 e 5): equivalência financeira, séries e taxas.

Convenções (iguais às de references/formulas.md):

* taxas sempre em decimal (10% = 0.10) e no mesmo período de ``n``;
* juros compostos; séries postecipadas (pagamento no fim do período), salvo ``antecipada=True``;
* sinais: as funções devolvem valores positivos; o sentido do caixa é decidido por quem chama.

Uso pela linha de comando::

    python calc_tvm.py --exemplo > tvm.json
    python calc_tvm.py --entrada tvm.json --formato md

A entrada é ``{"operacoes": [{"tipo": "vf", "vp": 1000, "taxa": 0.1, "n": 3}, ...]}``.
Tipos aceitos: vf, vp, pmt, vp_serie, vf_serie, perpetuidade, taxa_equivalente,
nominal_para_efetiva, efetiva_para_nominal, taxa_real, taxa_nominal, tma, wacc, n_periodos.
"""

from __future__ import annotations

import math
import sys

from _comum import brl, executar_cli, num, pct, tabela_md


# ---------------------------------------------------------------- equivalência de capitais
def valor_futuro(vp: float, taxa: float, n: float) -> float:
    """VF = VP * (1 + i)^n."""
    return vp * (1.0 + taxa) ** n


def valor_presente(vf: float, taxa: float, n: float) -> float:
    """VP = VF / (1 + i)^n."""
    return vf / (1.0 + taxa) ** n


def fator_vp_serie(taxa: float, n: int) -> float:
    """Fator de valor presente de série uniforme postecipada: [1 - (1+i)^-n] / i."""
    if taxa == 0:
        return float(n)
    return (1.0 - (1.0 + taxa) ** (-n)) / taxa


def fator_recuperacao_capital(taxa: float, n: int) -> float:
    """Fator de recuperação de capital (A/P): i(1+i)^n / [(1+i)^n - 1]."""
    if taxa == 0:
        return 1.0 / n
    return taxa * (1.0 + taxa) ** n / ((1.0 + taxa) ** n - 1.0)


def pmt(vp: float, taxa: float, n: int, vf: float = 0.0, antecipada: bool = False) -> float:
    """Prestação uniforme (Price) que amortiza ``vp`` e deixa saldo ``vf`` ao final.

    PMT = [VP - VF/(1+i)^n] * i / [1 - (1+i)^-n]; se antecipada, divide por (1+i).
    """
    valor = (vp - valor_presente(vf, taxa, n)) / fator_vp_serie(taxa, n)
    return valor / (1.0 + taxa) if antecipada else valor


def vp_serie(parcela: float, taxa: float, n: int, antecipada: bool = False) -> float:
    """Valor presente de série uniforme: PMT * [1 - (1+i)^-n] / i (x (1+i) se antecipada)."""
    valor = parcela * fator_vp_serie(taxa, n)
    return valor * (1.0 + taxa) if antecipada else valor


def vf_serie(parcela: float, taxa: float, n: int, antecipada: bool = False) -> float:
    """Valor futuro de série uniforme: PMT * [(1+i)^n - 1] / i (x (1+i) se antecipada)."""
    valor = parcela * n if taxa == 0 else parcela * ((1.0 + taxa) ** n - 1.0) / taxa
    return valor * (1.0 + taxa) if antecipada else valor


def perpetuidade(parcela: float, taxa: float, crescimento: float = 0.0) -> float:
    """Perpetuidade (Gordon): VP = PMT / (i - g), válida só se i > g."""
    if taxa <= crescimento:
        raise ValueError("perpetuidade exige taxa maior que o crescimento (i > g)")
    return parcela / (taxa - crescimento)


def n_periodos(vp: float, vf: float, taxa: float) -> float:
    """Número de períodos para VP virar VF: n = ln(VF/VP) / ln(1+i)."""
    return math.log(vf / vp) / math.log(1.0 + taxa)


# ---------------------------------------------------------------- taxas
def taxa_equivalente(taxa: float, periodos_origem: float, periodos_destino: float) -> float:
    """Converte taxa entre períodos: i_d = (1 + i_o)^(p_d / p_o) - 1.

    Exemplo: mensal para anual usa periodos_origem=1, periodos_destino=12 (em meses).
    """
    return (1.0 + taxa) ** (periodos_destino / periodos_origem) - 1.0


def mensal_para_anual(taxa_mensal: float) -> float:
    """(1 + i_m)^12 - 1."""
    return taxa_equivalente(taxa_mensal, 1, 12)


def anual_para_mensal(taxa_anual: float) -> float:
    """(1 + i_a)^(1/12) - 1."""
    return taxa_equivalente(taxa_anual, 12, 1)


def nominal_para_efetiva(taxa_nominal: float, capitalizacoes: int) -> float:
    """Taxa nominal j capitalizada m vezes no período: i_ef = (1 + j/m)^m - 1."""
    return (1.0 + taxa_nominal / capitalizacoes) ** capitalizacoes - 1.0


def efetiva_para_nominal(taxa_efetiva: float, capitalizacoes: int) -> float:
    """Inversa: j = m * [(1 + i_ef)^(1/m) - 1]."""
    return capitalizacoes * ((1.0 + taxa_efetiva) ** (1.0 / capitalizacoes) - 1.0)


def taxa_real(taxa_nominal: float, inflacao: float) -> float:
    """Equação de Fisher: (1 + nominal) = (1 + real)(1 + inflação)."""
    return (1.0 + taxa_nominal) / (1.0 + inflacao) - 1.0


def taxa_nominal(taxa_real_: float, inflacao: float) -> float:
    """Inversa de Fisher: nominal = (1 + real)(1 + inflação) - 1."""
    return (1.0 + taxa_real_) * (1.0 + inflacao) - 1.0


def compor_tma(taxa_base: float, premios: dict[str, float] | None = None, inflacao: float | None = None,
               metodo: str = "composto") -> dict:
    """Compõe a TMA a partir de uma taxa de referência (custo de capital ou taxa livre de risco).

    Composto: TMA = (1 + base) * prod(1 + prêmio_k) - 1.  Aditivo: TMA = base + soma(prêmios).
    Se ``inflacao`` for informada, devolve também a TMA real por Fisher.
    A taxa base nunca deve ser inventada: peça a vigente ao usuário ou rotule como hipótese.
    """
    premios = premios or {}
    if metodo == "aditivo":
        tma = taxa_base + sum(premios.values())
    else:
        tma = 1.0 + taxa_base
        for valor in premios.values():
            tma *= 1.0 + valor
        tma -= 1.0
    resultado = {"taxa_base": taxa_base, "premios": premios, "metodo": metodo, "tma_nominal": tma}
    if inflacao is not None:
        resultado["inflacao"] = inflacao
        resultado["tma_real"] = taxa_real(tma, inflacao)
    resultado["tma_mensal_equivalente"] = anual_para_mensal(tma)
    return resultado


def wacc(capital_proprio: float, divida: float, custo_proprio: float, custo_divida: float,
         aliquota_ir: float = 0.0) -> float:
    """Custo médio ponderado de capital: E/(D+E) ke + D/(D+E) kd (1 - t)."""
    total = capital_proprio + divida
    return capital_proprio / total * custo_proprio + divida / total * custo_divida * (1.0 - aliquota_ir)


# ---------------------------------------------------------------- CLI
_OPERACOES = {
    "vf": lambda o: valor_futuro(o["vp"], o["taxa"], o["n"]),
    "vp": lambda o: valor_presente(o["vf"], o["taxa"], o["n"]),
    "pmt": lambda o: pmt(o["vp"], o["taxa"], int(o["n"]), o.get("vf", 0.0), o.get("antecipada", False)),
    "vp_serie": lambda o: vp_serie(o["pmt"], o["taxa"], int(o["n"]), o.get("antecipada", False)),
    "vf_serie": lambda o: vf_serie(o["pmt"], o["taxa"], int(o["n"]), o.get("antecipada", False)),
    "perpetuidade": lambda o: perpetuidade(o["pmt"], o["taxa"], o.get("crescimento", 0.0)),
    "n_periodos": lambda o: n_periodos(o["vp"], o["vf"], o["taxa"]),
    "taxa_equivalente": lambda o: taxa_equivalente(o["taxa"], o["periodos_origem"], o["periodos_destino"]),
    "nominal_para_efetiva": lambda o: nominal_para_efetiva(o["taxa"], int(o["capitalizacoes"])),
    "efetiva_para_nominal": lambda o: efetiva_para_nominal(o["taxa"], int(o["capitalizacoes"])),
    "taxa_real": lambda o: taxa_real(o["taxa_nominal"], o["inflacao"]),
    "taxa_nominal": lambda o: taxa_nominal(o["taxa_real"], o["inflacao"]),
    "tma": lambda o: compor_tma(o["taxa_base"], o.get("premios"), o.get("inflacao"), o.get("metodo", "composto")),
    "wacc": lambda o: wacc(o["capital_proprio"], o["divida"], o["custo_proprio"], o["custo_divida"],
                           o.get("aliquota_ir", 0.0)),
}
_TAXAS = {"taxa_equivalente", "nominal_para_efetiva", "efetiva_para_nominal", "taxa_real", "taxa_nominal", "wacc"}


def calcular(dados: dict) -> dict:
    """Executa a lista de operações e devolve ``{"resultados": [...]}``."""
    resultados = []
    for op in dados.get("operacoes", []):
        tipo = op.get("tipo")
        if tipo not in _OPERACOES:
            raise ValueError(f"tipo de operação desconhecido: {tipo}")
        resultados.append({"tipo": tipo, "entrada": op, "resultado": _OPERACOES[tipo](op)})
    return {"resultados": resultados}


def renderizar_md(resultado: dict) -> str:
    """Tabela Markdown com cada operação e seu resultado formatado em pt-BR."""
    linhas = []
    for r in resultado["resultados"]:
        valor = r["resultado"]
        if isinstance(valor, dict):
            texto = (f"TMA nominal {pct(valor['tma_nominal'])}"
                     + (f"; real {pct(valor['tma_real'])}" if "tma_real" in valor else "")
                     + f"; mensal equivalente {pct(valor['tma_mensal_equivalente'], 4)}")
        elif r["tipo"] in _TAXAS:
            texto = pct(valor, 4)
        elif r["tipo"] == "n_periodos":
            texto = num(valor, 4) + " períodos"
        else:
            texto = brl(valor)
        entrada = ", ".join(f"{k}={v}" for k, v in r["entrada"].items() if k != "tipo")
        linhas.append([r["tipo"], entrada, texto])
    return tabela_md(["Operação", "Entrada", "Resultado"], linhas)


EXEMPLO = {
    "operacoes": [
        {"tipo": "vf", "vp": 1000, "taxa": 0.10, "n": 3},
        {"tipo": "vp", "vf": 1331, "taxa": 0.10, "n": 3},
        {"tipo": "pmt", "vp": 10000, "taxa": 0.01, "n": 12},
        {"tipo": "taxa_equivalente", "taxa": 0.01, "periodos_origem": 1, "periodos_destino": 12},
        {"tipo": "taxa_real", "taxa_nominal": 0.1025, "inflacao": 0.05},
        {"tipo": "tma", "taxa_base": 0.11, "premios": {"risco_projeto": 0.04}, "inflacao": 0.045},
    ]
}

if __name__ == "__main__":
    sys.exit(executar_cli(__doc__.splitlines()[0], EXEMPLO, calcular, renderizar_md))
