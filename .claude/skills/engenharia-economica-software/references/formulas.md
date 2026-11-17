# Fórmulas de Engenharia Econômica aplicadas a software

Notação: i = taxa por período (decimal), n = número de períodos, t = período (0 = hoje), F_t = fluxo de caixa líquido no fim do período t, VP = valor presente, VF = valor futuro, PMT = parcela uniforme. Todas as fórmulas estão implementadas nos scripts indicados e conferidas pelos testes em `tests/` do repositório.

## Sumário

1. Valor do dinheiro no tempo (Aulas 3 e 5)
2. Taxas: equivalentes, nominais, reais e TMA (Aulas 3 e 5)
3. Fluxo de caixa: CapEx, OpEx e impostos (Aulas 5, 6 e 8)
4. Viabilidade: VPL, TIR, TIRM, Payback, IL, ROI, CAUE (Aulas 6 e 8)
5. Depreciação e escudo fiscal (Aula 8)
6. Custo, preço e valor (Aula 4)
7. Métricas de produto digital (Aula 8)
8. Proposta: sensibilidade, cenários e equilíbrio (Aula 7)
9. GVA/EVM e versão ágil (Aula 9)
10. Decisão, bom o suficiente e priorização (Aulas 1, 2, 10, 11 e 12)

## 1. Valor do dinheiro no tempo (`calc_tvm.py`)

| Conceito | Fórmula | Exemplo conferido |
|---|---|---|
| Valor futuro | VF = VP (1 + i)^n | 1.000 a 10% por 3 anos = 1.331,00 |
| Valor presente | VP = VF / (1 + i)^n | 1.331 a 10% por 3 anos = 1.000,00 |
| Número de períodos | n = ln(VF/VP) / ln(1 + i) | 1.000 para 1.331 a 10% = 3 |
| VP de série uniforme postecipada | VP = PMT [1 - (1 + i)^-n] / i | 100 a 10% em 3 = 248,69 |
| VF de série uniforme | VF = PMT [(1 + i)^n - 1] / i | 100 a 10% em 3 = 331,00 |
| Série antecipada | multiplique a postecipada por (1 + i) | |
| Prestação (Price) | PMT = VP i / [1 - (1 + i)^-n] | 10.000 a 1% a.m. em 12 = 888,49 |
| Fator de recuperação de capital | FRC = i (1 + i)^n / [(1 + i)^n - 1] | 10% em 5 = 0,263797 |
| Perpetuidade | VP = PMT / i | 100 a 10% = 1.000 |
| Perpetuidade crescente (Gordon) | VP = PMT / (i - g), com i > g | 100 a 10% e g = 2% = 1.250 |

Com i = 0, as séries viram somas simples (VP = PMT x n).

## 2. Taxas e TMA (`calc_tvm.py`)

| Conceito | Fórmula | Exemplo |
|---|---|---|
| Taxa equivalente | i_2 = (1 + i_1)^(p_2/p_1) - 1 | 1% a.m. = 12,6825% a.a. |
| Anual para mensal | i_m = (1 + i_a)^(1/12) - 1 | 12% a.a. = 0,9489% a.m. |
| Nominal para efetiva | i_ef = (1 + j/m)^m - 1 | 12% a.a. capitalizada mensalmente = 12,6825% |
| Efetiva para nominal | j = m [(1 + i_ef)^(1/m) - 1] | |
| Fisher (real) | (1 + nominal) = (1 + real)(1 + inflação) | 10,25% nominal e 5% de inflação = 5% real |
| TMA composta | TMA = (1 + taxa base) x produto(1 + prêmio_k) - 1 | 11% e prêmio 4% = 15,44% |
| TMA aditiva (aproximação) | TMA = taxa base + soma dos prêmios | |
| WACC | E/(D+E) k_e + D/(D+E) k_d (1 - t) | 60/40, 15%, 10%, t = 34% = 11,64% |

**Como derivar a TMA.** Parta de uma taxa base que o usuário informe: custo de capital da empresa (WACC), rendimento de uma aplicação sem risco equivalente (custo de oportunidade) ou taxa exigida pela diretoria. Some prêmios por risco do projeto (tecnologia nova, mercado incerto) e por liquidez. Nunca afirme o valor vigente de Selic ou CDI: peça ao usuário ou rotule como hipótese. Se os fluxos estão em preços constantes, desconte pela TMA real (Fisher).

## 3. Fluxo de caixa de projeto de software

F_t = Receitas ou benefícios_t - OpEx_t - CapEx_t - Impostos_t + Valor residual_n

