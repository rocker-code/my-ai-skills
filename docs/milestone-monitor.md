# Milestone Monitor operacional

`aew dashboard`: TUI read-only Python 3/curses/SQLite (stdlib). A
[demo offline](../examples/milestone-monitor/) continua separada com **DADOS
SIMULADOS**. O painel operacional não inventa atividade, tempos ou aprovação.

## Instalar e configurar

Em um clone **retido**, não uma worktree a remover:

```sh
scripts/install-aew --bin-dir "$HOME/.local/bin"
aew --help
```

Inclua esse bin no PATH por sua configuração, se necessário. O instalador só cria
symlink, recusa destino diferente, não usa sudo nem altera shell rc. O launcher
resolve seu próprio caminho e funciona de qualquer diretório. Para desinstalar,
confira `readlink ~/.local/bin/aew` e remova **somente esse symlink**; mantenha
dados/config. Também distribuído via `scripts/sync-plugin` em
`plugins/my-ai-skills/scripts/`.

Crie `$XDG_CONFIG_HOME/aew/config.json` (fallback `~/.config/aew/config.json`):

```json
{
  "schema_version": 1,
  "targets": [{"repository": "owner/repo", "milestones": [1, 2]}],
  "runtime": {"enabled": false, "expected_version": "2.2.5"},
  "timing": {"github_interval": 60, "runtime_interval": 15,
             "github_ttl": 180, "activity_ttl": 45, "timeout": 10}
}
```

Substitua alvos por repositórios/números autorizados. Só GitHub.com, inteiros
positivos; duplicatas consolidadas. Sem alvos/config = vazio com orientação,
**não descoberta**. Tempos são segundos positivos até 86400, defaults acima.
Use `gh` já autenticado para atualizar GitHub; não coloque credenciais na config.

```sh
aew collect --once --config /caminho/config.json --state-dir /caminho/cache
aew dashboard --config /caminho/config.json --state-dir /caminho/cache
aew dashboard --offline --no-color --ascii
```

`collect --once` emite projeção JSON de metadados, saída não zero em falha de fonte.
`dashboard` exige TTY, inclusive tmux; não exige agente aberto. Config/caminhos
explícitos são opcionais. UI em pt-BR, nomes próprios/branches preservados.

## Arquitetura, estado e privacidade

GitHub paginado → snapshots SQLite → projeção/overlay OpenCode → reducer/curses.
Inventário por repo, comentários por issue e runtime são fontes independentes.
Coleta em thread, fila limitada, refresh coalescido e subprocessos com timeout;
sem requisição por frame, daemon ou plugin obrigatório. Sair fecha só o painel,
**nunca agentes, testes ou jobs**.

Cache schema 1 em `$XDG_STATE_HOME/aew/monitor.sqlite3` (fallback
`~/.local/state/aew/monitor.sqlite3`). Novos diretório/arquivo: 0700/0600; não muda
permissões existentes. SQLite serializa transações curtas com busy timeout; rede
fora de locks e geração contra resposta antiga. Falha de página/JSON/rede/escrita
mantém snapshot anterior. Banco futuro/corrompido é recusado, nunca apagado,
recriado ou rebaixado automaticamente. Preserve cópia e investigue espaço,
permissões/versão antes de intervenção. Sem migração de comentários GitHub.

- **GitHub:** identidade repo/número, milestone e fechamento. PRs são candidatas
  pela timeline, vinculadas somente após referência oficial de fechamento; múltiplas
  são ambíguas. Merge/head são fatos separados. PRs não entram no total de issues.
