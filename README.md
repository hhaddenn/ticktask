# taskManager

Aplicação pessoal para gerir projetos, tarefas e backlog, e registar o tempo gasto em cada tarefa.

## Problema

Não tenho um sítio único para os meus projetos e tarefas, para os bugs e sugestões que me chegam por email e para o tempo que gasto em cada coisa. Sem isso não sei quanto demoro de facto nem o que tenho pendente.

## MVP (Must)

- **Projetos:** criar, editar, arquivar.
- **Tarefas em kanban:** tarefas dentro de um projeto, organizadas em colunas (etapas), com drag and drop entre colunas e dentro da mesma coluna.
- **Timer:** botão start/stop numa tarefa, que cria um registo de tempo. Só um timer ativo de cada vez.
- **Registo de tempo manual:** adicionar ou corrigir registos à mão.
- **Totais:** horas por tarefa e por projeto.

## Should

- **Backlog:** tarefas do tipo bug / sugestão, criadas à mão, que depois passam para um projeto.
- **Datas limite:** data limite numa tarefa e email de aviso quando se aproxima.

## Could

- Criar entradas do backlog automaticamente a partir dos emails recebidos (ver pergunta em aberto).
- Reordenar e personalizar colunas, etiquetas, filtros e pesquisa.
- Relatórios de tempo por semana/mês.

## Won't (v1)

- Multi-utilizador, equipas e permissões.
- Faturação.
- App mobile nativa.
- Anexos em tarefas.

## Perguntas em aberto

- **De onde vêm os emails de bugs e sugestões?** Se vierem de um formulário noutro site, esse formulário pode fazer um POST diretamente à API do taskManager, em vez de eu ler a caixa de email (IMAP). A resposta muda a arquitetura.
- **Acesso:** só na rede local, por VPN, ou exposto à internet com HTTPS? (ver ADR 0002)

## Documentação

- [docs/plano.md](docs/plano.md): plano e backlog de tarefas
- [docs/adr/](docs/adr/): decisões técnicas
- [docs/registo-horas.md](docs/registo-horas.md): registo de horas

## Como correr

A definir no setup.
