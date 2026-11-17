# Fluxo de trabalho (Git Flow)

Este repositório segue o Git Flow. A ideia é simples: `main` sempre contém a versão entregue e estável, e todo
trabalho novo passa por revisão antes de chegar lá.

## Branches

| Branch | Função | Protegida |
|---|---|---|
| `main` | Versão estável e entregue. Cada versão recebe uma tag (`v1.0.0`). | Sim |
| `develop` | Integração das próximas mudanças. | Sim |
| `feature/<assunto>` | Uma funcionalidade ou ajuste, criada a partir de `develop`. | Não |
| `release/<versão>` | Preparação de uma versão (changelog, ajustes finais), criada a partir de `develop`. | Não |
| `hotfix/<assunto>` | Correção urgente, criada a partir de `main`. | Não |

## Passo a passo

1. `git switch develop && git pull`
2. `git switch -c feature/<assunto>`
3. Trabalhe e rode `python -m unittest discover -s tests` e `python scripts/validate_skill.py`.
4. Abra um Pull Request de `feature/<assunto>` para `develop`. O CI precisa passar.
5. Para publicar uma versão: crie `release/<versão>` a partir de `develop`, atualize o `CHANGELOG.md` e abra um
   Pull Request para `main`. Depois do merge, crie a tag `v<versão>` em `main` e traga `main` de volta para `develop`.
6. Correção urgente: `hotfix/<assunto>` a partir de `main`, Pull Request para `main` e depois para `develop`.

## Regras de proteção

`main` e `develop` não aceitam push direto, push forçado nem exclusão: tudo entra por Pull Request com o CI
(`testes`) aprovado e conversas resolvidas.

## Mensagens de commit

Português, no formato `tipo: descrição` (`feat`, `fix`, `docs`, `test`, `chore`, `refactor`).

## Privacidade

O repositório é público. Nunca versione segredos, e-mails pessoais, telefones, CPF/CNPJ, caminhos do seu computador
ou dados de terceiros. Use o e-mail `noreply` do GitHub como autor dos commits
(`git config user.email "<id>+<usuario>@users.noreply.github.com"`) e ative, no GitHub, as opções
*Keep my email addresses private* e *Block command line pushes that expose my email*.
O `.gitignore` cobre segredos e arquivos locais; o que for específico de uma máquina vai em `.git/info/exclude`.
