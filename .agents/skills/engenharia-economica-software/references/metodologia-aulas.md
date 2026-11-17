# Metodologia por aula (1 a 12) e checklist de revisão

Este roteiro diz o que fazer em cada tipo de análise, qual script usar e quais erros evitar. Leia a seção da aula correspondente à pergunta do usuário.

## Aulas 1 e 2: introdução e processo de decisão

Decisões de engenharia (on-premises x nuvem, refatorar x manter, terceirizar x construir, lançar funcionalidade x estabilizar) são decisões econômicas.

1. Defina o problema e o critério (maximizar VPL, minimizar custo anual, maximizar pontuação ponderada).
2. Liste alternativas mutuamente exclusivas, incluindo "não fazer nada" (manter o estado atual).
3. Estime fluxos de cada alternativa no mesmo horizonte e período.
4. Compare com `comparar_alternativas.py`; registre o custo de oportunidade (quanto se perde ao não escolher a melhor).
5. Complete com critérios não monetários na matriz ponderada (risco, aderência técnica, esforço), deixando os pesos visíveis.

Trade-off qualidade x custo: qualidade tem custo crescente e benefício decrescente; a Aula 12 mostra onde parar.

## Aulas 3 e 5: valor do dinheiro no tempo e fluxo de caixa

1. Fixe o período (mês ou ano) e converta todas as taxas para ele (`calc_tvm.py`, `taxa_equivalente`).
2. Componha a TMA: peça a taxa base ao usuário (custo de capital ou aplicação alternativa); some prêmios de risco. Mostre a conta.
3. Decida entre valores reais (preços constantes, desconto pela TMA real) e nominais (com inflação, desconto pela TMA nominal). Não misture.
4. Monte o fluxo: t = 0 com CapEx; t >= 1 com benefícios, OpEx e impostos. Separe investimento (CapEx) de operação (OpEx).

## Aula 4: custo, preço e valor em TI

1. Custos diretos: horas por papel x taxa horária com encargos.
2. Custos indiretos: infraestrutura, licenças e gestão rateados por critério explícito (horas, usuários, receita).
3. Preço por custo: markup ou markup divisor (com tributos). Preço mínimo = custo / (1 - tributos).
4. Valor percebido: quanto o cliente ganha (horas economizadas, receita, risco evitado). O preço final fica entre o piso (custo) e o teto (valor).

## Aulas 6 e 8: viabilidade, valuation, tributos e depreciação

1. Rode `calc_vpl_tir.py`: VPL, TIR (com status), TIRM, paybacks, IL, ROI.
2. Para produtos digitais, rode `metricas_produto.py`: CAC, LTV descontado, LTV/CAC, churn, payback do CAC.
3. Para ativos, rode `calc_depreciacao_tributos.py`: depreciação linear e por soma dos dígitos, efeito do regime tributário e escudo fiscal (só no Lucro Real).
4. Valuation de um sistema já construído: apresente a Leitura A (a partir de hoje, desenvolvimento como custo afundado) e a Leitura B (viabilidade total, desenvolvimento como investimento).

## Aula 7: proposta econômica de software

Estrutura (use `assets/proposta_executiva_template.md`):

1. Sumário executivo com recomendação e os indicadores-chave.
2. Justificativa de ROI em uma frase verificável.
3. Tabela de premissas com Origem e Como validar.
4. Riscos com probabilidade, impacto, variável do modelo afetada e mitigação.
5. Sensibilidade (tornado ±20%), cenários e ponto de equilíbrio (`sensibilidade.py`).

## Aula 9: Gerenciamento de Valor Agregado por sprint

1. Defina o BAC (orçamento total em R$ ou horas x taxa).
2. Para cada sprint: VP (planejado acumulado), VA (pontos concluídos / pontos totais x BAC), CR (horas reais x taxa).
3. Rode `calc_gva.py`; apresente IDC, IDP, as três EAC, ETC, VAC e TCPI, com leitura em linguagem simples.
4. Se o plano for reconstruído depois do fato, diga isso em destaque: os índices servem para aprendizado, não para auditoria.

### Estimativa de esforço pelo histórico do git (`estimar_esforco_git.py`)

Quando não há apontamento de horas:

1. Exporte commits sem merge: `git log --no-merges --reverse --format='%ad,%an' --date=format:'%Y-%m-%dT%H:%M:%S'`, troque nomes por iniciais e salve como CSV com cabeçalho `data_hora,autor`.
2. O script calcula, por mês: sessões (commits do mesmo autor com intervalo de até 3 h, mais 1 h de preparo, que é o piso observável) e dias ativos (pares autor e dia).
3. Horas do mês = max(sessões, dias ativos x horas por dia) x fator de trabalho sem commit, em três cenários (padrão 4/6/8 h por dia e fator 1,0/1,5/2,0).
4. Código importado de uma vez (primeiro commit grande) deve ser excluído do dia e estimado por produtividade em linhas por hora, com faixa.
5. Rotule como "estimativa derivada do histórico do repositório".

## Aulas 10 e 11: estratégia, legado e aposentadoria

Para cada componente problemático, compare três alternativas com `comparar_alternativas.py`:

- **Manter**: sem investimento, mas com custo anual esperado (falhas, retrabalho, risco de perda de dados).
- **Refatorar ou substituir**: investimento agora, custo anual menor.
- **Aposentar**: custo de retirada pequeno, mais o custo do processo alternativo (manual ou outro sistema).

Use o mesmo horizonte para as três; se as vidas diferirem, decida pelo CAUE.

## Aula 12: bom o suficiente e priorização de backlog

1. Para cada item: valor (1 a 10), esforço em horas, valor anual estimado em R$, criticidade no tempo e redução de risco.
2. Rode `priorizar_backlog.py`: ordena por Valor/Esforço, calcula WSJF, ICE e o VPL do item, aplica a capacidade do ciclo.
3. Itens com VPL do item <= 0 ficam fora ("bom o suficiente": o ganho marginal não paga o custo).
4. Para níveis de qualidade (cobertura de testes, desempenho, acessibilidade), informe níveis com custo e benefício acumulados e use a análise marginal (`niveis`).
5. Diga explicitamente o que não fazer agora e por quê.

## Checklist de revisão antes de entregar

- [ ] Todas as taxas no mesmo período dos fluxos.
- [ ] Taxa real com fluxo real, taxa nominal com fluxo nominal.
- [ ] TMA com composição mostrada e taxa base confirmada pelo usuário ou rotulada como hipótese.
- [ ] TIR só citada quando `status = unica`; caso contrário, VPL e TIRM.
- [ ] Payback descontado >= payback simples.
- [ ] Vidas diferentes comparadas por CAUE.
- [ ] Custo afundado fora da decisão de seguir (Leitura A).
- [ ] Depreciação fora do caixa, exceto pelo escudo fiscal no Lucro Real.
- [ ] Toda premissa com origem, faixa e forma de validação.
- [ ] Nenhuma alíquota, preço de provedor ou taxa de juros afirmada como fato atual.
- [ ] Sensibilidade feita e premissa mais sensível nomeada.
- [ ] Valores em R$ no formato pt-BR.