- **CapEx** (investimento): desenvolvimento ou aquisição de software, hardware, implantação, migração de dados, treinamento inicial.
- **OpEx** (operação): hospedagem, licenças recorrentes, suporte, manutenção corretiva e evolutiva, administração.
- **Benefícios** de sistemas internos: horas economizadas x custo da hora, retrabalho evitado, receita preservada (pela margem, não pela receita bruta), risco evitado (probabilidade x impacto, valor esperado).
- **Custo afundado** não entra na decisão de seguir em frente (Leitura A); entra apenas na avaliação do projeto como um todo (Leitura B).
- **Rampa de adoção**: multiplique os benefícios do primeiro ano pela fração de uso esperada.

## 4. Viabilidade (`calc_vpl_tir.py`)

| Indicador | Fórmula | Regra |
|---|---|---|
| VPL | VPL = soma de t = 0 a n de F_t / (1 + i)^t | aceitar se VPL > 0 |
| TIR | taxa que faz VPL = 0 | aceitar se TIR > TMA, só se a TIR for única |
| TIRM | [VF das entradas à taxa de reinvestimento / VP das saídas à taxa de financiamento]^(1/n) - 1 | aceitar se TIRM > TMA |
| Payback simples | k + abs(acumulado_k) / F_(k+1), k = último período com acumulado negativo | menor é melhor; ignora o depois |
| Payback descontado | igual, com F_t / (1 + i)^t | sempre maior ou igual ao simples |
| Índice de lucratividade | IL = VP(F_1 ... F_n) / abs(F_0) = 1 + VPL / abs(F_0) | aceitar se IL > 1 |
| ROI | (ganho - custo) / custo | descontado: (VP entradas - VP saídas) / VP saídas |
| VPL anualizado (CAUE com sinal) | VPL x FRC(i, n) | compara vidas diferentes |

**Exemplo conferido** (-1.000; 300; 400; 500; 600 a 10%): VP dos fluxos 272,73; 330,58; 375,66; 409,81; VPL = 388,77; TIR = 24,89%; TIRM = 19,41%; payback simples = 2 + 300/500 = 2,60; payback descontado = 3 + 21,04/409,81 = 3,05; IL = 1,3888.

**TIR clássica:** -1.000; 500; 500; 500 dá 23,38%.

**Robustez da TIR.** Pela regra de sinais de Descartes, o número de TIRs positivas é no máximo o número de trocas de sinal do fluxo. O script varre o VPL entre -99% e 1000% por período, isola cada mudança de sinal e refina por bissecção (tolerância 1e-12). Resultado:

- `unica`: uma raiz;
- `multiplas`: por exemplo -100; 230; -132 tem TIRs de 10% e 20% (resolva -132x² + 230x - 100 = 0 com x = 1/(1+r)); decida pelo VPL;
- `sem_raiz`: fluxos de mesmo sinal, ou polinômio sem raiz real (por exemplo -100; 150; -100).

## 5. Depreciação e escudo fiscal (`calc_depreciacao_tributos.py`)

| Método | Fórmula | Exemplo (10.000, 5 anos, residual 0) |
|---|---|---|
| Linear | D = (custo - residual) / vida | 2.000 por ano |
| Soma dos dígitos | D_t = (custo - residual) (vida - t + 1) / [vida (vida + 1) / 2] | 3.333,33; 2.666,67; 2.000; 1.333,33; 666,67 |

Fluxo após impostos (Lucro Real): FC = (R - C - D)(1 - t) + D = (R - C)(1 - t) + t D. O termo t D é o **escudo fiscal**: 2.000 de depreciação com t = 34% economiza 680 de imposto. No Simples Nacional e no Lucro Presumido o tributo incide sobre a receita (ou receita presumida), então a depreciação não gera escudo. A taxa fiscal usual para computadores é 20% a.a. (vida de 5 anos), a validar (ver `aliquotas.md`).

## 6. Custo, preço e valor (`calc_custos_preco.py`)

| Conceito | Fórmula |
|---|---|
| Taxa horária com encargos | salário mensal x (1 + encargos) / horas produtivas no mês |
| Custo direto | soma(horas x taxa horária) |
| Custo indireto | soma(recurso compartilhado x fração de rateio) |
| Preço por markup sobre custo | P = C (1 + markup) |
| Preço por margem sobre preço | P = C / (1 - margem) |
| Markup divisor (com tributos e despesas) | P = C / (1 - tributos - despesas - margem) |
| Preço mínimo | P_min = C / (1 - tributos) |
| Conversões | margem = markup / (1 + markup); markup = margem / (1 - margem) |
| Captura de valor | preço / valor percebido |

O custo define o piso; o valor percebido pelo cliente (benefício que ele obtém) define o teto. Precificar por valor captura parte do benefício do cliente; precificar por markup ignora quanto o cliente ganha.