- **Workflow v1 (#16):** parser/resumo/correlação canônicos, sem logger paralelo.
  Upsert comment ID/hash inclui last_seen_at; eventos mantêm ordem efetiva estável.
  Run mais recente por criação UTC, desempate run ID/comment ID, conflitos visíveis;
  histórico selecionável. Worktree movida/reabertura não apaga histórico local.
- **OpenCode:** overlay de atividade foreground, não prova de processo filho,
  teste/CI, aprovação ou conclusão de etapa.

Percentual = **issues fechadas/total**, nunca estimativa de implementação. Vazio:
0/0 e percentual indisponível. Fechada não prova entrega mergeada/verificada;
PR mergeada com issue aberta não aumenta conclusão. Reabrir/mover aplica próximo
inventário completo. Contagem exclusiva: fechada → concluída; espera → bloqueada
(humano distinto); falha/interrupção relevante → bloqueada; aberta confirmada
recentemente → executando; demais → pendente/desconhecida/inativa/reconciliação.
Espera vence worker paralelo; terminal vence running posterior; detalhes preservam
execuções distintas. Rework não herda estado/aprovação de incarnação anterior.

Cache reaberto não confirma atividade. Frescor por fonte, timestamps UTC, TTL
workflow/runtime 45s/GitHub 180s por padrão. Erro/cache não renova confirmação;
horário futuro não confirma. Tempos são canônicos registrados; trabalho paralelo
somado não é calendário. Relatório presente/evidence ref não implica aprovação.

Só allowlist de metadados; sem prompts/mensagens/tokens/logs/payloads arbitrários.
Títulos/controles ANSI sanitizados antes do cache/render. argv fixo sem shell;
conteúdo externo nunca vira instrução. Erros públicos categorizados (ausente,
não autorizado, negado, rate limit, timeout, resposta/contrato inválido,
armazenamento), nunca stderr bruto. Retry-After/reset quando fornecidos, senão
backoff exponencial limitado; `r` não fura backoff.

## Runtime opt-in e continuidade

Contrato **somente OpenCode 2.2.5**, CLI e servidor. Produtor oficial
`anomalyco/opencode@9bbb8ce18c80f099e0e448775f59d965ead40a21`, schema
`packages/protocol/openapi.json`, SHA-256
`92cc33ef9a107c8af6295e6fcbdf6d339d4374955910924456bd91a76844a5db`.
Outra versão exige nova conferência; sem fallback V1/prosa/banco interno.

Habilite `runtime.enabled: true`; `runtime.server` opcional HTTP(S) sem userinfo,
query ou fragment usa o mesmo contexto/auth oficial no bind/coleta. Omitido =
descoberta do serviço compartilhado pelo CLI; **nunca --standalone**.
IDs não vinculados são descartados. Após collect com run/incarnação aberta:

```sh
aew bind --issue https://github.com/owner/repo/issues/7 \
  --run-id wf-EXISTENTE --stage apply --worker-id worker-a \
  --execution-kind worker --execution-id EXECUCAO-EXISTENTE \
  --session-id ses_EXISTENTE --worktree /caminho/checkout --branch minha-branch
aew unbind --issue https://github.com/owner/repo/issues/7 \
  --run-id wf-EXISTENTE --stage apply --worker-id worker-a \
  --execution-kind worker --execution-id EXECUCAO-EXISTENTE
```

Substitua placeholders por IDs reais; ambos aceitam `--config`/`--state-dir`.
Branch opcional só é salva após verificar Git. Bind declara sessão executora
daquele worker. Teste/job/CI vinculado mostra agente ativo, mas só observação
própria canônica confirma o filho. Vínculo terminal/ambíguo, repo/checkout incorreto
ou sessão já vinculada a outra incarnação é recusado sem substituir anterior.
Unbind também remove vínculo terminal, preservando histórico.

Cada ciclo confirmatório revalida server.info, session.get, location.get explícito
e identidade Git. location.directory já é absoluto, não concatena subpath nem
aceita projectID/canonical compartilhado como prova de checkout. Mudar
localização/processo/contexto invalida vínculo até novo bind. 404 ausente,
inativa e falha de API são distintos. Amostras não são atômicas: movimento entre
consultas aparece na próxima. outcome da sessão não encerra workflow.

OpenCode/Codex continua pelas skills e workflow-event do coordenador, escritor
único. O painel não escreve eventos, aprova testes, controla agentes, fecha issues
ou faz merge. Codex produz v1, sem adaptador runtime nativo. Notificações/iPhone,
custos/tokens e web fora do MVP. Sem dependência Figma: curses, não redesign web.

## Teclas e régua

↑/↓ ou j/k navegar; Enter/Espaço sanfona/detalhes; a/c expandir/recolher todos;
f todas/executando/pendentes/bloqueadas/concluídas; v compacto/detalhado; r refresh;
[/] histórico de runs; PgUp/PgDn rolar detalhes; q/Esc sair. Preferências por
identidade persistem; histórico muda só detalhes, nunca totais do run mais recente.

Auditoria → Explorar → Decisões → Proposta → Revisar proposta → Aplicar → Testes →
**Verificar/arquivar** → Preparar PR → Auditar PR → CI → Merge → Kaizen.
`+` encerrada/concluída registrada; `>` atual registrada (não prova running);
`.` sem registro; `!` falha/interrupção; `?` reconciliação; `B` bloqueio; `H` humano.
Anteriores não viram sucesso por posição. Etapa desconhecida fica «outra».
Viewport inclui etapa atual; largura Unicode, fallback ASCII/sem cor, contadores
estreitos C/E/P/B. Testes stdlib: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
discover -s tests`. Fixtures artificiais não são smoke de integração real.
