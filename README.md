# Ticktask

Aplicação pessoal para gerir projetos, tarefas e backlog, e registar o tempo gasto em cada tarefa.

## Problema

Não tenho um sítio único para os meus projetos e tarefas, para os bugs e sugestões que me chegam por email e para o tempo que gasto em cada coisa. Sem isso não sei quanto demoro de facto nem o que tenho pendente.

## MVP (Must)

- **Projetos:** criar, editar, arquivar.
- **Tarefas em kanban:** tarefas dentro de um projeto, organizadas em colunas (etapas), com drag and drop entre colunas e dentro da mesma coluna.
- **Descrições:** texto simples no projeto e na tarefa, guardado já como markdown (ver "Decisões tomadas").
- **Timer normal:** start, pause e stop por tarefa, com arredondamento das horas no stop. Só um timer ativo de cada vez. Regras em [docs/timer.md](docs/timer.md).
- **Registo de tempo manual:** adicionar ou corrigir registos à mão.
- **Totais:** horas por tarefa e por projeto.

## Should

- **Milestones:** marcos por projeto, com prazo, que agrupam tarefas (como no Odoo).
- **Pomodoro:** foco, pausa e pausa longa configuráveis, com notificação com a app aberta. Estimativa da tarefa em pomodoros, com contador feitos / estimados (ex: 3 / 4).
- **Markdown estilo GitHub** nas descrições: cabeçalhos, listas, checkboxes (só visualização).
- **Documentos:** separador com documentos gerais e guidelines, em markdown.
- **Backlog:** tarefas do tipo bug / sugestão, criadas à mão, que depois passam para um projeto.
- **Datas limite:** data limite numa tarefa e email de aviso quando se aproxima.

## Could

- Marcar checkboxes das descrições com um clique.
- Editor visual (WYSIWYG) para as descrições, estilo Odoo.
- Vista Gantt das tarefas de um projeto (só visualização, com base em data de início e data limite).
- Notificações do pomodoro com a app fechada (Web Push).
- Comentários com data nas tarefas.
- Reordenar e personalizar colunas, etiquetas, filtros e pesquisa.
- Relatórios de tempo por semana/mês.

## Won't (v1)

- Multi-utilizador, equipas e permissões.
- SSO e login com Google.
- Dependências entre tarefas (no Gantt).
- Faturação (emitir faturas a partir das horas).
- App mobile nativa (antes disso: web responsiva e PWA).
- Anexos em tarefas.

## Fases futuras

1. **Utilizadores:** contas na app. Cada projeto já tem um dono (`owner`) desde a v1, para não ter de refazer o modelo.
2. **SSO com a app de finanças:** contas partilhadas entre as apps, com contas próprias e login Google como opção. Decisão a registar num ADR próprio.
3. **Tickets vindos de outras apps:** os forms de bugs e sugestões das minhas apps criam entradas no backlog através de um endpoint da API (ex: `POST /api/tickets/`), com uma chave por app.

## Decisões tomadas

- **Origem dos bugs e sugestões:** um form que envia para o meu email através do Resend. No futuro, o mesmo form passa a chamar a API (fase futura 3).
- **Acesso:** Cloudflare tunnel (ver [ADR 0002](docs/adr/0002-deploy-raspberry.md)).
- **Formato das descrições:** guardadas em markdown desde o início. Texto simples já é markdown válido, por isso evoluir para markdown renderizado e depois para editor visual não obriga a migrar dados.

## Documentação

- [docs/plano.md](docs/plano.md): plano e backlog de tarefas
- [docs/timer.md](docs/timer.md): regras do timer, pomodoro e arredondamento
- [docs/adr/](docs/adr/): decisões técnicas
- [docs/registo-horas.md](docs/registo-horas.md): registo de horas

## Como correr

A definir no setup.
