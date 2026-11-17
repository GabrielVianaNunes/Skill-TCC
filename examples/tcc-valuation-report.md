# Valoração econômica do ZEISS PILOT

**Autores:** Gabriel Viana Nunes e João Vítor de Alencar Fraissat Mamede  
**Curso:** Engenharia de Software, Faculdade SENAI Fatesg  
**Componente curricular:** Engenharia Econômica. **Docente:** Msc. Ujeverson Tavares Sampaio  
**Data-base:** 17/11/2026. **Moeda:** BRL, valores reais (preços constantes de novembro de 2026), fluxos anuais.  
**Gerado por:** skill `engenharia-economica-software` (`scripts/gerar_relatorio.py`), a partir de `examples/tcc-input.json`. Os números são reproduzíveis executando o mesmo comando.

## Sumário executivo

**Projeto:** ZEISS PILOT. Sistema web de gestão e rastreabilidade do Centro de Excelência em Metrologia (CEM) do SENAI Zeiss, em Goiânia (GO).

**Situação:** Sistema funcionalmente completo, ainda não implantado em produção. Não existe medição de ganho em uso real.

**Recomendação:** implantar o sistema em produção (Leitura A com VPL de R$ 38.596,38 e payback descontado de 1,00 anos (12,0 meses)). Como investimento total (Leitura B), o uso interno isolado não recupera o custo econômico do desenvolvimento em 5 anos (VPL -R$ 49.240,95); a recuperação depende de ampliar o uso ou de um modelo de negócio externo (seção VI).

| Indicador | Leitura A: ativo a partir de hoje | Leitura B: viabilidade total |
|---|---|---|
| O que entra no investimento inicial | implantação (desenvolvimento tratado como custo afundado) | implantação + custo econômico do desenvolvimento |
| Investimento inicial | R$ 5.640,00 | R$ 93.477,34 |
| VPL à TMA real de 10,47% | R$ 38.596,38 | -R$ 49.240,95 |
| TIR real | 158,98% | -12,14% |
| TIRM (reinvestimento à TMA) | 66,78% | -4,88% |
| Payback simples | 0,90 anos (10,8 meses) | não recupera no horizonte |
| Payback descontado | 1,00 anos (12,0 meses) | não recupera no horizonte |
| Índice de lucratividade | 7,84 | 0,47 |
| VPL pessimista / otimista | -R$ 90.302,79 / R$ 236.530,39 | -R$ 278.224,52 / R$ 190.546,89 |

**Justificativa de ROI.** O benefício anual em regime é de R$ 24.420,00 contra OpEx de R$ 10.840,00, um ganho líquido de R$ 13.580,00 por ano. Sobre o investimento de implantação de R$ 5.640,00, o ROI descontado em 5 anos é 684,33%. Para a Leitura B zerar o VPL seriam necessárias 7,3 h economizadas por usuário/mês (hipótese base: 4,0 h); para a Leitura A bastam 1,4 h.

**Eficiência da execução (GVA).** Na última data de status (Nov/2026 (até 04/11)), IDC (CPI) = 0,857 e IDP (SPI) = 0,849: cada R$ 1,00 gasto entregou só R$ 0,86 de valor (acima do orçamento); o escopo entregue está 15,1% atrás do planejado; para fechar no orçamento original seria preciso eficiência 15,12 no restante, o que é irrealista: replaneje pelo EAC. EAC (BAC/IDC) = R$ 13.995,62 para um BAC reconstruído de R$ 12.000,00.

**Modelo de negócio.** Uso interno institucional: VPL R$ 38.596,38; SaaS multi-laboratório: VPL -R$ 22.808,68; Implantação e suporte (instância por laboratório): VPL R$ 3.190,30. Vencedora na matriz ponderada: Uso interno institucional.

**Hipóteses que mais pesam.** custo da hora da equipe do laboratório, horas economizadas por usuário, número de usuários, horas de manutenção, taxa horária de desenvolvimento e TMA. Todas aparecem com faixa e forma de validação.

**Próximos passos.** (1) confirmar a TMA vigente e a taxa horária com a instituição; (2) colocar em produção e medir horas economizadas por 3 meses; (3) executar os itens 'fazer neste ciclo' do backlog; (4) só avaliar a oferta externa depois de formalizar o acordo de licença.

> Transparência: todos os números de benefício e de preço são hipóteses rotuladas na tabela de premissas, com faixa e forma de validação. Nenhum ganho foi medido em produção. O esforço é estimativa derivada do histórico do repositório, não apontamento de horas.

## 1. Contexto e fatos medidos

Sistema web de gestão e rastreabilidade do Centro de Excelência em Metrologia (CEM) do SENAI Zeiss, em Goiânia (GO). Sistema funcionalmente completo, ainda não implantado em produção. Não existe medição de ganho em uso real.

