# Tasks

## 1. Remover coletor e migrar consumidores

- [x] 1.1 Remover quatro scripts/módulos legados e três suítes exclusivamente dependentes deles; confirmar ausência de imports/callers ativos e preservar workflow-evidence/worktree-registry e suas suítes.
- [x] 1.2 Atualizar distribuição/instalador, fixtures de update e smoke dos helpers mantidos; provar ausência dos arquivos retirados e update preservando arquivos desconhecidos/personalizações. Publicar source imutável e repinar bootstrap/testes com SHA remoto real e digest antes da validação final.

## 2. Manter retomada e contratos coerentes

- [x] 2.1 Aplicar os deltas de specs e esclarecer histórico legado/ruptura nos README PT/EN e documentação ativa necessária; sincronizar referências existentes e verificar links sem alterar archives prévios.
- [x] 2.2 Conferir cenários de worker desconhecido, callback de outra execução, prova incompleta e fila sequencial nas instruções mantidas; verificar que progresso e Kaizen não leem métricas, sem criar coletor substituto.

## 3. Verificar integração

- [x] 3.1 Executar suíte pertinente e conferir seus exits e evidência real; executar Verify oficial e validação estrita, corrigindo achados relacionados. A suíte completa no candidato final limpo permanece obrigatória no follow-up abaixo.

## Workflow follow-up

- Arquivar pelo OpenSpec oficial e inspecionar sync; remover somente o arquivo ativo workflow-metrics vazio se remanescente. Preservar arquivos históricos e aprovar revisão independente do HEAD final antes da entrega.
- Executar a suíte completa no HEAD final limpo após archive e antes da entrega, registrando comando, log, exit e identidade; nenhuma alteração de código durante a execução.
- Parent publica PR e verifica merge/fechamento; testes são vinculados ao HEAD publicado ou árvore equivalente comprovada, sem inventar aprovação automática de helper.
