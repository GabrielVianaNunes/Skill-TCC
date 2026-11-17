#!/usr/bin/env python3
"""Valida a skill e o repositório sem dependências externas (sem PyYAML).

Verificações:

1. Frontmatter YAML do SKILL.md com um analisador próprio e restrito (chave: valor e um nível de
   mapa em ``metadata``): campos permitidos, ``name`` igual ao nome da pasta, minúsculas, dígitos e
   hífens, até 64 caracteres; ``description`` de 1 a 1024 caracteres, sem < ou >; ``compatibility``
   até 500 caracteres; ``metadata`` só com textos.
2. Corpo do SKILL.md com menos de 500 linhas e menos de 5.000 unidades de contexto estimadas (chars/4).
3. Referências relativas citadas nos Markdown da skill (links e caminhos ``scripts/...``,
   ``references/...``, ``assets/...``) existem.
4. Estrutura dos casos de teste em ``evals/`` (prompt.md com bloco de configuração, case.yaml com
   ``schema_version`` entre aspas e ``name`` igual à pasta, graders com bloco de cabeçalho).
5. Cópia em ``.claude/skills/`` idêntica à fonte em ``.agents/skills/``.
6. Varredura do repositório: travessões (U+2013 e U+2014), emojis, padrões de credenciais,
   endereços de e-mail e caminhos absolutos com pasta de usuário.

Uso::

    python scripts/validate_skill.py

Sai com código 0 se tudo passar e 1 caso contrário.
"""

from __future__ import annotations

import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOME = "engenharia-economica-software"
SKILL = os.path.join(RAIZ, ".agents", "skills", NOME)
COPIA = os.path.join(RAIZ, ".claude", "skills", NOME)
CAMPOS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
EXTENSOES_TEXTO = {".md", ".py", ".json", ".yaml", ".yml", ".csv", ".txt", ".cfg", ".toml", ".gitignore", ""}
PULAR = {".git", "dist", "__pycache__", "results"}

# Padrões montados por partes para que este arquivo não acuse a si próprio na varredura.
_P = "pass" + "word"
_S = "sen" + "ha"
_SEC = "sec" + "ret"
_TK = "tok" + "en"
PADROES_SEGREDO = {
    "chave privada": re.compile("-----BEGIN [A-Z ]*PRIVATE " + "KEY-----"),
    "chave AWS": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "credencial GitHub": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "credencial Slack": re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{10,}"),
    "chave de API genérica": re.compile(r"\b(sk|pk)_(live|test)_[A-Za-z0-9]{16,}"),
    "atribuição de credencial": re.compile(
        r"(?i)\b(" + _P + "|" + _S + "|" + _SEC + "|api[_-]?key|" + _TK + r")\b\s*[:=]\s*['\"]?[^\s'\"]{6,}"),
    "e-mail": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+"),
    "caminho de usuário Windows": re.compile(r"(?i)[A-Z]:\\\\?Users\\\\?[A-Za-z]"),
    "caminho de usuário Unix": re.compile(r"(/home/|/Users/)[a-z][a-z0-9_-]+/"),
}
TRAVESSOES = {chr(0x2013): "travessão curto (en dash)", chr(0x2014): "travessão (em dash)"}
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U0001F000-\U0001F2FF\U00002600-\U000026FF]")


class Relatorio:
    """Acumula verificações e erros."""

    def __init__(self) -> None:
        self.erros: list[str] = []
        self.oks: list[str] = []

    def ok(self, msg: str) -> None:
        self.oks.append(msg)

    def erro(self, msg: str) -> None:
        self.erros.append(msg)


def _valor_escalar(texto: str) -> str:
    texto = texto.strip()
    if len(texto) >= 2 and texto[0] == texto[-1] and texto[0] in "\"'":
        return texto[1:-1]
    return texto


