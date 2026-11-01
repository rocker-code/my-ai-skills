---
name: roadmap-status
description: Give a concise, evidence-based project or multi-repository roadmap snapshot with current focus, delivery status, blockers and one next step. Use for "Charles, me situa", "onde estamos", "me perdi no roadmap", "como estamos no MVP", "o que faço agora" or a quick milestone overview. Works in Web agents and CLI; read-only. Use milestone-progress instead when the user explicitly requests a detailed per-issue milestone report or timings.
---

# Roadmap status

Situar o usuário no produto sem despejar o backlog. Consultar evidências atuais, resumir em uma tela e recomendar uma ação por vez. Responder no idioma do usuário.

## Resolver escopo e acesso

- Reutilizar o produto, repositórios e objetivo explicitamente identificados na conversa ou nos registros do projeto. No CLI, conferir a identidade do checkout e suas instruções; um checkout isolado não representa automaticamente todo o produto. Perguntar apenas se houver ambiguidade que impeça a consulta.
- Usar as mesmas instruções nos dois ambientes: no Web, ler pelo conector GitHub autorizado; no CLI, usar integração GitHub ou `gh` autenticado. Não exigir checkout, OpenSpec, scripts auxiliares ou ferramentas de escrita para uma consulta. Não prometer instalação nativa a partir de um link Markdown.
- Consultar roadmap/Project/documentos existentes, milestones e decisões aprovadas para identificar MVP, ordem e foco. GitHub é a fonte de verdade; conversa e memória dão contexto, não comprovam andamento atual. Prioridade é uma decisão do produto, não consequência da numeração das issues, atividade recente ou ordem dos milestones.
- Manter o escopo solicitado: produto, MVP, repositório ou milestone. Para uma visão do MVP, conferir a classificação das entregas/issues: um milestone misto pode conter MVP e pós-MVP. Se não houver definição verificável, informar isso brevemente e apresentar apenas o recorte conhecido, sem inventar inclusão.

## Reconstituir o estado

1. Ler o plano vigente e inventariar milestones, issues abertas/fechadas e PRs relevantes ao recorte. Paginar as consultas necessárias; não tratar uma primeira página ou busca limitada como inventário completo. Ler comentários/decisões e dependências das entregas ativas, bloqueadas ou candidatas ao próximo passo. Aprofundar código/contratos apenas quando necessário para resolver uma dúvida concreta.
2. Conferir vínculos issue–PR por referências explícitas e estado de merge; título parecido não comprova associação. Distinguir PR ativa, substituída, cancelada e entrega parcial/revertida. Issue fechada como duplicada, cancelada ou sem entrega verificável não significa funcionalidade pronta. Em dependências entre repositórios, verificar o produtor e a disponibilidade do contrato antes de recomendar a integração consumidora.
3. Classificar em linguagem simples: **Concluído**, **Em andamento**, **Em revisão**, **Bloqueado**, **Aguardando** ou **Não verificado**. Usar Concluído para escopo entregue com evidência atual; para código, conferir merge e conclusão da issue, além dos critérios restantes. Separar código integrado de release, deploy e validação em produção. Para trabalho sem código, usar os critérios da própria entrega. CI verde sozinho não comprova entrega nem prontidão para merge; conferir requisitos e head atuais somente quando essa afirmação for necessária.
4. Agregar por entrega/funcionalidade quando isso explicar melhor o roadmap; usar frentes/repositórios quando o pedido for sobre integração. Uma frente com pendências é parcial: não marcar todo o Magento como concluído porque uma funcionalidade terminou. Não esconder bloqueios relevantes na agregação.
5. Identificar foco aprovado e uma próxima ação elegível considerando dependências, conclusão de trabalho iniciado, riscos e capacidade de um desenvolvedor. Se não houver foco aprovado, escrever **Foco sugerido**, com motivo curto; não alterar prioridades. Se tudo estiver bloqueado, recomendar a ação para destravar. Se faltar evidência, recomendar verificá-la antes de executar.
6. Comparar com o passado apenas com relatório/registro datado verificável e mesmo escopo, considerando mudanças de escopo. Sem referência, mostrar somente a fotografia atual. Não criar histórico, arquivos, comentários ou baseline automaticamente.

## Mostrar em uma tela

Por padrão, limitar a resposta a cerca de **180 palavras**, com no máximo **5 linhas de tabela**. Consolidar entregas relacionadas; indicar em uma frase quando mostrar apenas o foco atual, mantendo bloqueios materiais visíveis. Não reproduzir todas as issues, métricas, logs, testes, SHAs ou estados internos do workflow. Incluir links nas entregas e na próxima ação, sem uma lista separada de fontes.

Usar este formato, preenchendo apenas com evidências reais:

**📍 Onde estamos:** [objetivo e situação em uma frase].  
**Foco atual:** [entrega aprovada; usar “Foco sugerido” se for recomendação].

| Entrega / frente | Situação | Falta |
|---|---|---|
| [Nome com link] | 🟡 Em andamento | [pendência objetiva] |

**👉 Próximo passo:** [uma ação concreta com link e motivo curto].  
**🚧 Depende de você:** [decisão material, ou “nenhuma decisão identificada”].  
*Consultado em [data/hora e fuso do usuário]. [Limitação relevante, se houver.]*

- Manter texto junto aos ícones para não depender de cor. Usar 🟢 concluído, 🟡 andamento/revisão, 🔴 bloqueado, ⚪ aguardando/não verificado.
- Em “o que faço agora?”, priorizar uma recomendação curta e usar tabela somente se ajudar. Aprofundar em detalhes quando solicitado. Acionar `milestone-progress` apenas para o relatório detalhado de milestone, se disponível; não carregá-lo automaticamente para a visão rápida nem impor suas tabelas completas a esta resposta.
- Evitar percentuais por padrão. Se solicitados, calcular apenas com inventário completo e explicitar o denominador e que é contagem de itens, não esforço. Sem acesso/páginas suficientes, indicar **visão parcial** ou **não verificado**; nunca afirmar ausência de bloqueios ou decisões no escopo não consultado. Sem acesso atual, dizer “não consegui verificar agora”, separar último estado conhecido da situação atual e ainda oferecer uma próxima verificação útil.

## Limites

A consulta apenas lê e recomenda. Não iniciar `milestone-orchestrator`, implementar, rodar testes, limpar worktrees, editar issues/roadmap, fechar itens, fazer merge, release, deploy ou agendar tarefas. Um pedido posterior explícito de execução segue a skill correspondente e as autorizações existentes. Não prometer monitoramento em segundo plano. Não manter um roadmap paralelo baseado apenas na memória do agente.
