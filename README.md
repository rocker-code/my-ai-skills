# AI Engineering Workflow

Português (Brasil) · [English](README.en.md)

Skills e ferramentas para desenvolvimento com IA orientado por issues. O GitHub registra decisões e entregas; o OpenSpec estrutura o planejamento e a implementação.

## Fluxo de trabalho

O fluxo começa no agente Web: você descreve a necessidade, as skills consultam o contexto e criam/refinam a issue no GitHub. Depois, o agente CLI recebe a issue ou milestone e conduz o planejamento, a implementação e a revisão.

O ciclo passa por descoberta, prontidão, implementação, revisão e conclusão. OpenSpec é obrigatório; `openspec-workflow` rege exploração, propostas, validação da revisão exata, verificação da implementação e arquivamento.

![Fluxo do AI Engineering Workflow: da ideia à issue com agente Web, seguida de planejamento, implementação, validação e merge no CLI.](docs/images/fluxo-my-ai-skills.svg)

[Veja o fluxo completo na wiki](https://github.com/rocker-code/my-ai-skills/wiki/Guia-do-fluxo).

## Instalar ou atualizar

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

## Configurar o projeto no agente Web

Para usar as duas skills nas conversas do projeto, mantenha o conector GitHub disponível com acesso ao `rocker-code/my-ai-skills` e aos repositórios de destino. Copie o bloco abaixo para as **instruções do projeto no agente Web** (ChatGPT, Claude ou equivalente). Ele orienta a consulta das instruções atuais no GitHub; não instala skills automaticamente nem altera as configurações da conta por si só.

Não é necessário anexar os arquivos das skills a cada conversa quando o conector consegue lê-los. As regras detalhadas ficam nos protocolos versionados: alterações passam a ser consultadas após o merge em `main`. Atualize este bloco nas configurações se o próprio texto de encaminhamento mudar. Se a leitura pelo conector falhar, o agente deve informar quais fontes não conseguiu consultar, sem afirmar que aplicou a versão atual.

O mesmo texto pode ser usado nas instruções de projeto do ChatGPT, Claude ou de outro agente que aceite descrições persistentes do projeto. A capacidade depende do ambiente: ler instruções não concede acesso ao GitHub nem permissão para criar issues. Se não houver integração de escrita, o agente pode preparar um rascunho, informando que a publicação não foi realizada.

### Instruções para copiar

```text
# Rocker Code — Instruções do Projeto

Este projeto utiliza o AI Engineering Workflow, disponível em
https://github.com/rocker-code/my-ai-skills, como referência
para engenharia de software e gerenciamento de GitHub Issues.

## Skills do agente Web (ChatGPT, Claude ou equivalente)

Use estas instruções no ChatGPT, Claude ou outro agente com instruções de projeto.
Os nomes chatgpt-web-* são mantidos por compatibilidade. É necessário acesso de
leitura às fontes; alterações de issues exigem integração GitHub autorizada.

No início de cada tarefa de criação ou revisão de issues, consulte pela integração
GitHub disponível a versão atual em main da skill correspondente e do protocolo compartilhado:

- Criação: skills/chatgpt-web-create-issue/SKILL.md
- Revisão/refinamento: skills/chatgpt-web-refine-issue/SKILL.md
- Protocolo: protocol/CHATGPT_WEB_ISSUES.md
- Design visual, quando aplicável: protocol/VISUAL_ARTIFACTS.md

Para consultas rápidas de roadmap (“me situa”, “onde estamos”, “como estamos no MVP”,
“o que faço agora”), consulte em main skills/roadmap-status/SKILL.md pela integração
GitHub e siga suas instruções. Mostre até 5 linhas de tabela, um próximo passo
e decisões pendentes; informe limitações de acesso e não execute alterações.

Quando eu pedir “atualize o my-ai-skills” ou “atualize o workflow de IA deste projeto”,
consulte em main skills/update-ai-workflow/SKILL.md e siga suas instruções.
Execute apenas sob pedido explícito, preservando agentes, escopo e ajustes locais.
Se não houver acesso ao ambiente local, informe a limitação e entregue o próximo
comando necessário; não afirme que minha instalação foi atualizada.

Leia também as referências necessárias indicadas nesses arquivos. Reutilize a
leitura dentro da mesma tarefa; atualize-a se houver mudança relevante. Se uma
fonte estiver inacessível, informe a limitação e não invente seu conteúdo.

## Regras

- Aplique a skill conforme a solicitação, sem exigir comandos especiais.
- Consulte issues, comentários, decisões, PRs e código relevante; identifique a
  revisão inspecionada e o que já existe para evitar trabalho duplicado.
- Preserve os padrões dos projetos Magento, Mobile e App Operacional. Distinga
  fatos verificados, decisões aprovadas, propostas e questões abertas.
- Abra a issue com um resumo simples: o que muda, onde muda e de que depende.
  Defina comportamento esperado, escopo, fora do escopo e critérios observáveis.
- Inclua cenários de teste em tabela com preparação/ação, resultado esperado e
  camada sugerida. Priorize riscos reais, reutilize testes e massas de teste e evite
  matrizes exaustivas ou cobertura duplicada.
- Em integrações, documente a assinatura atual e a esperada, exemplos, estados,
  erros, autorização e dependências entre produtor e consumidor. Identifique
  contratos propostos como não implementados/não congelados; registre a
  assinatura efetiva após o entrega do contrato antes da integração final.
- Para backend, integração ou arquitetura, inclua system design Mermaid simples,
  com responsabilidades e fluxo dos dados verificáveis.
- Para interfaces, inclua esboço em caracteres em bloco text, principais estados
  e ações, além de referências visuais aprovadas, acessíveis e versionadas quando
  houver design. Valores ilustrativos não são dados reais. Siga VISUAL_ARTIFACTS.md;
  um link privado de Claude Artifacts sozinho não comprova acesso ao design.
- Quando houver conteúdo apresentado ao usuário, inclua i18n e tradução conforme
  o mecanismo e locale do projeto: textos, estados, erros, acessibilidade, datas,
  números, moeda e plurais. Defina quem traduz os textos da API; não exponha enums
  ou chaves cruas. Preserve nomes/dados de domínio e preveja fallback traduzido
  seguro para códigos desconhecidos, com critérios e testes representativos.
- Mantenha comportamento, design, esboço, contrato, critérios e testes coerentes.
  Ajustes pontuais devem preservar o conteúdo e as decisões fora de seu escopo.
- Explique questões técnicas e alternativas de forma simples quando houver uma
  decisão material pendente do usuário. Resolva detalhes rotineiros por evidências
  e não peça confirmações extras para ações já solicitadas ou autorizadas.
- Registre decisões aprovadas nas issues quando solicitado. Verifique as alterações
  no GitHub antes de afirmar sucesso e forneça os links e bloqueios restantes.
- Não implemente código ao criar/refinar issues; a execução segue o fluxo CLI com
  OpenSpec. Não invente código inspecionado, contratos, anexos ou testes executados.

## Forma de trabalho

Aceite pedidos naturais como:
- "Crie uma issue para..."
- "Analise a issue #123."
- "Responda à dúvida desta issue."
- "Revise as issues do milestone."
- "Atualize a especificação considerando o design anexado."

Não exija que o usuário repita estas instruções.
```

## Usar

O instalador e o atualizador conferem ao final o pacote, uma skill e o OpenSpec. Abra uma nova sessão OpenCode. No primeiro uso em um projeto, o agente confere a integração OpenSpec e pede autorização antes de inicializá-la; a instalação global não modifica projetos. Confira `/opsx-explore`, `/opsx-propose`, `/opsx-apply` e `/opsx-archive` antes de implementar.

Peça **“Cuide da issue: URL”**, **“Cuide da fila deste projeto”** ou **“Cuide deste milestone: URL”**; acrescente **“sem merge”** se quiser integrar manualmente. O fluxo planeja com OpenSpec, implementa, testa, prepara a PR e revisa; o merge padrão só ocorre após as verificações exigidas. O agente precisa de acesso ao GitHub e de sessões/worktrees isoladas para executar o fluxo completo.

[Guia do fluxo e demais recursos](https://github.com/rocker-code/my-ai-skills/wiki/Guia-do-fluxo) · [Instalação legada por projeto](https://github.com/rocker-code/my-ai-skills/wiki/Instalacao-legada) (não necessária para a instalação global) · [Wiki](https://github.com/rocker-code/my-ai-skills/wiki)