def analisar_frontmatter(conteudo: str) -> tuple[dict, str]:
    """Analisador YAML mínimo e estrito para o frontmatter do SKILL.md."""
    linhas = conteudo.split("\n")
    if not linhas or linhas[0].strip() != "---":
        raise ValueError("SKILL.md deve começar com '---'")
    try:
        fim = next(i for i in range(1, len(linhas)) if linhas[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("frontmatter sem '---' de fechamento") from exc
    dados: dict = {}
    mapa_atual: str | None = None
    for num_linha, linha in enumerate(linhas[1:fim], start=2):
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        if "\t" in linha:
            raise ValueError(f"linha {num_linha}: tabulação não é permitida em YAML")
        indentado = linha.startswith(" ")
        if ":" not in linha:
            raise ValueError(f"linha {num_linha}: esperado 'chave: valor'")
        chave, valor = linha.strip().split(":", 1)
        chave = chave.strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]+", chave):
            raise ValueError(f"linha {num_linha}: chave inválida '{chave}'")
        if indentado:
            if mapa_atual is None:
                raise ValueError(f"linha {num_linha}: indentação inesperada")
            dados[mapa_atual][chave] = _valor_escalar(valor)
            continue
        if chave in dados:
            raise ValueError(f"linha {num_linha}: chave duplicada '{chave}'")
        if valor.strip() == "":
            dados[chave] = {}
            mapa_atual = chave
        else:
            v = valor.strip()
            if v[0] in "\"'" and (len(v) < 2 or v[-1] != v[0]):
                raise ValueError(f"linha {num_linha}: aspas não fechadas")
            if v[0] in "[{|>&*!":
                raise ValueError(f"linha {num_linha}: use texto simples de uma linha em '{chave}'")
            if v[0] not in "\"'" and ": " in v:
                raise ValueError(f"linha {num_linha}: ': ' dentro de valor sem aspas é YAML inválido")
            dados[chave] = _valor_escalar(v)
            mapa_atual = None
    corpo = "\n".join(linhas[fim + 1:])
    return dados, corpo


def verificar_frontmatter(rel: Relatorio) -> str:
    with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as arq:
        conteudo = arq.read()
    try:
        fm, corpo = analisar_frontmatter(conteudo)
    except ValueError as exc:
        rel.erro(f"frontmatter inválido: {exc}")
        return ""
    rel.ok("frontmatter YAML analisado sem erros")
    extras = set(fm) - CAMPOS
    if extras:
        rel.erro(f"campos não permitidos no frontmatter: {sorted(extras)}")
    nome = fm.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", nome) or len(nome) > 64:
        rel.erro(f"name inválido: '{nome}'")
    elif nome != os.path.basename(SKILL):
        rel.erro(f"name '{nome}' difere da pasta '{os.path.basename(SKILL)}'")
    else:
        rel.ok(f"name '{nome}' igual à pasta, {len(nome)} caracteres")
    desc = fm.get("description", "")
    if not isinstance(desc, str) or not 1 <= len(desc) <= 1024:
        rel.erro(f"description deve ter de 1 a 1024 caracteres (tem {len(desc)})")
    elif "<" in desc or ">" in desc:
        rel.erro("description não pode conter < ou >")
    else:
        rel.ok(f"description com {len(desc)} caracteres")
    comp = fm.get("compatibility")
    if comp is not None and (not isinstance(comp, str) or len(comp) > 500):
        rel.erro("compatibility deve ser texto de até 500 caracteres")
    meta = fm.get("metadata", {})
    if not isinstance(meta, dict) or any(not isinstance(v, str) for v in meta.values()):
        rel.erro("metadata deve ser um mapa de textos")
    linhas = corpo.count("\n") + 1
    unidades = max(len(corpo) / 4.0, len(corpo.split()) * 1.4)
    if linhas >= 500 or unidades >= 5000:
        rel.erro(f"corpo do SKILL.md grande demais: {linhas} linhas, cerca de {unidades:.0f} unidades de contexto")
    else:
        rel.ok(f"corpo do SKILL.md: {linhas} linhas, cerca de {unidades:.0f} unidades de contexto (limite 5.000)")
    return corpo


def verificar_referencias(rel: Relatorio) -> None:
    faltando = []
    padrao_link = re.compile(r"\]\(([^)#\s]+)")
    padrao_caminho = re.compile(r"`((?:\.\./)?(?:scripts|references|assets)/[A-Za-z0-9_./-]+)`")
    for pasta, dirs, nomes in os.walk(SKILL):
        dirs[:] = [d for d in dirs if d not in PULAR and d != "evals"]
        for nome in nomes:
            if not nome.endswith(".md"):
                continue
            caminho = os.path.join(pasta, nome)
            with open(caminho, encoding="utf-8") as arq:
                texto = arq.read()
            alvos = set(padrao_link.findall(texto)) | set(padrao_caminho.findall(texto))
            for alvo in alvos:
                if alvo.startswith(("http://", "https://", "mailto:")):
                    continue
                base = pasta if alvo.startswith(("./", "../")) else SKILL
                if not os.path.exists(os.path.normpath(os.path.join(base, alvo))) and \
                        not os.path.exists(os.path.normpath(os.path.join(pasta, alvo))):
                    faltando.append(f"{os.path.relpath(caminho, RAIZ)} -> {alvo}")
    if faltando:
        for f in faltando:
            rel.erro(f"referência inexistente: {f}")
    else:
        rel.ok("todas as referências relativas da skill existem")


def verificar_evals(rel: Relatorio) -> None:
    base = os.path.join(SKILL, "evals")
    casos = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))) if os.path.isdir(base) else []
    if len(casos) < 3:
        rel.erro(f"esperados ao menos 3 casos em evals/, há {len(casos)}")
    for caso in casos:
        pasta = os.path.join(base, caso)
        if not re.fullmatch(r"[a-z][a-z0-9-]*", caso):
            rel.erro(f"nome de caso inválido: {caso}")
        try:
            with open(os.path.join(pasta, "prompt.md"), encoding="utf-8") as arq:
                prompt = arq.read()
            with open(os.path.join(pasta, "case.yaml"), encoding="utf-8") as arq:
                case = arq.read()
        except OSError as exc:
            rel.erro(f"caso {caso}: {exc}")
            continue
        if not prompt.startswith("---\n") or prompt.count("---") < 2:
            rel.erro(f"caso {caso}: prompt.md sem bloco de configuração")
        if not re.search(r'^schema_version: "[0-9.]+"$', case, re.M):
            rel.erro(f"caso {caso}: schema_version ausente ou sem aspas")
        if not re.search(rf"^name: {re.escape(caso)}$", case, re.M):
            rel.erro(f"caso {caso}: name do case.yaml difere da pasta")
        if "expected_outcome: |" not in case:
            rel.erro(f"caso {caso}: expected_outcome ausente")
        graders = os.path.join(pasta, "graders")
        arquivos = sorted(os.listdir(graders)) if os.path.isdir(graders) else []
        if not arquivos:
            rel.erro(f"caso {caso}: sem graders")
        for g in arquivos:
            with open(os.path.join(graders, g), encoding="utf-8") as arq:
                if not arq.read().startswith("---\ntype: "):
                    rel.erro(f"caso {caso}: grader {g} sem cabeçalho")
    if casos:
        rel.ok(f"{len(casos)} casos de teste em evals/ com estrutura válida" if not any(
            "caso" in e for e in rel.erros) else "casos de teste verificados")