| Fato | Valor (medido no repositório) |
|---|---|
| Stack | Java 21, Spring Boot 3.5, PostgreSQL 16, Thymeleaf e JavaScript sem framework, Docker e CI |
| Entidades de domínio | 22 |
| Endpoints REST | 101 |
| Perfis de acesso | 4 |
| Métodos de teste automatizado | 340 |
| Idiomas da interface | 3 (português, inglês e alemão) |
| Commits em main (25/05/2026 a 04/11/2026) | 222 (211 sem merge); Gabriel 174, João 48 |
| Commits por mês | mai 1, jun 5, jul 53, ago 117, set 4, out 29, nov 13 |
| Dias distintos com commit (sem merge) | 25 |
| Linhas de código atuais (aprox.) | Java 9,8 mil (produção) e 6,3 mil (teste); JavaScript 12,6 mil; CSS 9,2 mil; templates 8,4 mil; SQL 1,3 mil |
| Base importada no primeiro commit (25/05/2026) | 36.722 linhas (JS 13.380, CSS 9.118, HTML 7.411, Java 6.804, outros 9) |
| Registro formal de sprint | Somente a Sprint 5: 6 issues (#13 a #18) fechadas em 20/10/2026, prazo do marco 05/11/2026 |

## 2. Premissas e hipóteses

Cada linha diz de onde o número vem. **Origem** usa quatro rótulos: *medido no git* (fato verificável), *estimado* (derivado por heurística documentada), *hipótese de mercado* (valor típico a cotar) e *hipótese do grupo* (julgamento dos autores). Nenhuma hipótese foi apresentada como medição.

| Premissa | Base (provável) | Mínimo | Máximo | Origem | Como validar |
|---|---|---|---|---|---|
| Taxa de referência (base da TMA) | 11,00% |  |  | hipótese do grupo | Substituir pela taxa vigente (por exemplo, Selic ou custo de capital da instituição) informada pelo usuário |
| Prêmios de risco | risco_do_projeto: 4,00% |  |  | hipótese do grupo | Discutir com a gestão o risco aceito para projetos internos |
| Inflação anual esperada | 4,50% |  |  | hipótese de mercado | Usar a expectativa de mercado vigente (boletim Focus) |
| TMA nominal composta | 15,44% | 12,00% | 20,00% | estimado | (1 + base) x (1 + prêmio) - 1 |
| TMA real (Fisher), usada no desconto | 10,47% |  |  | estimado | (1 + nominal) / (1 + inflação) - 1 |
| Horizonte | 5 anos |  |  | hipótese do grupo | Vida útil esperada antes de reescrita relevante |
| Rampa de adoção | 70%, 100%, 100%, 100%, 100% |  |  | hipótese do grupo | Medir uso real no 1º ano |
| Tributos no uso interno | 0,00% |  |  | hipótese do grupo | Uso institucional sem receita tributável; validar o enquadramento da instituição com a contabilidade |
| Custo da hora de desenvolvimento com encargos (R$/h) | 60,00 | 48,00 | 84,00 | hipótese de mercado | Pesquisa salarial de desenvolvedor júnior e pleno em Goiânia; conferir encargos com contador |
| Custo médio da hora da equipe do laboratório (técnicos e estagiários) com encargos (R$/h) | 45,00 | 35,00 | 60,00 | hipótese do grupo | Pedir ao CEM a folha média por cargo (dado agregado, sem nomes) |
| Usuários internos ativos do sistema (usuários) | 8,00 | 5,00 | 12,00 | hipótese do grupo | Contar as contas ativas após 3 meses de produção |
| Horas de controle manual evitadas (OS, amostras, documentos, condições ambientais, almoxarifado, relatórios) (h/usuário/mês) | 4,00 | 2,00 | 6,00 | hipótese do grupo | Cronometrar as rotinas antes e depois da implantação durante 1 mês |
| Retrabalho evitado por dados validados e rastreáveis (h/mês) | 6,00 | 3,00 | 10,00 | hipótese do grupo | Registrar ocorrências de correção de cadastro e relatório por 3 meses |
| Ordens de serviço que deixariam de ser perdidas por melhor acompanhamento do pipeline comercial (OS/ano) | 2,00 | 0,00 | 4,00 | hipótese do grupo | Comparar a taxa de conversão do pipeline antes e depois (12 meses) |
| Ticket médio de uma OS de metrologia (R$) | 3.000,00 | 1.500,00 | 5.000,00 | hipótese de mercado | Usar o ticket médio real dos relatórios do próprio sistema após a implantação |
| Margem de contribuição da receita preservada (fração) | 40,00% | 30,00% | 50,00% | hipótese do grupo | Validar com a gestão financeira do CEM |
| Redução anual da probabilidade de não conformidade relevante de rastreabilidade em auditoria ISO/IEC 17025 (probabilidade/ano) | 5,00% | 2,00% | 10,00% | hipótese do grupo | Histórico de constatações de auditoria do laboratório |
| Custo de uma não conformidade relevante (reauditoria, retrabalho e serviços suspensos) (R$) | 30.000,00 | 15.000,00 | 50.000,00 | hipótese do grupo | Estimar com a qualidade do CEM |
| Manutenção corretiva, adaptativa e evolutiva (h/mês) | 12,00 | 6,00 | 20,00 | estimado | Apontar horas de manutenção nos 6 primeiros meses de produção |
| Administração da infraestrutura (atualizações, conferência de backup) (h/mês) | 2,00 | 1,00 | 4,00 | estimado | Apontar horas de operação |
| Infraestrutura em nuvem: domínio, armazenamento de backup e reserva para eventual migração da camada gratuita (R$/ano) | 760,00 | 160,00 | 3.400,00 | hipótese de mercado | Cotar no provedor na data da contratação; preços não são oficiais |
| Esforço registrado no git (h) | 216 | 112 | 384 | estimado (medido no git + heurística) | Comparar com registros das sprints, se existirem |
| Esforço da base importada (h) | 1.224 | 816 | 1.836 | estimado | Produtividade de 20 a 45 linhas/h; confrontar com o cronograma das Sprints 1 a 4 |

Derivação da taxa horária: salário mensal x (1 + 80% de encargos) / 150 h produtivas: R$ 4.000 (júnior) = 48; R$ 5.000 = 60; R$ 7.000 (pleno) = 84.

Composição da TMA: TMA nominal = (1 + 11,00%) x (1 + 4,00%) - 1 = 15,44%; TMA real = (1 + 15,44%) / (1 + 4,50%) - 1 = 10,47% a.a. (equivalente a 0,8332% a.m.). Como todos os fluxos estão em preços constantes, o desconto usa a taxa real (consistência de Fisher).

## 3. Esforço e custo de desenvolvimento

**Estimativa derivada do histórico do repositório.** Não há apontamento de horas; o esforço foi reconstruído dos commits sem merge. O commit de importação de 25/05/2026 (código anterior ao repositório) entra como base importada, não como trabalho do dia. Heurística: horas do mês = max(horas em sessões, dias ativos x horas por dia) x fator de trabalho sem commit; horas por dia ativo de 4/6/8 (mínimo/provável/máximo), fator de trabalho sem commit de 1,0/1,5/2,0, sessão = commits com intervalo de até 3 h + 1 h de preparo.

| Mês | Commits | Dias ativos | Horas em sessões (piso) | Mínimo (h) | Provável (h) | Máximo (h) |
|---|---|---|---|---|---|---|
| 2026-06 | 5 | 2 | 2,3 | 8,0 | 18,0 | 32,0 |
| 2026-07 | 53 | 6 | 20,3 | 24,0 | 54,0 | 96,0 |
| 2026-08 | 117 | 10 | 56,1 | 56,1 | 90,0 | 160,0 |
| 2026-09 | 3 | 1 | 4,0 | 4,0 | 9,0 | 16,0 |
| 2026-10 | 23 | 4 | 6,3 | 16,0 | 36,0 | 64,0 |
| 2026-11 | 9 | 1 | 1,3 | 4,0 | 9,0 | 16,0 |
| **Total** | 210 | 24 | 90,2 | 112,1 | 216,0 | 384,0 |

Rótulo: estimativa derivada do histórico do repositório (não é medição de horas).

Base importada: 36.722 linhas a 45, 30 e 20 linhas/h resultam em 816 h (mínimo), 1.224 h (provável) e 1.836 h (máximo).

| Cenário | Horas totais | Taxa horária | Custo direto | Custo indireto (rateio) | Custo econômico do desenvolvimento |
|---|---|---|---|---|---|
| pessimista | 2.220 | R$ 84,00 | R$ 186.488,40 | R$ 1.433,34 | R$ 187.921,73 |
| base | 1.440 | R$ 60,00 | R$ 86.404,00 | R$ 1.433,34 | R$ 87.837,34 |
| otimista | 928 | R$ 48,00 | R$ 44.550,16 | R$ 1.433,34 | R$ 45.983,49 |

O custo de desenvolvimento é **econômico** (custo de oportunidade das horas a preço de mercado), não um desembolso: o trabalho foi acadêmico. Por isso ele aparece só na Leitura B.

**Depreciação de ativos de TI.** A taxa fiscal usual para computadores e periféricos no Brasil é 20% a.a. (vida de 5 anos), a conferir na regra vigente com um contador (ver `references/aliquotas.md`).

**Notebook de desenvolvimento (cada)** (custo R$ 5.000,00, vida 5 anos)

| Ano | Linear | Soma dos dígitos |
|---|---|---|
| 1 | R$ 1.000,00 | R$ 1.666,67 |
| 2 | R$ 1.000,00 | R$ 1.333,33 |
| 3 | R$ 1.000,00 | R$ 1.000,00 |
| 4 | R$ 1.000,00 | R$ 666,67 |
| 5 | R$ 1.000,00 | R$ 333,33 |

**Servidor on-premises (alternativa de infraestrutura)** (custo R$ 12.000,00, vida 5 anos)

| Ano | Linear | Soma dos dígitos |
|---|---|---|
| 1 | R$ 2.400,00 | R$ 4.000,00 |
| 2 | R$ 2.400,00 | R$ 3.200,00 |
| 3 | R$ 2.400,00 | R$ 2.400,00 |
| 4 | R$ 2.400,00 | R$ 1.600,00 |
| 5 | R$ 2.400,00 | R$ 800,00 |


**Implantação (investimento da Leitura A, cenário base):**

| Item | Horas | Valor |
|---|---|---|
| Provisionar VM, domínio, TLS e backup externo; primeiro deploy | 24 | R$ 1.440,00 |
| Ajustes de produto prioritários antes da produção (itens a e f do backlog) | 4 | R$ 240,00 |
| Treinamento: preparação e condução pelos desenvolvedores | 12 | R$ 720,00 |
| Treinamento: horas dos usuários (4 h por usuário) | 32 | R$ 1.440,00 |
| Carga inicial de cadastros pela equipe do laboratório | 40 | R$ 1.800,00 |
| **Total** |  | **R$ 5.640,00** |

## I. Fluxo de Caixa

Fluxos anuais em valores reais, t = 0 na implantação, cenário base. Benefícios do ano 1 multiplicados pela rampa de adoção.

### Leitura A: valoração do ativo a partir de hoje (desenvolvimento como custo afundado)

| Linha | Ano 0 | Ano 1 | Ano 2 | Ano 3 | Ano 4 | Ano 5 |
|---|---|---|---|---|---|---|
| (+) Horas de controle manual economizadas | R$ 0,00 | R$ 12.096,00 | R$ 17.280,00 | R$ 17.280,00 | R$ 17.280,00 | R$ 17.280,00 |
| (+) Retrabalho evitado | R$ 0,00 | R$ 2.268,00 | R$ 3.240,00 | R$ 3.240,00 | R$ 3.240,00 | R$ 3.240,00 |
| (+) Margem de OS preservadas no pipeline comercial | R$ 0,00 | R$ 1.680,00 | R$ 2.400,00 | R$ 2.400,00 | R$ 2.400,00 | R$ 2.400,00 |
| (+) Risco de não conformidade 17025 evitado (valor esperado) | R$ 0,00 | R$ 1.050,00 | R$ 1.500,00 | R$ 1.500,00 | R$ 1.500,00 | R$ 1.500,00 |
| (-) Manutenção corretiva e evolutiva | R$ 0,00 | -R$ 8.640,00 | -R$ 8.640,00 | -R$ 8.640,00 | -R$ 8.640,00 | -R$ 8.640,00 |
| (-) Administração da infraestrutura | R$ 0,00 | -R$ 1.440,00 | -R$ 1.440,00 | -R$ 1.440,00 | -R$ 1.440,00 | -R$ 1.440,00 |
| (-) Infraestrutura em nuvem (domínio, backup, reserva) | R$ 0,00 | -R$ 760,00 | -R$ 760,00 | -R$ 760,00 | -R$ 760,00 | -R$ 760,00 |
| (-) Investimento (CapEx e implantação) | -R$ 5.640,00 | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 0,00 |
| **Fluxo líquido** | **-R$ 5.640,00** | **R$ 6.254,00** | **R$ 13.580,00** | **R$ 13.580,00** | **R$ 13.580,00** | **R$ 13.580,00** |
| Acumulado simples | -R$ 5.640,00 | R$ 614,00 | R$ 14.194,00 | R$ 27.774,00 | R$ 41.354,00 | R$ 54.934,00 |
| VP do fluxo | -R$ 5.640,00 | R$ 5.661,32 | R$ 11.128,07 | R$ 10.073,48 | R$ 9.118,84 | R$ 8.254,67 |
| Acumulado descontado | -R$ 5.640,00 | R$ 21,32 | R$ 11.149,39 | R$ 21.222,87 | R$ 30.341,71 | R$ 38.596,38 |

### Leitura B: viabilidade total (desenvolvimento como investimento inicial)

| Linha | Ano 0 | Ano 1 | Ano 2 | Ano 3 | Ano 4 | Ano 5 |
|---|---|---|---|---|---|---|
| (+) Horas de controle manual economizadas | R$ 0,00 | R$ 12.096,00 | R$ 17.280,00 | R$ 17.280,00 | R$ 17.280,00 | R$ 17.280,00 |
| (+) Retrabalho evitado | R$ 0,00 | R$ 2.268,00 | R$ 3.240,00 | R$ 3.240,00 | R$ 3.240,00 | R$ 3.240,00 |
| (+) Margem de OS preservadas no pipeline comercial | R$ 0,00 | R$ 1.680,00 | R$ 2.400,00 | R$ 2.400,00 | R$ 2.400,00 | R$ 2.400,00 |
| (+) Risco de não conformidade 17025 evitado (valor esperado) | R$ 0,00 | R$ 1.050,00 | R$ 1.500,00 | R$ 1.500,00 | R$ 1.500,00 | R$ 1.500,00 |
| (-) Manutenção corretiva e evolutiva | R$ 0,00 | -R$ 8.640,00 | -R$ 8.640,00 | -R$ 8.640,00 | -R$ 8.640,00 | -R$ 8.640,00 |
| (-) Administração da infraestrutura | R$ 0,00 | -R$ 1.440,00 | -R$ 1.440,00 | -R$ 1.440,00 | -R$ 1.440,00 | -R$ 1.440,00 |
| (-) Infraestrutura em nuvem (domínio, backup, reserva) | R$ 0,00 | -R$ 760,00 | -R$ 760,00 | -R$ 760,00 | -R$ 760,00 | -R$ 760,00 |
| (-) Investimento (CapEx e implantação + desenvolvimento) | -R$ 93.477,34 | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 0,00 |
| **Fluxo líquido** | **-R$ 93.477,34** | **R$ 6.254,00** | **R$ 13.580,00** | **R$ 13.580,00** | **R$ 13.580,00** | **R$ 13.580,00** |
| Acumulado simples | -R$ 93.477,34 | -R$ 87.223,34 | -R$ 73.643,34 | -R$ 60.063,34 | -R$ 46.483,34 | -R$ 32.903,34 |
| VP do fluxo | -R$ 93.477,34 | R$ 5.661,32 | R$ 11.128,07 | R$ 10.073,48 | R$ 9.118,84 | R$ 8.254,67 |
| Acumulado descontado | -R$ 93.477,34 | -R$ 87.816,01 | -R$ 76.687,95 | -R$ 66.614,46 | -R$ 57.495,62 | -R$ 49.240,95 |

## II. VPL (Valor Presente Líquido)

VPL = soma de F_t / (1 + i)^t, com i = TMA real de 10,47% a.a.

| Cenário | VPL Leitura A | Decisão A | VPL Leitura B | Decisão B |
|---|---|---|---|---|
| pessimista | -R$ 90.302,79 | inviável (VPL < 0) | -R$ 278.224,52 | inviável (VPL < 0) |
| base | R$ 38.596,38 | viável (VPL > 0) | -R$ 49.240,95 | inviável (VPL < 0) |
| otimista | R$ 236.530,39 | viável (VPL > 0) | R$ 190.546,89 | viável (VPL > 0) |

Os cenários pessimista e otimista combinam todos os extremos ao mesmo tempo (teste de estresse); a probabilidade conjunta é baixa, por isso a decisão se apoia no cenário base, na sensibilidade e no ponto de equilíbrio.

| TMA nominal | TMA real | VPL A | VPL B |
|---|---|---|---|
| 12,00% | 7,18% | R$ 42.942,32 | -R$ 44.895,01 |
| 20,00% | 14,83% | R$ 33.683,62 | -R$ 54.153,71 |

VPL anualizado (benefício anual uniforme equivalente) do cenário base: A = R$ 10.303,88/ano; B = -R$ 13.145,61/ano.

## III. TIR (Taxa Interna de Retorno)

A TIR é obtida por varredura de -99% a 1000% e bissecção, com contagem de trocas de sinal; quando não existe ou não é única, o script informa o status em vez de um número.

| Cenário | Leitura | Status | TIR real | TIRM | Trocas de sinal | Comparação |
|---|---|---|---|---|---|---|
| pessimista | A | sem_raiz | inexistente (sem troca de sinal) | n/d | 0 | decidir pelo VPL |
| pessimista | B | sem_raiz | inexistente (sem troca de sinal) | n/d | 0 | decidir pelo VPL |
| base | A | unica | 158,98% | 66,78% | 1 | supera a TMA |
| base | B | unica | -12,14% | -4,88% | 1 | abaixo da TMA |
| otimista | A | unica | 993,34% | 139,91% | 1 | supera a TMA |
| otimista | B | unica | 110,81% | 50,78% | 1 | supera a TMA |

TIR nominal equivalente (Fisher) no cenário base, Leitura A: 170,63%.

## IV. Payback

Interpolação linear dentro do ano: payback = k + |acumulado_k| / fluxo_(k+1), onde k é o último ano com saldo negativo.

| Cenário | Leitura | Payback simples | Payback descontado | Índice de lucratividade | ROI descontado |
|---|---|---|---|---|---|
| pessimista | A | não recupera no horizonte | não recupera no horizonte | -11,975 | -100,00% |
| pessimista | B | não recupera no horizonte | não recupera no horizonte | -0,428 | -100,00% |
| base | A | 0,90 anos (10,8 meses) | 1,00 anos (12,0 meses) | 7,843 | 684,33% |
| base | B | não recupera no horizonte | não recupera no horizonte | 0,473 | -52,68% |
| otimista | A | 0,10 anos (1,3 meses) | 0,12 anos (1,4 meses) | 48,306 | 4.730,61% |
| otimista | B | 1,05 anos (12,6 meses) | 1,14 anos (13,6 meses) | 4,737 | 373,74% |

O payback descontado é sempre maior ou igual ao simples, porque cada entrada futura vale menos hoje.

## Sensibilidade, cenários e ponto de equilíbrio

### Tornado da Leitura A (±20%, uma variável por vez)

VPL base: R$ 38.596,38

| Variável | VPL com -20% | VPL com +20% | Amplitude |
|---|---|---|---|
| Benefícios / receitas | R$ 21.628,19 | R$ 55.564,58 | R$ 33.936,39 |
| Custos operacionais (OpEx) | R$ 46.717,30 | R$ 30.475,46 | R$ 16.241,84 |
| TMA | R$ 41.289,28 | R$ 36.129,73 | R$ 5.159,55 |
| Investimento inicial | R$ 39.724,38 | R$ 37.468,38 | R$ 2.256,00 |

Os benefícios podem cair até 45,49% antes de o VPL zerar (multiplicador de equilíbrio 0,5451).

### Tornado da Leitura B (±20%, uma variável por vez)

VPL base: -R$ 49.240,95

| Variável | VPL com -20% | VPL com +20% | Amplitude |
|---|---|---|---|
| Investimento inicial | -R$ 30.545,49 | -R$ 67.936,42 | R$ 37.390,93 |
| Benefícios / receitas | -R$ 66.209,15 | -R$ 32.272,76 | R$ 33.936,39 |
| Custos operacionais (OpEx) | -R$ 41.120,03 | -R$ 57.361,87 | R$ 16.241,84 |
| TMA | -R$ 46.548,05 | -R$ 51.707,61 | R$ 5.159,55 |

Os benefícios precisam subir 58,04% para o VPL zerar (multiplicador de equilíbrio 1,5804).

| Cenário | Investimento A | Investimento B | Benefício anual em regime | OpEx anual |
|---|---|---|---|---|
| pessimista | R$ 6.960,00 | R$ 194.881,73 | R$ 5.760,00 | R$ 27.592,00 |
| base | R$ 5.640,00 | R$ 93.477,34 | R$ 24.420,00 | R$ 10.840,00 |
| otimista | R$ 5.000,00 | R$ 50.983,49 | R$ 74.040,00 | R$ 4.192,00 |

**Ponto de equilíbrio em horas economizadas:** mantidos os demais parâmetros do cenário base, o VPL da Leitura A zera com 1,43 h por usuário/mês e o da Leitura B com 7,28 h por usuário/mês (hipótese base: 4,0 h).

## V. Métricas de eficiência ágil via GVA (EVM)

**Reconstrução retrospectiva, sem medição contemporânea.** Só a Sprint 5 tem registro formal no repositório (issues #13 a #18); os meses de jul a out/2026 são tratados como 4 períodos planejados. O plano de referência (VP) foi reconstruído: Plano de referência reconstruído: 2 desenvolvedores x cerca de 6 h/semana x 17 semanas (jul a out/2026), arredondado para 200 h. BAC = 200 h x R$ 60,00 = R$ 12.000,00, distribuído uniformemente em 4 períodos. O VA usa pontos de história atribuídos retrospectivamente aos pacotes entregues (86 pontos no total), com o mês de conclusão tirado do git. O CR usa as horas prováveis da seção 3 x taxa horária base.

| Pacote | Pontos | Concluído em |
|---|---|---|
| P1: Infraestrutura de base: versionamento de esquema, suíte de testes, backup, Docker e CI | 13 | 2026-07 |
| P2: Papéis de acesso e endurecimento inicial | 5 | 2026-07 |
| P3: Internacionalização completa e tema acessível (WCAG AA) | 8 | 2026-08 |
| P4: Conformidade com padrões institucionais, criptografia de dados pessoais e auditoria | 8 | 2026-08 |
| P5: Módulo de clientes, catálogo de serviços e notificações | 8 | 2026-08 |
| P6: Normalização e validação de todos os campos (6 fases) | 13 | 2026-08 |
| P7: Dashboard de receita por cliente e vínculo de campos | 5 | 2026-08 |
| P8: Estabilização do CI e documentação | 2 | 2026-09 |
| P9: Melhorias de eventos, indicadores, dados de demonstração e hierarquia de acesso | 5 | 2026-10 |
| P10: Sprint 5 (issues #13 a #18) | 3 | 2026-10 |
| P11: Refinamento de interface e acessibilidade | 3 | 2026-11 |
| P12: Implantação em produção (VM, domínio, backup externo, treinamento) | 8 | pendente |
| P13: Conclusão de fluxos pendentes (registro de máquina, anexo de termo de amostra) | 5 | pendente |

| Período | VP (PV) | VA (EV) | CR (AC) | VC (CV) | VPr (SV) | IDC (CPI) | IDP (SPI) |
|---|---|---|---|---|---|---|---|
| Jul/2026 | R$ 3.000,00 | R$ 2.511,63 | R$ 3.240,00 | -R$ 728,37 | -R$ 488,37 | 0,775 | 0,837 |
| Ago/2026 | R$ 6.000,00 | R$ 8.372,09 | R$ 8.640,00 | -R$ 267,91 | R$ 2.372,09 | 0,969 | 1,395 |
| Set/2026 | R$ 9.000,00 | R$ 8.651,16 | R$ 9.180,00 | -R$ 528,84 | -R$ 348,84 | 0,942 | 0,961 |
| Out/2026 (inclui Sprint 5) | R$ 12.000,00 | R$ 9.767,44 | R$ 11.340,00 | -R$ 1.572,56 | -R$ 2.232,56 | 0,861 | 0,814 |
| Nov/2026 (até 04/11) | R$ 12.000,00 | R$ 10.186,05 | R$ 11.880,00 | -R$ 1.693,95 | -R$ 1.813,95 | 0,857 | 0,849 |

| Projeção na última data de status | Valor |
|---|---|
| BAC (orçamento no término) | R$ 12.000,00 |
| EAC = BAC / IDC | R$ 13.995,62 |
| EAC = CR + (BAC - VA) | R$ 13.693,95 |
| EAC = CR + (BAC - VA) / (IDC x IDP) | R$ 14.372,37 |
| ETC = EAC - CR (base BAC/IDC) | R$ 2.115,62 |
| VAC = BAC - EAC (base BAC/IDC) | -R$ 1.995,62 |
| TCPI para cumprir o BAC | 15,116 |
| TCPI para cumprir o EAC | 0,857 |

Duração estimada pelo IDP: 4,71 períodos.

Leitura: cada R$ 1,00 gasto entregou só R$ 0,86 de valor (acima do orçamento); o escopo entregue está 15,1% atrás do planejado; para fechar no orçamento original seria preciso eficiência 15,12 no restante, o que é irrealista: replaneje pelo EAC.

Leitura por período: Jul/2026: cada R$ 1,00 gasto entregou só R$ 0,78 de valor (acima do orçamento); o escopo entregue está 16,3% atrás do planejado. Ago/2026: cada R$ 1,00 gasto entregou só R$ 0,97 de valor (acima do orçamento); o escopo entregue está 39,5% à frente do planejado. Set/2026: cada R$ 1,00 gasto entregou só R$ 0,94 de valor (acima do orçamento); o escopo entregue está 3,9% atrás do planejado. Out/2026 (inclui Sprint 5): cada R$ 1,00 gasto entregou só R$ 0,86 de valor (acima do orçamento); o escopo entregue está 18,6% atrás do planejado; para fechar no orçamento original seria preciso eficiência 3,38 no restante, o que é irrealista: replaneje pelo EAC. Nov/2026 (até 04/11): cada R$ 1,00 gasto entregou só R$ 0,86 de valor (acima do orçamento); o escopo entregue está 15,1% atrás do planejado; para fechar no orçamento original seria preciso eficiência 15,12 no restante, o que é irrealista: replaneje pelo EAC.

## VI. Proposta de modelo de negócio

O repositório do sistema tem licença proprietária com uso acadêmico pelo SENAI FATESG; qualquer exploração comercial exige acordo prévio com a instituição. Multi-tenancy não foi implementado por decisão registrada; a opção SaaS exige esse investimento (CapEx).

As opções externas são avaliadas à TMA real de negócio de 19,31% a.a. (TMA real + prêmio de risco de novo negócio), equivalente a 1,482% a.m. O uso interno usa a TMA institucional.

### Precificação: markup sobre custo x valor percebido (opção SaaS)

| Referência de preço mensal por laboratório | Valor |
|---|---|
| Custo variável por cliente (infra + suporte) | R$ 240,00 |
| Custo total por cliente com rateio do fixo | R$ 365,42 |
| Preço mínimo (cobre custo e tributos) | R$ 388,74 |
| Preço por markup divisor (tributos 6,00% + margem 30,00%) | R$ 570,96 |
| Valor percebido (benefício base de um laboratório / 12) | R$ 2.035,00 |
| Preço por captura de valor | R$ 712,25 |
| **Preço adotado na projeção** | **R$ 700,00** |
| Margem bruta por cliente após tributos | 59,71% |

### Métricas de produto digital

SaaS multi-laboratório:

| Métrica | Valor |
|---|---|
| Churn mensal | 1,50% |
| Vida média do cliente | 66,7 meses |
| CAC | R$ 3.000,00 |
| LTV simples | R$ 27.866,67 |
| LTV descontado (i = 1,482% a.m.) | R$ 14.017,84 |
| LTV/CAC | 4,67 |
| Payback do CAC | 7,2 meses |
| Leitura | relação saudável (LTV/CAC >= 3) |

| Ano | Novos | Perdidos | Ativos no fim | Receita |
|---|---|---|---|---|
| 1 | 1,0 | 0,08 | 0,92 | R$ 4.308,89 |
| 2 | 2,0 | 0,31 | 2,61 | R$ 15.643,57 |
| 3 | 3,0 | 0,67 | 4,94 | R$ 32.838,71 |
| 4 | 3,0 | 1,06 | 6,89 | R$ 50.613,34 |
| 5 | 3,0 | 1,38 | 8,51 | R$ 65.439,73 |

Implantação e suporte (contrato de suporte como recorrência):

| Métrica | Valor |
|---|---|
| Churn mensal | 1,00% |
| Vida média do cliente | 100,0 meses |
| CAC | R$ 3.000,00 |
| LTV simples | R$ 24.300,00 |
| LTV descontado (i = 1,482% a.m.) | R$ 9.790,83 |
| LTV/CAC | 3,26 |
| Payback do CAC | 12,3 meses |
| Leitura | relação saudável (LTV/CAC >= 3) |

### Fluxo da opção SaaS multi-laboratório

CapEx inicial: R$ 17.400,00 (Multi-tenancy (200 h) e adaptação para cobrança e isolamento (40 h) + acordo de licença com a instituição (R$ 3.000)).

| Ano | Receita | Tributos | Custos variáveis | Custos fixos | Aquisição (CAC) | Fluxo líquido | Clientes no fim |
|---|---|---|---|---|---|---|---|
| 1 | R$ 4.308,89 | -R$ 258,53 | -R$ 1.477,33 | -R$ 12.040,00 | -R$ 3.000,00 | -R$ 12.466,98 | 0,92 |
| 2 | R$ 15.643,57 | -R$ 938,61 | -R$ 5.363,51 | -R$ 12.040,00 | -R$ 6.000,00 | -R$ 8.698,55 | 2,61 |
| 3 | R$ 32.838,71 | -R$ 1.970,32 | -R$ 11.258,99 | -R$ 12.040,00 | -R$ 9.000,00 | -R$ 1.430,60 | 4,94 |
| 4 | R$ 50.613,34 | -R$ 3.036,80 | -R$ 17.353,15 | -R$ 12.040,00 | -R$ 9.000,00 | R$ 9.183,39 | 6,89 |
| 5 | R$ 65.439,73 | -R$ 3.926,38 | -R$ 22.436,48 | -R$ 12.040,00 | -R$ 9.000,00 | R$ 18.036,87 | 8,51 |

### Fluxo da opção Implantação e suporte (instância por laboratório)

CapEx inicial: R$ 5.400,00 (Empacotamento, manual de implantação (40 h) + acordo de licença (R$ 3.000)).

| Ano | Receita | Tributos | Custos variáveis | Custos fixos | Aquisição (CAC) | Fluxo líquido | Clientes no fim |
|---|---|---|---|---|---|---|---|
| 1 | R$ 10.820,38 | -R$ 649,22 | -R$ 4.728,15 | -R$ 5.760,00 | -R$ 3.000,00 | -R$ 3.316,99 | 0,95 |
| 2 | R$ 15.612,63 | -R$ 936,76 | -R$ 6.645,05 | -R$ 5.760,00 | -R$ 3.000,00 | -R$ 729,18 | 1,79 |
| 3 | R$ 30.680,78 | -R$ 1.840,85 | -R$ 13.072,31 | -R$ 5.760,00 | -R$ 6.000,00 | R$ 4.007,62 | 3,48 |
| 4 | R$ 39.238,18 | -R$ 2.354,29 | -R$ 16.495,27 | -R$ 5.760,00 | -R$ 6.000,00 | R$ 8.628,62 | 4,98 |
| 5 | R$ 46.823,34 | -R$ 2.809,40 | -R$ 19.529,33 | -R$ 5.760,00 | -R$ 6.000,00 | R$ 12.724,60 | 6,30 |

### Comparação das opções

| Opção | Taxa | VPL | TIR | Payback descontado | IL |
|---|---|---|---|---|---|
| Uso interno institucional | 10,47% | R$ 38.596,38 | 158,98% | 1,00 anos (12,0 meses) | 7,84 |
| SaaS multi-laboratório | 19,31% | -R$ 22.808,68 | -9,68% | não recupera no horizonte | -0,31 |
| Implantação e suporte (instância por laboratório) | 19,31% | R$ 3.190,30 | 29,54% | 4,39 anos (52,7 meses) | 1,59 |

| Opção | VPL (peso 0,35) | risco (peso 0,25) | aderência às decisões técnicas (peso 0,20) | dependência de acordo de licença (peso 0,10) | esforço da equipe (peso 0,10) | Pontuação |
|---|---|---|---|---|---|---|
| Uso interno institucional | 10,0 | 8,0 | 10,0 | 10,0 | 8,0 | 9,30 |
| SaaS multi-laboratório | 0,0 | 3,0 | 2,0 | 3,0 | 3,0 | 1,75 |
| Implantação e suporte (instância por laboratório) | 4,2 | 6,0 | 9,0 | 4,0 | 6,0 | 5,78 |

Nota de VPL normalizada de 0 a 10 entre as opções; demais notas são julgamento do grupo. **Recomendação:** Uso interno institucional.

### Tributos e escudo fiscal (opção SaaS, ano 5, parâmetros a validar)

Amortização anual do CapEx a 20% a.a.: R$ 3.480,00. No Simples Nacional e no Lucro Presumido a base é a receita, então não há escudo fiscal; no Lucro Real o escudo é t x D.

| Regime | Tributos | Fluxo de caixa | Escudo fiscal |
|---|---|---|---|
| Lucro real | R$ 6.284,31 | R$ 15.678,95 | R$ 1.183,20 |
| Simples Nacional | R$ 3.926,38 | R$ 18.036,87 | R$ 0,00 |
| Lucro Presumido (carga 13,33%) | R$ 8.723,12 | R$ 13.240,13 | R$ 0,00 |

## Decisões de engenharia como decisões econômicas

### Infraestrutura: on-premises x nuvem

Custos de 5 anos (valores reais) de hospedar o sistema; benefícios iguais nas três opções. Vidas diferentes, logo a comparação usa o VPL anualizado (CAUE).

| Alternativa | Vida | VPL | VPL anualizado (CAUE) | TIR | Custo de oportunidade |
|---|---|---|---|---|---|
| Nuvem com camada gratuita (plano do projeto) | 5 | -R$ 8.720,78 | -R$ 2.328,14 | não se aplica (fluxo só de custos) | R$ 0,00 |
| VM paga pequena em nuvem | 5 | -R$ 13.215,76 | -R$ 3.528,14 | não se aplica (fluxo só de custos) | R$ 1.200,00 |
| Servidor on-premises no laboratório | 4 | -R$ 22.122,83 | -R$ 7.050,08 | não se aplica (fluxo só de custos) | R$ 4.721,93 |

Escolha econômica: **Nuvem com camada gratuita (plano do projeto)** (vidas diferentes: maior VPL anualizado (CAUE)).

| Alternativa | custo (peso 0,40) | risco operacional (peso 0,30) | aderência institucional (peso 0,20) | esforço de operação (peso 0,10) | Pontuação |
|---|---|---|---|---|---|
| Nuvem com camada gratuita (plano do projeto) | 9,0 | 5,0 | 5,0 | 7,0 | 6,80 |
| VM paga pequena em nuvem | 7,0 | 7,0 | 6,0 | 7,0 | 6,80 |
| Servidor on-premises no laboratório | 4,0 | 6,0 | 8,0 | 4,0 | 5,40 |

Vencedora na matriz ponderada: **VM paga pequena em nuvem**.

| Opção | Premissas |
|---|---|
| Nuvem com camada gratuita (plano do projeto) | VM sem custo sujeita aos termos do provedor; 8 h de configuração; domínio, backup, reserva de migração e 2 h/mês de administração |
| VM paga pequena em nuvem | VM de 2 vCPU e 4 GB por cerca de R$ 150/mês (hipótese), domínio, backup e 2 h/mês de administração |
| Servidor on-premises no laboratório | Servidor de R$ 12.000 (vida econômica de 4 anos; a vida fiscal é de 5 anos, 20% a.a.), 16 h de configuração, energia e rateio, 3 h/mês de administração |

### Construir x comprar: sistema próprio x LIMS de mercado

Usar o sistema próprio já construído ou licenciar um sistema de gestão laboratorial (LIMS) de mercado com escopo comparável. Custo afundado do desenvolvimento excluído (decisão a partir de hoje). Valores do LIMS são hipótese do grupo para um produto genérico de mercado, sem citar fornecedor; cotar antes de decidir.

| Alternativa | Vida | VPL | VPL anualizado (CAUE) | TIR | Custo de oportunidade |
|---|---|---|---|---|---|
| Sistema próprio (implantar e manter) | 5 | -R$ 46.244,59 | -R$ 12.345,68 | não se aplica (fluxo só de custos) | R$ 0,00 |
| LIMS de mercado (licenciar) | 5 | -R$ 67.179,68 | -R$ 17.934,62 | não se aplica (fluxo só de custos) | R$ 20.935,09 |

Escolha econômica: **Sistema próprio (implantar e manter)** (vidas iguais: maior VPL).

### Manter, refatorar ou aposentar componentes

**Cadastro de scanners 3D (dados mantidos apenas no navegador)**

| Alternativa | Vida | VPL | VPL anualizado (CAUE) | TIR | Custo de oportunidade |
|---|---|---|---|---|---|
| Manter como está | 5 | -R$ 2.247,49 | -R$ 600,00 | não se aplica (fluxo só de custos) | R$ 943,74 |
| Refatorar: persistir no servidor | 5 | -R$ 1.440,00 | -R$ 384,43 | não se aplica (fluxo só de custos) | R$ 136,26 |
| Aposentar: retirar a tela e controlar em planilha | 5 | -R$ 1.303,74 | -R$ 348,05 | não se aplica (fluxo só de custos) | R$ 0,00 |

Escolha econômica: **Aposentar: retirar a tela e controlar em planilha** (vidas iguais: maior VPL).

| Opção | Premissa |
|---|---|
| Manter como está | valor esperado de perda ou divergência de registros (hipótese) |
| Refatorar: persistir no servidor | 24 h de desenvolvimento; elimina a perda |
| Aposentar: retirar a tela e controlar em planilha | 3 h para retirar; controle manual estimado |

**Anexo de termo de recebimento de amostra (fluxo incompleto)**

| Alternativa | Vida | VPL | VPL anualizado (CAUE) | TIR | Custo de oportunidade |
|---|---|---|---|---|---|
| Manter como está | 5 | -R$ 1.498,32 | -R$ 400,00 | não se aplica (fluxo só de custos) | R$ 629,16 |
| Refatorar: concluir o fluxo de upload | 5 | -R$ 960,00 | -R$ 256,29 | não se aplica (fluxo só de custos) | R$ 90,84 |
| Aposentar: ocultar o recurso e manter termo em papel | 5 | -R$ 869,16 | -R$ 232,04 | não se aplica (fluxo só de custos) | R$ 0,00 |

Escolha econômica: **Aposentar: ocultar o recurso e manter termo em papel** (vidas iguais: maior VPL).

| Opção | Premissa |
|---|---|
| Manter como está | confusão de uso e arquivamento paralelo (hipótese) |
| Refatorar: concluir o fluxo de upload | 16 h, reaproveitando o padrão de documentos de máquina |
| Aposentar: ocultar o recurso e manter termo em papel | 2 h; arquivamento manual |

## Priorização do backlog (Valor x Esforço) e princípio bom o suficiente

Valor de 1 a 10 e horas estimadas pelo grupo; custo a R$ 60,00/h; VPL do item = valor anual x 3,7458 (fator de série a 10,47% em 5 anos) - custo. Capacidade do próximo ciclo: 80 h.

| # | Id | Item | Valor | Horas | Valor/Esforço | Quadrante | WSJF | ICE | VPL do item | Decisão |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | a | Aprimorar o gerenciamento de sessão de usuário | 8 | 2 | 4,000 | ganho rápido | 96,00 | 630 | R$ 5.498,72 | fazer neste ciclo |
| 2 | f | Preservar a data de criação ao editar ordem de serviço | 7 | 2 | 3,500 | ganho rápido | 76,00 | 551 | R$ 4.374,97 | fazer neste ciclo |
| 3 | d | Calcular a conformidade ambiental no servidor a partir das faixas de referência | 7 | 6 | 1,167 | ganho rápido | 26,67 | 379 | R$ 5.258,72 | fazer neste ciclo |
| 4 | c | Concluir o registro de ligar e desligar máquina de ponta a ponta | 5 | 8 | 0,625 | preenchimento | 12,00 | 250 | R$ 2.216,98 | fazer neste ciclo |
| 5 | l | Documentar a API com OpenAPI | 3 | 6 | 0,500 | preenchimento | 8,00 | 162 | R$ 763,74 | fazer neste ciclo |
| 6 | e | Máquina de estados da ordem de serviço com validação de transições | 6 | 12 | 0,500 | ganho rápido | 10,67 | 232 | R$ 2.651,23 | fazer neste ciclo |
| 7 | i | Provisionar VM, domínio e backup externo e colocar em produção | 10 | 24 | 0,417 | projeto estratégico | 9,33 | 384 | R$ 49.428,11 | fazer neste ciclo |
| 8 | k | Testes de interface ponta a ponta dos 5 fluxos críticos | 5 | 16 | 0,312 | preenchimento | 7,50 | 175 | R$ 3.534,97 | fazer neste ciclo |
| 9 | b | Persistir o cadastro de scanners 3D no servidor | 4 | 24 | 0,167 | evitar | 3,67 | 120 | R$ 807,49 | próximo ciclo (VPL positivo, sem capacidade agora) |
| 10 | h | Geração de relatórios PDF no servidor | 4 | 40 | 0,100 | evitar | 1,80 | 80 | R$ 971,23 | próximo ciclo (VPL positivo, sem capacidade agora) |
| 11 | g | Módulo de calibração com certificados e incerteza de medição | 8 | 120 | 0,067 | projeto estratégico | 1,33 | 55 | R$ 15.274,87 | próximo ciclo (VPL positivo, sem capacidade agora) |
| 12 | j | Multi-tenancy para oferta SaaS | 3 | 200 | 0,015 | evitar | 0,16 | 12 | -R$ 12.000,00 | não fazer (decisão registrada; reavaliar só se a opção SaaS for aprovada) |

Horas comprometidas no ciclo: 76 de 80.
Ranking WSJF: a, f, d, c, e, i, l, k, b, h, g, j. Ranking ICE: a, f, i, d, c, e, k, l, b, h, g, j.

Nível 'bom o suficiente': 5 fluxos críticos (login, OS, amostra, documento, relatório).

| Id | Justificativa |
|---|---|
| a | Boa prática de produto para computadores compartilhados do laboratório; mudança pequena no frontend |
| b | Hoje o cadastro fica no navegador; exige entidade, migração, API e ajuste de tela |
| c | Uso de máquina alimenta indicadores; requer grupos de validação distintos para criar e atualizar |
| d | Comparação automática com 20 ± 2 °C e 45 a 65% de umidade apoia a ISO/IEC 17025 |
| e | Status hoje é texto validado no banco; transições explícitas melhoram qualidade de dados e mensagens |
| f | Mantém a receita no mês correto dos relatórios |
| g | Maior lacuna funcional para a 17025; escopo grande e incerto |
| h | Hoje a impressão é feita pelo navegador; ganho de padronização |
| i | Pré-requisito de todos os benefícios (as mesmas 24 h já estão no investimento de implantação); valor anual igual ao benefício líquido anual em regime (ano 2) do cenário base, calculado pelo modelo |
| j | Decisão registrada de não implementar; só faz sentido se a opção SaaS for escolhida |
| k | Protege a evolução contra regressões; escopo limitado pelo princípio bom o suficiente (ver análise abaixo) |
| l | Facilita integração e manutenção por outra equipe de TI |

**Bom o suficiente em testes de interface:** benefício e custo acumulados (VP, R$) por nível de cobertura.

| Nível | Custo acumulado | Benefício acumulado |
|---|---|---|
| Sem testes de interface (só testes de API e serviço atuais) | R$ 0,00 | R$ 0,00 |
| 5 fluxos críticos (login, OS, amostra, documento, relatório) | R$ 960,00 | R$ 3.000,00 |
| Todas as 22 telas | R$ 2.400,00 | R$ 3.800,00 |
| Todas as telas + regressão visual nos 2 temas e 3 idiomas | R$ 4.800,00 | R$ 4.300,00 |

| Passo para | Custo marginal | Benefício marginal |
|---|---|---|
| 5 fluxos críticos (login, OS, amostra, documento, relatório) | R$ 960,00 | R$ 3.000,00 |
| Todas as 22 telas | R$ 1.440,00 | R$ 800,00 |
| Todas as telas + regressão visual nos 2 temas e 3 idiomas | R$ 2.400,00 | R$ 500,00 |

Nível escolhido: **5 fluxos críticos (login, OS, amostra, documento, relatório)**. Depois dele, cada real adicional compra menos de um real de benefício.

**O que não fazer agora:** b (Persistir o cadastro de scanners 3D no servidor): próximo ciclo (VPL positivo, sem capacidade agora); h (Geração de relatórios PDF no servidor): próximo ciclo (VPL positivo, sem capacidade agora); g (Módulo de calibração com certificados e incerteza de medição): próximo ciclo (VPL positivo, sem capacidade agora); j (Multi-tenancy para oferta SaaS): não fazer (decisão registrada; reavaliar só se a opção SaaS for aprovada).

## Riscos e hipóteses (transparência)

| Risco | Probabilidade | Impacto | Variável do modelo | Mitigação |
|---|---|---|---|---|
| Benefícios menores que o previsto (adoção baixa) | média | alto | usuarios, horas_economizadas_usuario_mes | Treinamento, medição de uso no 1º trimestre e revisão do modelo |
| Camada gratuita de nuvem descontinuada ou recuperada pelo provedor | média | médio | custo_infra_ano | Reserva de migração, backup externo diário cifrado e deploy em contêiner reproduzível |
| Exigências de padrão institucional de TI (banco de dados e arquitetura) que obriguem reescrita | média | alto | investimento, horas_manutencao_mes | Negociar escopo de aderência antes da produção; manter o sistema portável |
| Manutenção acima do estimado ao transferir a operação para outra equipe | média | médio | horas_manutencao_mes | Documentação de API, testes automatizados e runbook |
| Taxa horária de mercado diferente da hipótese | alta | médio | taxa_hora_dev | Sensibilidade de ±20% e cenários; validar com pesquisa salarial |
| Exploração comercial sem acordo de propriedade intelectual | baixa | alto | modelo de negócio | Formalizar acordo com a instituição antes de qualquer oferta externa |

## Limitações

- O sistema ainda não está em produção: nenhum benefício foi medido; todos são hipóteses com faixa.
- O esforço é estimativa derivada do histórico do repositório; commits agrupados e trabalho sem commit tornam a faixa larga.
- O plano de referência do GVA foi reconstruído depois do fato; IDC e IDP servem para aprendizado, não para auditoria.
- Preços de infraestrutura, de LIMS e alíquotas são parâmetros configuráveis, não cotações oficiais.
- Valores reais (sem inflação) e sem valor residual no fim do horizonte, o que é conservador.
- O modelo de negócio externo depende de acordo de licença com a instituição e, no caso SaaS, de multi-tenancy.

Fórmulas: `references/formulas.md`. Alíquotas e parâmetros a validar: `references/aliquotas.md`.
