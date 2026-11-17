---
name: engenharia-economica-software
description: Calcula e defende a viabilidade econômica e o valor de projetos de software com scripts determinísticos em Python. Cobre valor do dinheiro no tempo, TMA, fluxo de caixa com CapEx e OpEx, VPL, TIR (com detecção de múltiplas raízes), TIRM, Payback simples e descontado, CAC, LTV, churn, depreciação e tributos, custo, markup e valor percebido, GVA/EVM por sprint (CPI, SPI, EAC), sensibilidade, cenários, ponto de equilíbrio, on-premises x nuvem, legado x refatorar, priorização de backlog (Valor/Esforço, WSJF) e proposta econômica com sumário executivo. Use sempre que o usuário falar de VPL, TIR, payback, ROI, TMA, custo de software, preço, orçamento, valoração (valuation), viabilidade, business case, GVA, IDC, IDP, sprint estourando custo, priorizar backlog, vale a pena refatorar, comprar ou construir, ou pedir para "provar o valor" de um sistema, mesmo sem citar engenharia econômica.
license: MIT
compatibility: Requer Python 3.9 ou superior (somente biblioteca padrão) e permissão do harness para executar comandos Python. Funciona em qualquer harness compatível com Agent Skills.
metadata:
  autores: "Gabriel Viana Nunes; João Vítor de Alencar Fraissat Mamede"
  versao: "1.0.0"
  curso: "Engenharia de Software, Faculdade SENAI Fatesg"
  idioma: "pt-BR"
---

# Engenharia Econômica de Software

Esta skill transforma perguntas de negócio sobre software ("vale a pena?", "quanto cobrar?", "estamos no orçamento?", "o que fazer primeiro?") em números reproduzíveis e numa recomendação defensável. Os cálculos ficam nos scripts de `scripts/` porque contas feitas "de cabeça" por um modelo de linguagem erram casas decimais, confundem taxa mensal com anual e inventam TIR onde ela não existe. O seu papel é estruturar a decisão, coletar e rotular premissas, executar os scripts e explicar o resultado em linguagem clara.

## Princípios (leia antes de calcular)

1. **Número só sai de script.** Rode o script adequado e copie o resultado. Se não for possível executar Python, diga isso ao usuário, mostre a fórmula de `references/formulas.md` e deixe claro que a conta é manual.
2. **Nunca invente a taxa vigente.** Selic, CDI, inflação, custo de capital e alíquotas mudam. Peça o valor ao usuário. Se ele não souber, use uma hipótese explícita e rotulada ("hipótese: 11% a.a., substitua pela taxa vigente") e mostre a composição da TMA. Isso importa porque o VPL inteiro depende dessa taxa.
3. **Rotule a origem de cada premissa**: medido (fato verificável, como commits do git), estimado (heurística documentada), hipótese de mercado ou hipótese do grupo, sempre com faixa (mínimo, provável, máximo) e "como validar". A transparência sobre hipóteses é o que torna uma proposta econômica confiável (Aula 7).
4. **Separe custo afundado de investimento futuro.** Custo já gasto não muda a decisão de seguir em frente; ele entra só quando a pergunta é "o projeto como um todo valeu a pena?". Quando o usuário trouxer um sistema já construído, apresente as duas leituras (A: a partir de hoje; B: viabilidade total).
5. **Seja consistente com a inflação.** Fluxos em preços constantes usam taxa real; fluxos nominais usam taxa nominal (Fisher). Misturar os dois distorce o VPL.
6. **Formate em pt-BR**: R$ 1.234,56 e 12,34%. Os scripts já fazem isso com `--formato md`.

## Fluxo de trabalho

1. **Entenda a decisão.** Identifique o tipo de pergunta e as alternativas mutuamente exclusivas (inclusive "não fazer nada"). Uma decisão sem alternativas explícitas não tem custo de oportunidade calculável (Aulas 1 e 2).
2. **Colete as premissas.** Para cada número que faltar, pergunte; se o usuário preferir seguir, use hipótese rotulada. Itens típicos: TMA (ou taxa base e prêmios), horizonte, período (mês ou ano), inflação, CapEx, OpEx, horas e taxa horária, benefícios esperados.
3. **Escolha o script** pela tabela abaixo e gere a entrada JSON. Todo script aceita `--exemplo` (imprime uma entrada válida), `--entrada arquivo.json`, `--formato json|md` e `--help`.
4. **Execute** a partir da pasta da skill, por exemplo `python scripts/calc_vpl_tir.py --entrada fluxo.json --formato md`.
5. **Interprete** com as regras da seção "Como ler os resultados". Não pare no número: diga o que ele significa para a decisão.
6. **Teste a robustez**: rode `scripts/sensibilidade.py` (tornado de ±20% em TMA, benefícios, custos e investimento, cenários e ponto de equilíbrio) sempre que a recomendação depender de hipóteses.
7. **Entregue** no formato pedido. Para uma proposta executiva, use `assets/proposta_executiva_template.md` e inclua a tabela de premissas e riscos.

## Qual script usar

