# Tributos, encargos e depreciação: parâmetros a validar

**Leia isto primeiro.** Tudo neste arquivo é valor de referência para preencher parâmetros dos scripts, não afirmação sobre a regra vigente. A legislação brasileira muda com frequência e está em transição pela reforma tributária do consumo. Antes de usar qualquer número numa decisão real, confirme com um contador e com a legislação em vigor na data da análise. Nos relatórios, marque estes valores como "hipótese, validar".

## Depreciação de ativos de TI

| Ativo | Taxa anual de referência | Vida útil | Status |
|---|---|---|---|
| Computadores, notebooks e periféricos | 20% a.a. | 5 anos | validar na tabela da Receita Federal vigente |
| Servidores e equipamentos de rede | 20% a.a. | 5 anos | validar |
| Software adquirido (amortização) | 20% a.a. | 5 anos | validar; depende do contrato e da norma contábil |
| Software desenvolvido internamente | conforme vida útil estimada | | depende da capitalização como intangível (validar com contador) |

A vida fiscal (para imposto) pode diferir da vida econômica (para decisão): um servidor pode ser depreciado em 5 anos para o fisco e substituído em 4 por obsolescência. Na comparação de alternativas, use a vida econômica.

## Regimes de tributação (parâmetros de entrada)

### Simples Nacional

- Tributo calculado sobre a receita bruta com **alíquota efetiva** = (RBT12 x alíquota nominal - parcela a deduzir) / RBT12.
- Serviços de desenvolvimento e licenciamento de software costumam cair no Anexo III ou no Anexo V conforme o "fator R" (folha de 12 meses / receita de 12 meses; referência usual: 28% ou mais leva ao Anexo III). Validar.
- Valores de referência da primeira faixa, a validar: Anexo III 6%; Anexo V 15,5%.
- A depreciação não reduz o tributo (não há escudo fiscal).

Parâmetro no script: `simples_aliquota_efetiva` (padrão de exemplo 0,06).

### Lucro Presumido (serviços)

| Parâmetro | Referência | Status |
|---|---|---|
| Presunção do lucro para serviços | 32% da receita | validar |
| IRPJ | 15% da base presumida, adicional de 10% sobre a parcela que excede o limite legal | validar |
| CSLL | 9% da base presumida | validar |
| PIS (cumulativo) | 0,65% da receita | validar; em transição pela reforma |
| COFINS (cumulativa) | 3% da receita | validar; em transição pela reforma |
| ISS | 2% a 5% conforme o município | validar no município; em transição |

Carga de referência sobre a receita, com ISS de 2%: 32% x (15% + 9%) + 0,65% + 3% + 2% = 13,33%. Parâmetro no script: `presumido` com `presuncao`, `irpj`, `csll`, `tributos_faturamento`.

### Lucro Real

- IRPJ e CSLL sobre o lucro contábil ajustado; referência didática de 34% (15% + 10% de adicional + 9%), a validar.
- Só aqui a depreciação gera escudo fiscal (t x D). Parâmetro: `aliquota_ir_csll`.

### Reforma tributária do consumo

A Emenda Constitucional 132/2023 e sua regulamentação substituem gradualmente PIS, COFINS, ICMS e ISS pela CBS e pelo IBS, com período de transição que começa em 2026. Para horizontes de 5 anos, trate os tributos sobre faturamento como parâmetro de cenário e confirme as alíquotas de cada ano com um contador.

### Entidades sem fins lucrativos e uso interno

Sistemas de uso interno não geram receita tributável; os benefícios são economia de custo. Entidades imunes ou isentas (por exemplo, de educação e assistência social) podem não recolher IRPJ e CSLL. Modele `tributos_uso_interno = 0` e registre como hipótese a validar com a contabilidade da instituição.

## Encargos sobre a folha (custo da hora)

Para contratação CLT, a soma de encargos e provisões sobre o salário costuma ficar entre 70% e 100%, conforme regime tributário e benefícios. Componentes típicos, todos a validar: INSS patronal, RAT/FAP, contribuições a terceiros, FGTS (8%), 13º salário, férias com 1/3, provisões de rescisão e benefícios. No Simples Nacional parte da contribuição patronal pode estar incluída no DAS, o que reduz o percentual.

Para PJ ou freelancer, use a taxa horária contratada e acrescente custos de gestão, se houver.

Fórmula usada: taxa horária = salário x (1 + encargos) / horas produtivas (150 a 160 h por mês, descontando férias, feriados e tempo não faturável).

## Preços de infraestrutura

Preços de nuvem, domínio e armazenamento mudam por provedor, região, câmbio e promoção. Use sempre faixas e a observação "cotar no provedor na data da contratação". Camadas gratuitas dependem dos termos do provedor e podem ser alteradas; trate o risco com uma reserva de migração no OpEx.
