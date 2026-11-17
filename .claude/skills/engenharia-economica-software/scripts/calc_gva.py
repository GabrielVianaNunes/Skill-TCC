#!/usr/bin/env python3
"""Gerenciamento de Valor Agregado, GVA/EVM (Aula 9), com versão ágil por sprint.

Siglas em português (inglês): VP (PV) valor planejado, VA (EV) valor agregado, CR (AC) custo
real, ONT (BAC) orçamento no término, IDC (CPI), IDP (SPI), ENT (EAC) estimativa no término.

Fórmulas, sempre com valores acumulados até a data de status:

* VC (CV) = VA - CR;  VPr (SV) = VA - VP;  IDC = VA / CR;  IDP = VA / VP;
* EAC1 = BAC / IDC (o desempenho de custo atual continua);
* EAC2 = CR + (BAC - VA) (o restante sai conforme o orçado);
* EAC3 = CR + (BAC - VA) / (IDC * IDP) (custo e prazo influenciam o restante);
* ETC = EAC - CR;  VAC = BAC - EAC;  TCPI = (BAC - VA) / (BAC - CR) (meta: BAC) e
  TCPI_EAC = (BAC - VA) / (EAC - CR) (meta: EAC);
* prazo estimado = duração planejada / IDP (aproximação clássica).

Versão ágil (AgileEVM): VA = BAC * pontos concluídos / pontos totais da release e
VP = BAC * sprints decorridas / sprints planejadas (limitado a BAC).

Uso::

    python calc_gva.py --exemplo > gva.json
    python calc_gva.py --entrada gva.json --formato md
"""

from __future__ import annotations

import sys

from _comum import brl, executar_cli, num, tabela_md


def _div(a: float, b: float) -> float | None:
    return None if b == 0 else a / b


def indicadores(bac: float, pv: float, ev: float, ac: float) -> dict:
    """Indicadores de GVA para valores acumulados em uma data de status."""
    cpi = _div(ev, ac)
    spi = _div(ev, pv)
    eac1 = _div(bac, cpi) if cpi else None
    eac2 = ac + (bac - ev)
    eac3 = ac + (bac - ev) / (cpi * spi) if cpi and spi else None
    tcpi = _div(bac - ev, bac - ac)
    return {
        "pv": pv, "ev": ev, "ac": ac, "bac": bac,
        "cv": ev - ac, "sv": ev - pv, "cpi": cpi, "spi": spi,
        "eac_cpi": eac1, "eac_orcado": eac2, "eac_cpi_spi": eac3,
        "etc": None if eac1 is None else eac1 - ac,
        "vac": None if eac1 is None else bac - eac1,
        "tcpi_bac": tcpi if bac != ac else None,
        "tcpi_eac": _div(bac - ev, eac1 - ac) if eac1 is not None and eac1 != ac else None,
        "percentual_concluido": _div(ev, bac),
        "percentual_gasto": _div(ac, bac),
    }


def leitura(ind: dict) -> str:
    """Interpretação em linguagem simples do par IDC e IDP."""
    partes = []
    cpi, spi = ind["cpi"], ind["spi"]
    if cpi is not None:
        if cpi >= 1:
            partes.append(f"cada R$ 1,00 gasto entregou R$ {num(cpi)} de valor (custo sob controle)")
        else:
            partes.append(f"cada R$ 1,00 gasto entregou só R$ {num(cpi)} de valor (acima do orçamento)")
    if spi is not None:
        if spi >= 1:
            partes.append(f"o escopo entregue está {num((spi - 1) * 100, 1)}% à frente do planejado")
        else:
            partes.append(f"o escopo entregue está {num((1 - spi) * 100, 1)}% atrás do planejado")
    tcpi = ind.get("tcpi_bac")
    if tcpi is not None and tcpi > 1.2:
        partes.append(f"para fechar no orçamento original seria preciso eficiência {num(tcpi)} no restante, "
                      "o que é irrealista: replaneje pelo EAC")
    return "; ".join(partes) + "."


def calcular(dados: dict) -> dict:
    """Aceita períodos com pv/ev/ac (modo clássico) ou com pontos (modo ágil)."""
    bac = float(dados["bac"])
    acumulado = dados.get("acumulado", False)
    agil = "pontos_totais" in dados
    periodos = []
    pv_acc = ev_acc = ac_acc = pts_acc = 0.0
    for k, p in enumerate(dados["periodos"], start=1):
        if agil:
            pts_acc = p["pontos_concluidos"] if acumulado else pts_acc + p["pontos_concluidos"]
            ev_acc = bac * pts_acc / dados["pontos_totais"]
            pv_acc = bac * min(1.0, k / dados["sprints_planejadas"])
            ac_acc = p["ac"] if acumulado else ac_acc + p["ac"]
        elif acumulado:
            pv_acc, ev_acc, ac_acc = p["pv"], p["ev"], p["ac"]
        else:
            pv_acc += p["pv"]
            ev_acc += p["ev"]
            ac_acc += p["ac"]
        ind = indicadores(bac, pv_acc, ev_acc, ac_acc)
        if agil:
            ind["pontos_acumulados"] = pts_acc
        ind["nome"] = p.get("nome", f"P{k}")
        ind["leitura"] = leitura(ind)
        periodos.append(ind)
    final = periodos[-1]
    resultado = {"modo": "agil" if agil else "classico", "bac": bac, "periodos": periodos, "final": final}
    if "duracao_planejada" in dados and final["spi"]:
        resultado["duracao_estimada"] = dados["duracao_planejada"] / final["spi"]
    return resultado


def renderizar_md(r: dict) -> str:
    """Tabela acumulada por período e projeções da última data de status."""
    linhas = [[p["nome"], brl(p["pv"]), brl(p["ev"]), brl(p["ac"]), brl(p["cv"]), brl(p["sv"]),
               num(p["cpi"], 3), num(p["spi"], 3)] for p in r["periodos"]]
    partes = [tabela_md(["Período", "VP (PV)", "VA (EV)", "CR (AC)", "VC (CV)", "VPr (SV)", "IDC (CPI)", "IDP (SPI)"],
                        linhas), ""]
    f = r["final"]
    partes.append(tabela_md(["Projeção na última data de status", "Valor"], [
        ["BAC (orçamento no término)", brl(f["bac"])],
        ["EAC = BAC / IDC", brl(f["eac_cpi"])],
        ["EAC = CR + (BAC - VA)", brl(f["eac_orcado"])],
        ["EAC = CR + (BAC - VA) / (IDC x IDP)", brl(f["eac_cpi_spi"])],
        ["ETC = EAC - CR (base BAC/IDC)", brl(f["etc"])],
        ["VAC = BAC - EAC (base BAC/IDC)", brl(f["vac"])],
        ["TCPI para cumprir o BAC", num(f["tcpi_bac"], 3)],
        ["TCPI para cumprir o EAC", num(f["tcpi_eac"], 3)],
    ]))
    if "duracao_estimada" in r:
        partes.append(f"\nDuração estimada pelo IDP: {num(r['duracao_estimada'], 2)} períodos.")
    partes.append("\nLeitura: " + f["leitura"])
    return "\n".join(partes)


EXEMPLO = {
    "bac": 1000,
    "acumulado": True,
    "periodos": [{"nome": "Status", "pv": 500, "ev": 400, "ac": 450}],
}

if __name__ == "__main__":
    sys.exit(executar_cli(__doc__.splitlines()[0], EXEMPLO, calcular, renderizar_md))