| Pergunta do usuário | Script | Referência |
|---|---|---|
| Equivalência VP/VF, prestação, série, perpetuidade, taxa mensal x anual, nominal x efetiva, real x nominal, compor TMA, WACC | `calc_tvm.py` | formulas.md, Aulas 3 e 5 |
| VPL, TIR, TIRM, Payback simples e descontado, IL, ROI, VPL anualizado | `calc_vpl_tir.py` | formulas.md, Aulas 6 e 8 |
| Custo direto e indireto, taxa horária com encargos, markup, margem, preço mínimo, valor percebido | `calc_custos_preco.py` | formulas.md, Aula 4 |
| Depreciação (linear, soma dos dígitos), escudo fiscal, Simples, Presumido, Lucro Real | `calc_depreciacao_tributos.py` | aliquotas.md |
| CAC, LTV, churn, LTV/CAC, payback de CAC, projeção de assinaturas | `metricas_produto.py` | formulas.md, Aula 8 |
| GVA/EVM: VP, VA, CR, IDC, IDP, três EAC, ETC, VAC, TCPI, versão ágil por pontos | `calc_gva.py` | formulas.md, Aula 9 |
| Comparar alternativas (nuvem x on-premises, manter x refatorar x aposentar, comprar x construir), CAUE, matriz de decisão | `comparar_alternativas.py` | metodologia-aulas.md, Aulas 10 e 11 |
| Priorizar backlog (Valor/Esforço, WSJF, ICE, VPL do item) e nível "bom o suficiente" | `priorizar_backlog.py` | metodologia-aulas.md, Aula 12 |
| Tornado, cenários, ponto de equilíbrio | `sensibilidade.py` | formulas.md, Aula 7 |
| Esforço em horas a partir do histórico do git | `estimar_esforco_git.py` | metodologia-aulas.md |
| Valoração completa de um sistema (todas as seções) | `gerar_relatorio.py` | esquema-entrada.md |

## Valoração completa de um sistema

Quando o usuário pedir a valoração, o business case ou a viabilidade de um sistema inteiro:

1. Copie `assets/modelo_entrada.json` e preencha com os dados do projeto. O formato está em `references/esquema-entrada.md`; leia-o só nesse caso, porque é longo.
2. Se houver repositório git e não houver apontamento de horas, exporte os commits sem merge para CSV (`data_hora,autor`, com iniciais no lugar de nomes se o repositório for público) e use `esforco.arquivo_log`. O script deriva horas por sessões e dias ativos com faixa; rotule o resultado como "estimativa derivada do histórico do repositório". Sem git, use `esforco.meses_informados`.
3. Execute `python scripts/gerar_relatorio.py --entrada projeto.json --saida-md relatorio.md --saida-json relatorio.json`.
4. Revise o relatório com o usuário: premissas com origem "hipótese" devem ser confirmadas ou mantidas conscientemente. Gere de novo após cada ajuste, sem editar números à mão, para que o relatório continue reproduzível.

O relatório traz: sumário executivo, premissas e hipóteses, esforço e custo, I Fluxo de Caixa, II VPL, III TIR, IV Payback, sensibilidade e cenários, V GVA, VI modelo de negócio (CAC, LTV, preço por markup x valor), decisões de engenharia (infraestrutura, comprar x construir, manter x refatorar x aposentar), backlog priorizado com "bom o suficiente", riscos e limitações.

## Como ler os resultados

- **VPL > 0** cria valor à TMA; entre alternativas mutuamente exclusivas de mesma vida, vence o maior VPL. Com vidas diferentes, compare o VPL anualizado (CAUE), não o VPL.
- **TIR**: o script devolve `status`. Com `unica`, compare com a TMA. Com `multiplas` (fluxo com mais de uma troca de sinal) ou `sem_raiz`, não cite uma TIR; decida pelo VPL e apresente a TIRM. Isso evita a armadilha clássica de reportar uma TIR que não significa nada.
- **Payback descontado** é sempre maior ou igual ao simples. Ambos ignoram o que vem depois da recuperação, então nunca decida só por eles.
- **IDC (CPI) < 1** significa custo acima do orçado; **IDP (SPI) < 1**, atraso. Apresente as três EAC e diga qual premissa cada uma assume. TCPI muito acima de 1 indica que o orçamento original não é mais alcançável e o certo é replanejar pelo EAC.
- **LTV/CAC** abaixo de 3 sinaliza modelo de aquisição frágil; use o LTV descontado pela TMA mensal.
- **Bom o suficiente**: pare de investir em qualidade (ou em um item de backlog) quando o benefício marginal ficar abaixo do custo marginal. Diga explicitamente o que não fazer agora.

## Armadilhas que você deve evitar

- Usar taxa anual com fluxo mensal (converta com `calc_tvm.py`, `taxa_equivalente`).
- Somar valores de datas diferentes sem descontar.
- Tratar depreciação como saída de caixa (ela só afeta o caixa pelo imposto, o escudo fiscal, e só no Lucro Real).
- Afirmar alíquota, preço de nuvem ou taxa básica de juros como fato atual. Apresente como parâmetro "a validar"; valores de referência estão em `references/aliquotas.md`.
- Apresentar estimativa como medição, ou benefício hipotético como ganho comprovado.
- Comparar alternativas sem incluir a opção de manter o estado atual.

## Formato da resposta

Responda em português do Brasil, formal e direto. Para perguntas pontuais: o número, a fórmula em uma linha, a interpretação e a premissa mais sensível. Para propostas e relatórios: siga o template de `assets/`, com tabela de premissas (colunas Origem e Como validar), tabela de riscos e recomendação clara. Sempre informe quais números são hipóteses que o usuário precisa confirmar.

## Referências (carregue só quando precisar)

- `references/formulas.md`: todas as fórmulas, por aula, com exemplos numéricos conferidos.
- `references/aliquotas.md`: tributos, encargos e depreciação como parâmetros a validar.
- `references/metodologia-aulas.md`: roteiro de cada aula (1 a 12), estimativa de esforço pelo git e checklist de revisão.
- `references/glossario.md`: siglas em português e inglês (VPL/NPV, IDC/CPI etc.).
- `references/esquema-entrada.md`: formato do JSON de `gerar_relatorio.py`.
