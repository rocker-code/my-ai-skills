# Proposal

## Why

O workflow já preserva a worktree entre sessões, mas não vincula explicitamente a retenção e o encerramento do sandbox M2T a esse ciclo. Limpar ao fim de uma execução destrói recursos reutilizáveis e pode apagar um sandbox ainda necessário; os produtores M2T #46 e my-ai-skills #69 já foram entregues e permitem planejar o consumo da interface efetiva.

## What Changes

- Identificar, registrar e revalidar o sandbox/seleções pertencentes à worktree no handoff e inventário já existentes; reutilizar comandos públicos M2T sem `down`/`reset` automático por teste, commit, sessão, pausa ou troca de agente.
- Manter instâncias e referências em PR aberta, falha, interrupção ou incerteza; atualização de código invalida a prova afetada, não autoriza skip de teste nem descarte indiscriminado.
- No closeout após entrega e kaizen, confirmar posse, ausência de dependências ativas e elegibilidade segundo `WORKTREES`; encerrar somente integração e cada seleção GraphQL conhecida e comprovadamente própria, com `--worktree` explícito fora do checkout, antes de remover o diretório. Falha/lock retém a worktree e registra motivo e próxima ação.
- Consumir resumos limitados, códigos de saída e logs privados do contrato M2T entregue; não interpretar `status`, recibo ou run ID isolado como prova de posse ou teste aprovado. Preservar cache vendor compartilhado e cleanup interno de `unit`/`exec`.
- Atualizar instruções do pacote global, referências geradas e exemplos aplicáveis, sem mudar código M2T, Magento, política de merge, gates, permissão ou topologia de instâncias; registrar interface para o consumidor Rancho #457 sem editar o repositório dele.

## Capabilities

### New Capabilities

- `m2t-worktree-lifecycle`: retenção, reconciliação e closeout seguro de sandboxes M2T vinculados ao trabalho em uma worktree.

### Modified Capabilities

Nenhuma. `checkout-write-reservation` continua responsável somente pela posse do checkout; o lock M2T continua responsabilidade do produtor.

## Impact

`protocol/WORKTREES.md`, instruções de planejamento/Apply/PR/correção/retomada/housekeeping em `skills/*/SKILL.md` e `protocol/AI_WORKFLOW.md` quando conflitantes, referências sincronizadas por `scripts/sync-skill-references`, documentação de distribuição e testes existentes de protocolo/instalação. Produção externa: M2T #46/PR #48 merge `04f027277e127890beb4058817b6d0634ce67645`; launcher #69/PR #73 merge `02194d7aaa343a481e5bff47ababfc3c669fedc1`; #71 OpenSpec 2.0 merge `5e33688d2a9db702e6bd0f2027d778f3baebdf35`. Contrato consumidor congelado pelo handoff final informado para T1–T7; #47 `db:sql` e unificação de instâncias não são pré-requisitos. Sem novos serviços, registry paralelo ou alteração da CLI M2T.
