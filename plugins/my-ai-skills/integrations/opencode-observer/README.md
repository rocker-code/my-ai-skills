# Ponte opcional OpenCode

Cliente oficial **2.2.5**, Node >=22. Não é um serviço, publicador GitHub ou
controlador de agentes. Não altera configuração do OpenCode nem inicia o servidor.
O monitor Python permanece utilizável sem Node e sem este pacote.

**Smoke real controlado: executado em 2026-11-09 na issue #440 com autorização explícita — não ativar em outros ambientes sem autorização.** A ponte usa a opção
pública `fetch` do cliente oficial para enviar a allowlist fixa de tipos na
requisição HTTP; o filtro local de alto nível 2.2.5 sozinho não seria suficiente.
O teste do pacote instalado verifica a query recebida pelo servidor simulado,
autenticação, cancelamento e IPC sanitizado. A assinatura recusa redirects.
O comando Python `aew observe` supervisiona a ponte em foreground. Correlação,
outbox/publicação e vínculo são caminhos separados; testes simulados não validam
integração real sozinhos. O smoke autorizado está documentado em
`openspec/changes/integrate-opencode-workflow-instrumentation/verification.md`;
a ativação operacional geral continua separada e depende de autorização.

## Instalação voluntária

No clone retido, somente quando desejar habilitar a ponte:

```sh
cd integrations/opencode-observer
npm ci --ignore-scripts --no-audit --no-fund
npm test
```

O lockfile fixa a árvore instalada. Não distribuir `node_modules`. Os testes
usam fixtures sintéticas e servidor HTTP simulado com o cliente instalado; não
atestam integração real. O teste Python de proveniência é opt-in via
`OPENCODE_CONTRACT_SOURCE`, diretório contendo fontes públicas do commit
`anomalyco/opencode@9bbb8ce18c80f099e0e448775f59d965ead40a21`.

## Protocolo versão 1

`node integrations/opencode-observer/main.js < /caminho/ponte.json`
recebe **um** JSON limitado a 16 KiB pelo stdin, terminado por EOF. Exemplo
sintético (substituir por vínculos previamente validados; não descobre sessões):

```json
{
  "version": 1,
  "context": {"endpoint": "shared-discovery", "version": "2.2.5", "pid": 1234},
  "bindings": [{
    "session_id": "ses_fixture", "revision": "rev_fixture",
    "worktree": "/fixture/worktree", "bound_at": "2026-11-08T00:00:00Z"
  }]
}
```

O supervisor fornece o PID/contexto e a revisão atuais. Mudanças na allowlist
exigem encerrar somente esta ponte e iniciá-la novamente, invalidando continuidade.
Não usar sessão coordenadora como fallback. Sem vínculos a ponte recusa iniciar.

Descoberta compartilhada usa exclusivamente `Service.discover({version:'2.2.5'})`.
Servidor explícito acrescenta `server` e usa a mesma URL em `context.endpoint`.
Credenciais vêm **somente do ambiente herdado** (`OPENCODE_PASSWORD`, fallback
`OPENCODE_SERVER_PASSWORD`); usuário `opencode`, headers por `Service.headers`.
Não passar senha em argv, URL, JSON ou arquivo. Credencial negada/ausente não
provoca troca de servidor. Não ler arquivos privados de credenciais.

Saída stdout: um objeto NDJSON por evento selecionado, até 16 KiB, com
`version`, `type`, `event_id`, `created` (epoch UTC em **milissegundos**),
`received_at` (UTC ISO), `context`; fatos de sessão incluem `session_id` e
`binding_revision`. Execuções incluem `sequence`; pedidos incluem `request_id`;
resposta de permissão inclui `resolution` (`answered`/`rejected`).
`server.connected` e `location.shutdown` são marcadores sem identidade de sessão.
Nenhum texto, erro remoto, argumento, resposta humana ou metadata arbitrária passa
para stdout/stderr. stderr contém somente `{version:1,category:...}`.

Tipos: `session.execution.started/succeeded/failed/interrupted`,
`permission.asked/replied`, `form.created/replied/cancelled`, `session.moved`,
`location.shutdown`, além do marcador obrigatório `server.connected`.
Sessão alheia, tipo não permitido e evento anterior ao bind são descartados.
Localização/contexto divergente, envelope inválido/grande e perda de fluxo
encerram a ponte com falha categorizada. `SIGINT`/`SIGTERM` cancelam somente a
assinatura; nenhum agente/servidor é interrompido. Backpressure de stdout é
respeitado; saturação do cliente oficial falha e exige reconciliação.

Fluxo **live-only**, sem replay ou reconexão automática: o supervisor deve
reconciliar atividade/permissões/formulários por consulta oficial após início,
marcador conectado, erro ou reinício. Não deduzir horário de resposta perdida,
conclusão de etapa ou aprovação de testes a partir destes eventos.

Sem dependências instaladas a ponte está indisponível; não instalar ao abrir o
dashboard. Usar snapshots CLI em modo degradado, sem alegar cobertura contínua.
Instalação/ativação real e smoke com sessão real exigem autorização explícita.
