# m2t-worktree-lifecycle Specification

## Purpose
Vincular a retenção e a limpeza de instâncias de testes M2T ao ciclo comprovado do trabalho em uma worktree, sem confundir posse do código, execução do sandbox e prova de testes.

## Requirements

### Requirement: Inventário de sandbox associado ao trabalho
O workflow SHALL registrar na evidência/handoff existente a worktree e cada seleção M2T conhecida usada pelo trabalho, inclusive o escopo e token GraphQL quando aplicável. Inventário M2T isolado MUST NOT ser tratado como prova de posse do workflow.

#### Scenario: Primeiro uso e retomada no mesmo checkout
- **WHEN** um worker usa pela primeira vez testes M2T numa worktree e outro worker assume o mesmo trabalho
- **THEN** o handoff conserva o caminho, a seleção conhecida e a identificação de execução; a retomada reconcilia estado e dono sem criar registry concorrente

#### Scenario: Seleção GraphQL não inventariada
- **WHEN** há uma instância GraphQL listada pelo produtor mas nenhuma prova de que pertença à entrega
- **THEN** o workflow não a inclui em limpeza automática e registra incerteza para reconciliação

### Requirement: Retenção durante trabalho não concluído
O workflow SHALL reutilizar a interface pública M2T sem executar `reset` ou `down` automaticamente ao término de teste, comando, commit, Apply, sessão, pausa ou handoff. Falhas, interrupção, PR aberta e bloqueios MUST reter as instâncias próprias e referências para retomada.

#### Scenario: Execuções consecutivas sem alteração de inputs (T1)
- **WHEN** duas seleções de teste rodam no mesmo checkout sem mudança relevante
- **THEN** o workflow não impõe teardown nem bypass de preparação; o M2T decide se pode reutilizar instalação, vendor e baseline

#### Scenario: Planejamento, Apply e correção (T2)
- **WHEN** a mesma worktree passa entre planejamento, Apply e correção de PR
- **THEN** as seleções M2T comprovadas permanecem associadas ao trabalho e o novo worker verifica posse do checkout e prova no código atual, sem atribuir ao lock M2T a posse de escrita

#### Scenario: Pausa, crash, falha ou PR aberta (T3)
- **WHEN** a execução termina sem entrega elegível ou sua conclusão não é confirmada
- **THEN** instâncias e referência do checkout são retidas com motivo e próxima ação, sem presumir que container ativo ou ausente prova término do worker

### Requirement: Prova atual e diagnósticos efetivos
O workflow SHALL distinguir identidade/estado do sandbox de evidência de teste verificável no código atual. SHALL consumir saída operacional resumida por padrão e consultar log privado somente quando necessário; erro de execução ou captura MUST NOT virar aprovação por ter run ID, contagem, arquivo ou container.

#### Scenario: Código alterado após teste
- **WHEN** código ou seleção relevante muda depois de uma prova
- **THEN** apenas obrigações afetadas são revalidadas, sem skip inseguro ou teardown automático

#### Scenario: Resultado e log privado
- **WHEN** `test`/`graphql` retorna ID e estado resumido ou `unit`/`exec` retorna recibo e caminho de log
- **THEN** o workflow registra saída/código e evidência pertinente, usa `runs show --json` para run registrado quando necessário e consulta trecho relevante do log em falha, sem equiparar recibo ou status a prova aprovada

### Requirement: Closeout condicionado a elegibilidade e posse
Somente após entrega/merge e kaizen verificados, evidência durável e ausência comprovada de owner, teste ou processo dependente, o workflow SHALL limpar instâncias exclusivamente pertencentes à worktree por interface pública M2T antes de remover o checkout elegível. Dúvida ou falha MUST manter checkout e referência para nova tentativa.

#### Scenario: Outro worktree e cache compartilhado (T4)
- **WHEN** a entrega desta worktree está concluída e outro trabalho ainda usa M2T
- **THEN** somente instâncias próprias comprovadas são encerradas e o cache vendor e os recursos do outro worktree permanecem

#### Scenario: Lock, owner ativo ou falha de down (T5)
- **WHEN** há processo/owner ainda dependente, `down --no-wait` encontra lock ou qualquer remoção falha
- **THEN** o checkout não é removido, a falha/código e o escopo pendente são registrados e não se tenta limpeza manual abrangente

### Requirement: Seleção exata e ordem da limpeza
O workflow SHALL tratar integração padrão e cada token GraphQL comprovado como seleções distintas; MUST usar a assinatura pública efetiva com `--worktree` explícito fora do checkout e terminar todas as seleções próprias antes de perder o caminho de resolução. MUST NOT usar `gc` global, filtro por prefixo/idade ou inferência de tokens desconhecidos.

#### Scenario: Integração e múltiplos GraphQL (T6)
- **WHEN** a worktree tem instância de integração e duas seleções GraphQL próprias com tokens conhecidos
- **THEN** o fechamento considera separadamente integração e cada `--scope graphql --sandbox-id <token>`; seleção não comprovada permanece, e o checkout não é removido enquanto o fechamento seguro estiver incompleto

#### Scenario: Worktree removida antes de resolver seleção
- **WHEN** a operação M2T ainda necessita da worktree existente para identificar a instância
- **THEN** a remoção Git aguarda o resultado do cleanup M2T, preservando referência e motivo caso não se conclua

### Requirement: Recursos efêmeros continuam internos ao produtor
Retenção de sandbox de integração/GraphQL MUST NOT impedir a limpeza normal dos recursos descartáveis `unit`/`exec` sob suas próprias regras e recibos; caches compartilhados MUST ser preservados.

#### Scenario: Término de unit ou exec (T7)
- **WHEN** `unit` ou `exec` encerra e limpa sua cópia/volume efêmero
- **THEN** o workflow não impede o cleanup interno nem invoca `down` de integração/GraphQL por causa dessa execução; log privado e cache compartilhado seguem seus contratos próprios

### Requirement: Resultado de closeout visível e distribuído
O workflow SHALL registrar por issue worktree/seleção removida ou retida, motivo e ação pendente, e distribuir a orientação pelas fontes globais e referências oficiais, sem impor política de cleanup em repositório consumidor externo como efeito colateral.

#### Scenario: Cleanup parcial e handoff
- **WHEN** uma seleção própria é encerrada e outra falha
- **THEN** o resumo diferencia ambas, conserva checkout/referência e não anuncia closeout total