def verificar_copia(rel: Relatorio) -> None:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from sync_skill_copies import diferencas  # noqa: E402
    difs = diferencas(SKILL, COPIA)
    if difs:
        rel.erro("cópia .claude/skills difere da fonte: " + "; ".join(difs[:5]) + " (rode scripts/sync_skill_copies.py)")
    else:
        rel.ok("cópia em .claude/skills idêntica à fonte em .agents/skills")


def varrer_repositorio(rel: Relatorio) -> None:
    problemas = []
    for pasta, dirs, nomes in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in PULAR]
        for nome in nomes:
            ext = os.path.splitext(nome)[1].lower()
            if ext not in EXTENSOES_TEXTO and nome not in ("LICENSE",):
                continue
            caminho = os.path.join(pasta, nome)
            try:
                with open(caminho, encoding="utf-8") as arq:
                    linhas = arq.read().split("\n")
            except (UnicodeDecodeError, OSError):
                continue
            relativo = os.path.relpath(caminho, RAIZ)
            for n, linha in enumerate(linhas, start=1):
                for car, desc in TRAVESSOES.items():
                    if car in linha:
                        problemas.append(f"{relativo}:{n}: {desc}")
                if EMOJI.search(linha):
                    problemas.append(f"{relativo}:{n}: emoji")
                if relativo.replace(os.sep, "/") == "scripts/validate_skill.py":
                    continue
                for desc, padrao in PADROES_SEGREDO.items():
                    if padrao.search(linha):
                        problemas.append(f"{relativo}:{n}: possível {desc}")
    if problemas:
        for p in problemas:
            rel.erro(p)
    else:
        rel.ok("varredura: sem travessões, emojis, credenciais, e-mails ou caminhos de usuário")


def main() -> int:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
    rel = Relatorio()
    verificar_frontmatter(rel)
    verificar_referencias(rel)
    verificar_evals(rel)
    verificar_copia(rel)
    varrer_repositorio(rel)
    for msg in rel.oks:
        print(f"[OK] {msg}")
    for msg in rel.erros:
        print(f"[ERRO] {msg}")
    print(f"\n{len(rel.oks)} verificações OK, {len(rel.erros)} erros.")
    return 1 if rel.erros else 0


if __name__ == "__main__":
    sys.exit(main())
