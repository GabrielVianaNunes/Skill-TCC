# Checklist de pegadinhas de Engenharia Econômica

Erros comuns que a skill foi projetada para evitar, com o teste automatizado que cobre cada um.

| Pegadinha | Como a skill trata | Teste |
|---|---|---|
| TIR reportada quando há múltiplas raízes | `tir()` devolve `status = multiplas` e a lista de raízes | `test_vpl_tir.TestTir.test_multiplas_raizes` |
| TIR inventada quando não existe | `status = sem_raiz` com mensagem | `test_sem_raiz_mesmo_sinal`, `test_sem_raiz_com_troca` |
| Payback sem interpolação (só anos inteiros) | interpolação linear dentro do período | `TestPayback.test_simples` |
| Payback descontado menor que o simples | impossível pela construção; testado | `test_descontado_maior_que_simples` |
| Saldo que volta a ficar negativo | usa o último período negativo | `test_saldo_que_volta_a_ficar_negativo` |
| Taxa anual aplicada a fluxo mensal | conversão explícita por equivalência | `test_mensal_para_anual`, `test_anual_para_mensal` |
| Taxa nominal confundida com efetiva | funções separadas | `test_nominal_efetiva` |
| Fluxo real descontado por taxa nominal | relatório usa TMA real com fluxo real (Fisher) | `test_fisher`, `test_tma_composta` |
| Vidas diferentes comparadas por VPL | `comparar_alternativas` troca para CAUE | `test_vidas_diferentes_usa_caue` |
| Custo afundado na decisão de seguir | Leituras A e B separadas | `test_leitura_b_menor_que_a` |
| Depreciação como saída de caixa | só entra via escudo fiscal no Lucro Real | `test_fluxo_apos_impostos` |
| LTV sem desconto | LTV descontado pela TMA mensal, conferido contra a série | `test_ltv_descontado_igual_serie` |
| EAC único | três variantes de EAC e TCPI | `TestGva.test_tres_eac` |
| Taxa de juros ou alíquota afirmada como fato atual | parâmetros com "validar" e TMA com taxa base rotulada | caso de avaliação `tir-multipla-sem-tma` |
| Travessões e formatação fora do padrão pt-BR | formatação `R$ 1.234,56`; validador varre o repositório | `test_brl`, `test_sem_travessao`, `scripts/validate_skill.py` |
