# Design

## Context

No commit base `a722f4c4894e62ba50ff9dd0921d7f03d87664d0`, `scripts/install-global` aceita `--revision` completo e apenas `--agent opencode`; prepara `versions/<SHA>/{skills,protocol,templates,scripts}`, valida bytes/modos via `manifest.json`, verifica o `active` anterior contra Git e aponta `active` à nova revisão depois de preparar orientação/vínculos. `tests/test_global_install.py` já usa HOME, fonte Git e falhas simuladas descartáveis. `README.md` e `README.en.md` publicam bootstrap com SHA e digest independente da entrada; `update-ai-workflow` ainda prescreve `npx skills add` e cópias `.ai-workflow`. O plugin pessoal não é fonte (#52).

## Goals / Non-Goals

**Goals:** Uma execução usa uma revisão aprovada e tem relatório preciso para pacote e cópias legadas visíveis; mantém ponteiro anterior/arquivos personalizados quando falha; preserva contratos da instalação #50.

**Non-Goals:** Descobrir/reescrever todos os repositórios, eliminar cópias customizadas, atualizar runtimes ou OpenSpec existente, usar `npx skills update`, atualizar sem pedido ou publicar um serviço de versões.

## Decisions

### Reutilizar a entrada verificada da #50, não executá-la a partir de `active`

O comando público continuará baixando a entrada por commit imutável e conferindo o SHA-256 **literal publicado independentemente** antes do `python3`; o argumento `--revision` fixa o snapshot-alvo no mesmo comando. Não executar `/active/scripts/install-global` diretamente: o manifesto local não é raiz de confiança e poderia ser autodeclarado após adulteração. Para versão nova da entrada, atualizar conjuntamente o SHA de bootstrap e seu digest literal nos READMEs após revisão; não derivar o digest do mesmo download nem usar `main` como URL de script. A pessoa aprova um SHA Git completo como alvo (eventualmente descoberto em `main` por pedido natural), não uma string mutável `latest`; `git fetch`/`fsck` e igualdade do SHA validam os objetos, mas **não** atestam que código arbitrário do commit é seguro. Um `--source` de teste nunca entra na receita pública. Alternativas rejeitadas: download por `main` e hash fornecido junto (sem trust anchor), execução direta do ativo local (adulteração), atualizar por pacote de skills.sh (componentes dispersos).

### Tornar atualização uma extensão do instalador

Preservar a API `--agent opencode --revision <SHA>` e as instalações existentes. Sob o lock atual, inspecionar `active` e manifesto antigo, conferir cada item de propriedade e origem via snapshot Git antigo, depois preparar/validar nova versão. Comparar listas de skills para adicionar vínculos somente se o destino estiver vazio e remover somente vínculos cujo target seja exatamente o gerenciado; conflitos de outra origem bloqueiam sem substituição. Trocar somente o ponteiro `active` por rename atômico após preparações, com rollback de vínculos/orientação gerenciados se algo falhar antes; nunca misturar arquivos das duas versões no diretório publicado. O ponteiro é atômico, não uma transação de filesystem sobre `AGENTS.md` e todos os symlinks: documentar janelas transitórias e revalidar o estado final sob lock; consumidores concorrentes podem observar versões diferentes entre duas leituras, mas cada versão completa é coerente. Não apagar versões antigas nem artefatos desconhecidos. Se falha pós-troca for introduzida, tratá-la explicitamente com restauração segura do ponteiro ou relatar estado ativo real sem falso sucesso.

### Relatar estados por evidência, não por intenção

Capturar SHA anterior validado (ou `none`), SHA solicitado e SHA lido do `active/manifest.json` ao final, agente suportado, itens adicionados/removidos e pendências. `updated` só quando pacote e integração gerenciada estão completos; `already current` quando tudo é idêntico; `blocked` quando nenhuma mudança elegível chega à ativação; `partial` quando o pacote global está coerente mas uma migração local explicitamente solicitada permanece pendente (não falsear o estado global). Resultados PT-BR compreensíveis no CLI e procedimentos equivalentes PT-BR/EN no README; nenhum segredo ou caminho de credenciais em saída.

### Limitar migração ao projeto explicitamente identificado

O pacote global é atualizado sem depender da inspeção de todos os projetos. Para pedido natural com projeto corrente identificado, ou opção explícita de inspeção limitada a uma raiz, inventariar somente `./.opencode/skills/`, `.ai-workflow/` e instruções aplicáveis desse projeto sem seguir symlinks desconhecidos. Registrar tipo/proveniência (symlink gerenciado; arquivo com baseline oficial confirmado por SHA; modificado/sem baseline), precedência local sobre global e ação recomendada. Conciliação automática **apenas** para cópia identificada por manifesto/baseline anterior confiável e sem edição local, dentro do escopo autorizado, mantendo regras locais; para outras, deixar intacto com instrução de comparação/decisão posterior. Não declarar migração completa quando outros projetos fechados ou instalações parciais `skills.sh` possam sombrear a global. Instalação legado no destino global como clone `.git` permanece bloqueada e exige realocação/decisão, não substituição. Alternativa rejeitada: varrer HOME e sobrescrever todos os projetos (escopo e propriedade desconhecidos).

### Skill como roteador, sem instalador paralelo

`skills/update-ai-workflow/SKILL.md` distingue pacote global da antiga instalação local/parcial; para a global, resolve alvo aprovado de `main`, confirma bootstrap/digest vigente no README, chama a mesma entrada e apresenta relatório. Se só existe instalação legada, não adivinha migração nem muda seleção parcial: inventaria e pede definição de alvo/escopo. No Web, entrega orientação CLI sem alegar efeitos locais. Atualizar PT-BR/EN em paridade e manter comandos de instalação local legada claramente separados do fluxo global.

## Risks / Trade-offs

- [Bootstrap antigo não entende layout futuro] → validar entrada revisada e publicar SHA/digest correspondente; fixar alvo compatível; não ensinar sintaxe antes de verificá-la.
- [Ponteiro muda enquanto um processo já usa arquivos antigos] → manter `versions/<SHA>` imutáveis e instaladas; nova sessão do agente recomendada para recarregar catálogo; sem remover versão anterior.
- [Links adicionados antes do switch podem estar temporariamente quebrados] → ordem de publicação e rollback exercitados em testes; não declarar atomicidade multipath; nunca publicar bytes parciais em `active`.
- [SHA Git aponta código malicioso ou fonte remota não confiável] → exigir revisão aprovada e digest independente da entrada; Git SHA garante identidade, não endosso do código; recusar fonte arbitrária no comando público.
- [Baseline local incerto ou instrução personalizada] → inspecionar sem overwrite, pendência clara, nenhum `rsync --delete` ou limpeza de repositórios.
- [Falha/aborto entre alterações de múltiplos caminhos] → teste de falhas simuladas nos pontos existentes `skills`/`guidance` e em novos pontos relevantes, reentrada idempotente e diagnóstico de recuperação quando rollback não puder ser confirmado.

## Migration Plan

1. Evoluir entrada e testes num HOME isolado; validar que instalações #50 existentes e manifestos legados ainda atualizam sem recriar diretórios desconhecidos.
2. Publicar receita real com revisão/digest literais da entrada revisada e SHA-alvo explícito, em PT-BR e EN; nenhuma promoção automática de `main`.
3. No pedido autorizado, executar atualização global; conferir manifesto/links finais; diagnosticar o projeto identificado e reconciliar somente cópias inequivocamente pertencentes ao workflow com baseline confiável. Outros projetos permanecem intocados e com diagnóstico pendente.
4. Em erro, manter `active` anterior e relatar o SHA efetivamente ativo; versão anterior continua disponível para reinstalação com entrada confiável. Não remover clones/cópias locais sem autorização e comparação.