## 7. Métricas de produto digital (`metricas_produto.py`)

| Métrica | Fórmula |
|---|---|
| Churn | clientes perdidos no período / clientes no início |
| Vida média | 1 / churn |
| CAC | gasto de marketing e vendas / novos clientes |
| LTV simples | ARPA x margem bruta / churn |
| LTV descontado | ARPA x margem / (i + churn), i = TMA mensal |
| LTV/CAC | referência usual: 3 ou mais |
| Payback do CAC | CAC / (ARPA x margem), em meses |
| Projeção | ativos_m = ativos_(m-1) (1 - churn) + novos_m |

Exemplo: ARPA 100, margem 80%, churn 5%, i = 1% a.m., CAC 400: LTV simples 1.600; LTV descontado 1.333,33; LTV/CAC 3,33; payback do CAC 5 meses.

## 8. Sensibilidade, cenários e equilíbrio (`sensibilidade.py`)

- **Tornado**: varie uma variável por vez (TMA, benefícios, custos, investimento) em ±20% e ordene pela amplitude do VPL. As barras maiores mostram onde validar primeiro.
- **Cenários**: pessimista (benefícios no mínimo, custos no máximo), base (provável) e otimista. Combinar todos os extremos é um teste de estresse de probabilidade conjunta baixa.
- **Equilíbrio econômico**: multiplicador dos benefícios que zera o VPL, m* = [VP(custos) + investimento] / VP(benefícios). Como o VPL é linear em cada fator, o valor de equilíbrio de um parâmetro x é x* = x_0 - VPL / (dVPL/dx).
- **Equilíbrio contábil**: Q* = custos fixos / (preço - custo variável unitário). Exemplo: 10.000 / (50 - 30) = 500 unidades.

## 9. GVA/EVM (`calc_gva.py`)

| Sigla PT (EN) | Fórmula | Leitura |
|---|---|---|
| VP (PV) | custo orçado do trabalho planejado até a data | |
| VA (EV) | custo orçado do trabalho realizado | |
| CR (AC) | custo real do trabalho realizado | |
| VC (CV) | VA - CR | negativo: acima do custo |
| VPr (SV) | VA - VP | negativo: atrasado |
| IDC (CPI) | VA / CR | < 1: ineficiência de custo |
| IDP (SPI) | VA / VP | < 1: atraso |
| EAC 1 | BAC / IDC | desempenho de custo atual continua |
| EAC 2 | CR + (BAC - VA) | restante sai conforme orçado |
| EAC 3 | CR + (BAC - VA) / (IDC x IDP) | custo e prazo afetam o restante |
| ETC | EAC - CR | quanto falta gastar |
| VAC | BAC - EAC | estouro (negativo) ou sobra |
| TCPI | (BAC - VA) / (BAC - CR) | eficiência necessária para cumprir o BAC |
| Prazo estimado | duração planejada / IDP | aproximação |

Exemplo conferido (BAC 1.000; VP 500; VA 400; CR 450): CV -50; SV -100; IDC 0,889; IDP 0,800; EAC 1.125,00 / 1.050,00 / 1.293,75; ETC 675; VAC -125; TCPI 1,091.

**Versão ágil (AgileEVM):** VA = BAC x pontos concluídos / pontos totais da release; VP = BAC x sprints decorridas / sprints planejadas; CR = horas reais x taxa.

## 10. Decisão, bom o suficiente e priorização

- **Alternativas mutuamente exclusivas, vidas iguais**: maior VPL.
- **Vidas diferentes**: maior VPL anualizado (CAUE), que equivale a repetir as alternativas até o MMC das vidas. Exemplo: X (-1.000; -100/ano; 2 anos) tem custo anual 676,19 e Y (-1.500; -80/ano; 3 anos) tem 683,17 a 10%, logo X.
- **Custo de oportunidade** da escolha k = indicador da melhor - indicador de k.
- **Matriz de decisão ponderada**: pontuação = soma(peso_c x nota_c), pesos normalizados.
- **Valor/Esforço**: valor (1 a 10) / horas; quadrantes: ganho rápido (alto valor, baixo esforço), projeto estratégico, preenchimento, evitar.
- **WSJF** = (valor de negócio + criticidade no tempo + redução de risco) / tamanho.
- **ICE** = impacto x confiança x facilidade.
- **VPL do item** = valor anual x [1 - (1 + i)^-n] / i - horas x taxa.
- **Custo de atraso** mensal = valor anual / 12; CD3 = custo de atraso / duração.
- **Bom o suficiente**: avance para o próximo nível de qualidade só enquanto benefício marginal >= custo marginal.
