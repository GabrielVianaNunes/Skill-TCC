# Roteiro do mini workshop (24/11/2026)

Duração sugerida: 15 minutos de apresentação e 5 de perguntas. Apresentadores: Gabriel Viana Nunes e João Vítor de Alencar Fraissat Mamede.

## Preparação (antes da aula)

1. Clonar o repositório e rodar `python -m unittest discover -s tests` (deve terminar em OK).
2. Rodar `python scripts/validate_skill.py` (0 erros).
3. Abrir o Claude Code na raiz do repositório e conferir que a skill aparece (`/skills` ou perguntar "quais skills você tem?").
4. Deixar abertos: `README.md`, `examples/tcc-valuation-report.md` e um terminal.
5. Plano B sem internet: executar os scripts direto no terminal (os comandos abaixo funcionam sem modelo de linguagem).

## Roteiro

| Tempo | Quem | O que mostrar |
|---|---|---|
| 0:00 a 2:00 | Gabriel | Problema: decisões de engenharia são decisões econômicas. O que é uma Agent Skill e a divulgação progressiva (diagrama do README) |
| 2:00 a 4:00 | João | Estrutura do repositório: `SKILL.md` (frontmatter e fluxo), `scripts/`, `references/`, `assets/`, `evals/`; por que número só sai de script |
| 4:00 a 7:00 | Gabriel | Demonstração ao vivo 1: no Claude Code, perguntar "Um módulo custa R$ 1.000 e gera 300, 400, 500 e 600 nos próximos 4 anos, TMA de 10%. Vale a pena?". Mostrar o script sendo executado e o resultado (VPL R$ 388,77; TIR 24,89%; payback 2,6 e 3,05 anos) |
| 7:00 a 8:30 | João | Demonstração ao vivo 2: fluxo -100, 230, -132 sem TMA. A skill acusa duas TIRs (10% e 20%), não inventa uma e pede a TMA |
| 8:30 a 13:00 | Gabriel e João | Valoração do TCC: rodar `python .agents/skills/engenharia-economica-software/scripts/gerar_relatorio.py --entrada examples/tcc-input.json --saida-md /tmp/r.md` e percorrer o relatório: premissas com origem, Leituras A e B, GVA reconstruído, modelo de negócio, backlog |
| 13:00 a 15:00 | João | Limitações e honestidade: benefícios são hipóteses, esforço é estimativa do git, GVA reconstruído; próximos passos (medir em produção) |

## Mensagens-chave

- O sistema vale a pena a partir de hoje (Leitura A: VPL de R$ 38.596,38, payback descontado de 1 ano), mas o uso interno sozinho não paga o custo econômico do desenvolvimento em 5 anos (Leitura B: VPL de -R$ 49.240,95). Para empatar, seriam precisas 7,3 h economizadas por usuário/mês, contra 4 h na hipótese base.
- O modelo de negócio externo mais coerente com as decisões técnicas é implantação e suporte com uma instância por laboratório (VPL de R$ 3.190,30), não SaaS (VPL negativo, exige multi-tenancy).
- GVA: IDC 0,857 e IDP 0,849 em 04/11; a pendência de implantação em produção explica a maior parte do atraso.

## Perguntas prováveis e respostas curtas

- **"De onde veio a taxa horária?"** Hipótese de mercado com derivação explícita (salário x 1,8 / 150 h), faixa de R$ 48 a R$ 84 e sensibilidade.
- **"Por que a TIR da Leitura A é tão alta?"** Porque o investimento a partir de hoje é pequeno (só implantação); o desenvolvimento é custo afundado. Por isso mostramos também a Leitura B.
- **"O GVA é real?"** É reconstruído: o plano de referência e os pontos foram atribuídos depois. O CR vem de estimativa do git. Serve para aprendizado, e o relatório diz isso.
- **"Por que não usar a Selic atual?"** A skill não afirma taxa vigente: pede ao usuário ou usa hipótese rotulada. Trocar a taxa base no JSON e gerar de novo leva segundos.
- **"Funciona em outros modelos?"** O formato é o padrão aberto Agent Skills. Testamos no Claude Code; nos demais harnesses a compatibilidade é por especificação (README, seção Plataformas).
