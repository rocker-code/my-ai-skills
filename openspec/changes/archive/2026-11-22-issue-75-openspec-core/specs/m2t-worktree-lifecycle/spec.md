# Spec Delta

## MODIFIED Requirements

### Requirement: Closeout condicionado a elegibilidade e posse
Somente após entrega/merge verificados, evidência durável e ausência comprovada de owner, teste ou processo dependente, o workflow SHALL limpar instâncias exclusivamente pertencentes à worktree por interface pública M2T antes de remover o checkout elegível. Dúvida ou falha MUST manter checkout e referência para nova tentativa.

#### Scenario: Outro worktree e cache compartilhado (T4)
- **WHEN** a entrega desta worktree está concluída e outro trabalho ainda usa M2T
- **THEN** somente instâncias próprias comprovadas são encerradas e o cache vendor e os recursos do outro worktree permanecem

#### Scenario: Lock, owner ativo ou falha de down (T5)
- **WHEN** há processo/owner ainda dependente, `down --no-wait` encontra lock ou qualquer remoção falha
- **THEN** o checkout não é removido, a falha/código e o escopo pendente são registrados e não se tenta limpeza manual abrangente

#### Scenario: Entrega elegível sem Kaizen
- **WHEN** entrega/merge e evidência durável estão verificados, não há owner/teste/processo dependente e Kaizen não foi executado
- **THEN** o workflow pode realizar cleanup elegível com as mesmas verificações de posse e seleção, sem aguardar Kaizen
