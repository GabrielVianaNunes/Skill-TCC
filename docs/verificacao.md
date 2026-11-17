# Verificação independente de números do relatório

Três números de `examples/tcc-valuation-report.md` foram recalculados por um caminho diferente do usado pela skill: à mão, com a aritmética escrita abaixo, e conferidos com o módulo `decimal` do Python (28 dígitos), sem importar nenhum script da skill. Data da verificação: 17/11/2026.

## 1. VPL da Leitura A (cenário base) = R$ 38.596,38

TMA real: (1,1544 / 1,045) - 1 = 0,104689 (10,47% a.a.).

| Ano | Fluxo | Fator (1,104689)^t | VP |
|---|---|---|---|
| 0 | -5.640,00 | 1,000000 | -5.640,00 |
| 1 | 6.254,00 | 1,104689 | 5.661,32 |
| 2 | 13.580,00 | 1,220338 | 11.128,07 |
| 3 | 13.580,00 | 1,348094 | 10.073,48 |
| 4 | 13.580,00 | 1,489224 | 9.118,84 |
| 5 | 13.580,00 | 1,645130 | 8.254,67 |
| | | **Soma** | **38.596,38** |

Origem dos fluxos: ano 1 = 24.420,00 x 70% (rampa) - 10.840,00 = 6.254,00; anos 2 a 5 = 24.420,00 - 10.840,00 = 13.580,00. Benefício anual: 8 usuários x 4 h x 12 x R$ 45 = 17.280; 6 h x 12 x R$ 45 = 3.240; 2 OS x R$ 3.000 x 40% = 2.400; 5% x R$ 30.000 = 1.500; total 24.420. OpEx: 12 h x 12 x R$ 60 = 8.640; 2 h x 12 x R$ 60 = 1.440; infraestrutura 760; total 10.840. Investimento: (24 + 4 + 12) h x R$ 60 + (32 + 40) h x R$ 45 = 2.400 + 3.240 = 5.640.

Resultado igual ao do relatório. **Conferido.**

## 2. Payback simples da Leitura A = 0,90 ano

O acumulado fica positivo já no ano 1 (-5.640 + 6.254 = 614). Interpolação: 0 + 5.640 / 6.254 = 0,9018 ano = 10,8 meses. O relatório informa 0,90 ano (10,8 meses). **Conferido.** O payback descontado (1,00 ano) é maior, como deve ser: -5.640 + 5.661,32 = 21,32, então 5.640 / 5.661,32 = 0,9962 ano.

## 3. IDC (CPI) e IDP (SPI) finais do GVA = 0,857 e 0,849

- BAC = 200 h x R$ 60 = R$ 12.000.
- Pontos totais = 13 + 5 + 8 + 8 + 8 + 13 + 5 + 2 + 5 + 3 + 3 + 8 + 5 = 86; concluídos até 04/11 = 86 - 8 - 5 = 73.
- VA = 12.000 x 73 / 86 = R$ 10.186,05.
- VP = BAC (os 4 períodos planejados já passaram) = R$ 12.000.
- CR = horas prováveis de jul a nov (54 + 90 + 9 + 36 + 9 = 198 h) x R$ 60 = R$ 11.880.
- IDC = 10.186,05 / 11.880 = 0,8574; IDP = 10.186,05 / 12.000 = 0,8488.
- EAC = 12.000 / 0,8574 = R$ 13.995,62.

Resultados iguais aos do relatório. **Conferido.**

## Verificação adicional: TIR da Leitura B

Com a TIR informada (-12,14%), o VPL do fluxo da Leitura B calculado à mão com `decimal` dá cerca de -16 reais sobre um investimento de 93 mil (o arredondamento da taxa para quatro casas explica a diferença); com a taxa completa do JSON (-0,121444) o VPL fica a menos de R$ 1 de zero.

## Execução real dos 3 casos de avaliação no Claude Code (17/11/2026)

Cada prompt de `evals/` foi executado em modo não interativo (`claude -p`) na raiz do repositório, com permissão apenas para a skill, leitura e `python`. Em todos os casos o agente acionou a skill sozinho (sem que o prompt citasse o nome dela) e executou o script indicado.

| Caso | Script executado | Graders atendidos | Observação |
|---|---|---|---|
| `vpl-tir-payback-classico` | `calc_vpl_tir.py` | 6 de 6 | VPL R$ 388,77; TIR 24,89%; payback 2,60 e 3,05 anos; conclusão "vale a pena" |
| `gva-sprint-projecao-eac` | `calc_gva.py` | 6 de 6 | CPI 0,889; SPI 0,800; EAC R$ 1.125.000, R$ 1.050.000 e R$ 1.293.750; TCPI 1,091 |
| `tir-multipla-sem-tma` | `calc_vpl_tir.py` | 5 de 5 | Informou as duas TIRs (10% e 20%), decidiu pelo VPL e usou TMA de 15% rotulada como hipótese a substituir |

A avaliação foi feita lendo a resposta e o registro de ferramentas de cada execução contra os graders; não foi usada a comparação automática com e sem a skill.
