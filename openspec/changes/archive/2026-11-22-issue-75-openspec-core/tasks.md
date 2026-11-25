# Tasks

## 1. Checkpoint single-issue

- [x] 1.1 Inventariar consumidores ativos dos wrappers e salvaguardas não nativas; verificar revisão base, perfil OpenSpec e referências rastreadas antes de remover arquivos.
- [x] 1.2 Reduzir protocolo e adaptador ao ciclo oficial e integrações necessárias; migrar audit/ready/explore e entradas públicas sem repetir lifecycle; verificar cenário simples e replanejamento material.
- [x] 1.3 Consolidar revisão independente e loop de correção/merge no HEAD final; preservar testes/CI, proteção e modos auto/manual; verificar cenários HEAD igual, push e check falho.
- [x] 1.4 Adicionar simplify opcional pequeno e três princípios de engenharia; verificar preservação de contratos/erros e ausência de estágio obrigatório com cenários de código claro e melhoria concreta.
- [x] 1.5 Migrar comunicação dos consumidores para corpo da issue/OpenSpec/PR/checks, retirando comentário operacional e Kaizen obrigatório; verificar que blockers reais e discussões de review continuam possíveis sem apagar história.
- [x] 1.6 Migrar referências/gerador/testes e README PT/EN do single-issue; sincronizar referências, verificar idempotência/links e rodar os testes direcionados afetados antes do próximo checkpoint.

## 2. Checkpoint scheduler sequencial

- [x] 2.1 Reduzir milestone-orchestrator a escopo, dependências, uma issue ativa e ownership; verificar forward-test com issues independentes e consumidor bloqueado, sem planejamento/execução paralelos entre issues.
- [x] 2.2 Migrar retomada e consultas de status para fontes Git/GitHub/OpenSpec/runtime existentes; verificar interrupções após Propose/Apply, PR existente e blocker estacionado sem duplicação nem resultado inventado.
- [x] 2.3 Atualizar docs/protocolos/consumidores de fila, housekeeping e evolução; aplicar o delta de `m2t-worktree-lifecycle` retirando apenas a dependência de Kaizen e verificar next issue/cleanup elegível sem Kaizen, mantendo todos os demais gates e ausência de issues cosméticas/duplicadas.
- [x] 2.4 Migrar referências e testes do scheduler; sincronizar/idempotência, verificar links e executar cenários controlados com subagentes apenas dentro da issue ativa.

## 3. Integração final

- [x] 3.1 Executar suíte unittest obrigatória e testes de distribuição/ownership/evidence; resolver regressões e registrar resultados reais, sem métricas de tempo do workflow.
- [x] 3.2 Inspecionar suporte oficial de Verify, habilitá-lo oficialmente se suportado mas ainda não gerado, invocá-lo por padrão e relatar limitação real ou falha de habilitação com precisão; validar mudança com `openspec validate issue-75-openspec-core --strict`, tratar findings e obter revisão independente do candidato final.

## Workflow follow-up

- Arquivar pelo OpenSpec oficial no mesmo branch após implementação, testes, validação e revisão aplicáveis; inspecionar spec sincronizada e archive.
- Preparar PR da issue #75 com provas reais, limitações e remoções; confirmar checks e merge autorizado antes de iniciar #76, ou estacionar explicitamente quando houver bloqueio real.
