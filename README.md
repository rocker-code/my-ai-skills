# AI Engineering Workflow

Português (Brasil) · [English](README.en.md)

Skills e ferramentas para desenvolvimento com IA orientado por issues. O GitHub registra decisões e entregas; o OpenSpec estrutura o planejamento e a implementação.

## Instalar ou atualizar (OpenCode)

Linux/macOS: requer Git, Python 3.10+, `curl`, `gh`, `jq` e OpenCode V2 no `PATH`. Para usar o workflow, o OpenSpec é necessário, mas **não precisa estar instalado antes**: o instalador preserva o CLI existente ou instala a distribuição standalone oficial para seu usuário se estiver ausente. Autentique o GitHub CLI separadamente com `gh auth login`.

O comando fixa a entrada em `57733e891659174b79c772fb4f16d8b47fe6c93c` e confere seu SHA-256 literal `07caf29cb6a331fbb00310a3e3df836834b8f55aa89059f28032f6f8a8215fa1` antes da execução:

```bash
( tmp=$(mktemp) && trap 'rm -f "$tmp"' EXIT &&
  curl -fsSL 'https://raw.githubusercontent.com/rocker-code/my-ai-skills/57733e891659174b79c772fb4f16d8b47fe6c93c/scripts/install-global' -o "$tmp" &&
  python3 -c 'import hashlib,sys;sys.exit(0 if hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest()==sys.argv[2] else 1)' "$tmp" '07caf29cb6a331fbb00310a3e3df836834b8f55aa89059f28032f6f8a8215fa1' &&
  python3 "$tmp" --revision 57733e891659174b79c772fb4f16d8b47fe6c93c --agent opencode )
```

Para **atualizar**, aprove uma revisão Git completa e substitua **somente** o SHA de `--revision` no comando acima; a URL do instalador e o digest permanecem fixos. Repetir o comando com a mesma revisão não atualiza para `main`. Não use `npx skills update` nem execute o instalador da instalação ativa para atualizar o pacote. [Detalhes, conflitos e migração](https://github.com/rocker-code/my-ai-skills/wiki/Instalacao-global).

## Verificar e usar

```bash
test -f "${XDG_DATA_HOME:-$HOME/.local/share}/my-ai-skills/active/manifest.json"
test -f "${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills/apply-issue/SKILL.md"
openspec --version
```

Abra uma nova sessão OpenCode. No primeiro uso em um projeto, o agente confere a integração OpenSpec e pede autorização antes de inicializá-la; a instalação global não modifica projetos. Confira `/opsx-explore`, `/opsx-propose`, `/opsx-apply` e `/opsx-archive` antes de implementar.

Peça **“Cuide da issue: URL”**, **“Cuide da fila deste projeto”** ou **“Cuide deste milestone: URL”**; acrescente **“sem merge”** se quiser integrar manualmente. O fluxo planeja com OpenSpec, implementa, testa, prepara a PR e revisa; o merge padrão só ocorre após as verificações exigidas. O agente precisa de acesso ao GitHub e de sessões/worktrees isoladas para executar o fluxo completo.

[Guia do fluxo e demais recursos](https://github.com/rocker-code/my-ai-skills/wiki/Guia-do-fluxo) · [Instalação legada por projeto](https://github.com/rocker-code/my-ai-skills/wiki/Instalacao-legada) (não necessária para a instalação global) · [Wiki](https://github.com/rocker-code/my-ai-skills/wiki)
