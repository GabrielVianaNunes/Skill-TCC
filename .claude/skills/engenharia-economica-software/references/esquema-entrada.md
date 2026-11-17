# Esquema do JSON de `gerar_relatorio.py`

Modelo completo e executável: `../assets/modelo_entrada.json`. Os scripts individuais documentam a própria entrada em `--help` e `--exemplo`.

## Blocos obrigatórios

| Chave | Conteúdo |
|---|---|
| `meta` | `titulo`, `sistema`, `descricao`, `autores` (lista), `curso`, `componente`, `docente`, `data_base`, `moeda`, `situacao` |
| `premissas` | `horizonte_anos`; `tma` com `taxa_base`, `premios` (mapa nome: taxa), `inflacao`, `faixa_nominal` [mín, máx]; opcionais `premio_risco_negocio`, `tributos_uso_interno` |
| `parametros` | mapa nome: valor fixo ou objeto `{min, provavel, max, unidade, descricao, origem, como_validar}`; opcionais `sentido_fixo` ("beneficio" ou "custo") e `derivacao`. `taxa_hora_dev` é obrigatório |
| `esforco` | git: `arquivo_log` (CSV `data_hora,autor`, caminho relativo ao JSON), `excluir_datas`, `horas_por_dia_ativo`, `fator_trabalho_sem_commit`, `intervalo_sessao_horas`, `preparo_sessao_horas`, `nota_metodo`; ou sem git: `meses_informados` [{mes, horas_min, horas_provavel, horas_max}]. Opcional `base_importada` {linhas, produtividade_linhas_hora {alta, provavel, baixa}, como_validar} |
| `implantacao` | lista de {descricao, horas (número ou "k*parametro"), taxa (nome de parâmetro)} ou {descricao, valor} |
| `beneficios` | lista de {nome, fatores (nomes de parâmetros multiplicados), multiplicador} |
| `opex` | igual a `beneficios` |

## Blocos opcionais

| Chave | Conteúdo |
|---|---|
| `fatos_medidos` | lista de {item, valor} |
| `rampa_adocao` | fração de uso por ano (padrão 1,0) |
| `custos_indiretos_desenvolvimento` | lista de {descricao, valor, rateio} |
| `ativos_ti` | lista de {nome, custo, taxa_anual ou vida_anos, residual} |
| `gva` | `bac_horas`, `bac_nota`, `nota_registro`, `sprints_planejadas`, `meses` (chaves AAAA-MM), `rotulos`, `pacotes` [{id, nome, pontos, mes_concluido ou null}], `duracao_planejada_meses` |
| `alternativas_infra` | `descricao`, `opcoes` [{nome, investimento, anual, vida, nota}], `criterios` [{nome, peso}], `notas` {opção: {critério: nota}} |
| `construir_vs_comprar` | `descricao`, `lims_implantacao`, `lims_assinatura_mensal`, `nota`, `parametro_equipe` |
| `aposentadoria` | lista de {componente, opcoes [{nome, investimento, anual (negativo = custo), nota}]} |
| `backlog` | `capacidade_horas`, `limiar_valor`, `limiar_horas`, `itens` [{id, titulo, valor, esforco_horas, criticidade_tempo, reducao_risco, confianca, valor_anual (número ou "$beneficio_liquido_ano2"), justificativa, decisao_fixa}], `niveis_qualidade_testes_interface` [{nome, custo, beneficio}] |
| `modelo_negocio` | `nota_licenca`, `nota_multitenancy`, `tributos_simples_aliquota_efetiva`, `presumido`, `aliquota_ir_csll_lucro_real`, `saas` {capex_horas, capex_outros, capex_descricao, custo_variavel_mensal_cliente {infra, horas_suporte}, custos_fixos_anuais {infra, horas_manutencao_mes}, margem_desejada, captura_valor, preco_mensal, cac, churn_mensal, novos_por_ano}, `implantacao_suporte` {capex_horas, capex_outros, capex_descricao, taxa_implantacao, horas_implantacao, mensalidade_suporte, horas_suporte_mes_cliente, custos_fixos_anuais {horas_manutencao_mes}, cac, churn_mensal, novos_por_ano}, `criterios`, `notas` (a nota de VPL é calculada) |
| `riscos` | lista de {risco, probabilidade, impacto, variavel, mitigacao} |

## Regras do modelo

- Fluxos anuais em valores reais; desconto pela TMA real = (1 + TMA nominal) / (1 + inflação) - 1.
- Leitura A: F_0 = -soma(implantação); F_t = benefícios_t x rampa_t - OpEx_t.
- Leitura B: F_0 da Leitura A menos o custo econômico do desenvolvimento (horas x `taxa_hora_dev` + indiretos).
- Cenários: base usa `provavel`; pessimista usa `min` nos fatores de benefício e `max` nos de custo; otimista, o inverso. `sentido_fixo` força o mesmo sentido em todos os usos do parâmetro.
- O ponto de equilíbrio em horas usa os parâmetros `usuarios`, `custo_hora_equipe` e `horas_economizadas_usuario_mes`, se existirem.
