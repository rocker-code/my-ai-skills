# AI Engineering Workflow

Português (Brasil) · [English](README.en.md)

Skills e ferramentas para desenvolvimento com IA orientado por issues. O GitHub registra decisões e entregas; o OpenSpec estrutura o planejamento e a implementação.

## Instalar ou atualizar (OpenCode)

Linux/macOS: requer Git, Python 3.10+, `curl`, `gh`, `jq` e OpenCode V2 no `PATH`. Para usar o workflow, o OpenSpec é necessário, mas **não precisa estar instalado antes**: o instalador preserva o CLI existente ou instala a distribuição standalone oficial para seu usuário se estiver ausente. Autentique o GitHub CLI separadamente com `gh auth login`.

Execute o instalador diretamente do GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/rocker-code/my-ai-skills/main/scripts/install.sh | sh
```

O script instala a versão mais recente da `main`. Ele baixa uma versão fixa do **instalador**, confere seu SHA-256 e só então a usa para instalar a revisão atual. Se o `curl` falhar, ele avisa, mas o pipeline pode retornar sucesso sem instalar nada. **A verificação não cobre o próprio script obtido de `main`**: revise [seu código](scripts/install.sh) antes de executá-lo ou use o [comando com entrada verificada](https://github.com/rocker-code/my-ai-skills/wiki/Instalacao-global) para maior garantia.

Para **atualizar para a versão mais recente da `main`**, execute (somente quando quiser atualizar):

```bash
curl -fsSL https://raw.githubusercontent.com/rocker-code/my-ai-skills/main/scripts/update.sh | sh
```

**Os dois comandos instalam a revisão mais recente ao serem executados.** `update.sh` apenas deixa explícita a intenção de atualizar; ele confia na `main` atual e chama o mesmo instalador verificado. Nenhuma atualização roda em segundo plano. Não use `npx skills update` nem execute o instalador da instalação ativa para atualizar o pacote. [Detalhes, conflitos e migração](https://github.com/rocker-code/my-ai-skills/wiki/Instalacao-global).

## Usar

O instalador e o atualizador conferem ao final o pacote, uma skill e o OpenSpec. Abra uma nova sessão OpenCode. No primeiro uso em um projeto, o agente confere a integração OpenSpec e pede autorização antes de inicializá-la; a instalação global não modifica projetos. Confira `/opsx-explore`, `/opsx-propose`, `/opsx-apply` e `/opsx-archive` antes de implementar.

Peça **“Cuide da issue: URL”**, **“Cuide da fila deste projeto”** ou **“Cuide deste milestone: URL”**; acrescente **“sem merge”** se quiser integrar manualmente. O fluxo planeja com OpenSpec, implementa, testa, prepara a PR e revisa; o merge padrão só ocorre após as verificações exigidas. O agente precisa de acesso ao GitHub e de sessões/worktrees isoladas para executar o fluxo completo.

[Guia do fluxo e demais recursos](https://github.com/rocker-code/my-ai-skills/wiki/Guia-do-fluxo) · [Instalação legada por projeto](https://github.com/rocker-code/my-ai-skills/wiki/Instalacao-legada) (não necessária para a instalação global) · [Wiki](https://github.com/rocker-code/my-ai-skills/wiki)
