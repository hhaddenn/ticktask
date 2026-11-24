# Plano de implementação: Ticktask

## Marcos

| Marco | Entregável                                                                             | Data |
| ----- | -------------------------------------------------------------------------------------- | ---- |
| M0    | Requisitos, ADRs e modelos de dados fechados                                           |      |
| M1    | Backend e frontend a correr em dev, ligados um ao outro                                |      |
| M2    | Projetos e tarefas em kanban com drag and drop                                         |      |
| M3    | Timer e registo de tempo, com totais                                                   |      |
| M4    | Deploy na Raspberry                                                                    |      |
| M5    | Funcionalidades Should: pomodoro, markdown, documentos, backlog, avisos de data limite |      |

M0 a M4 são o MVP. As tarefas de M3 em diante são mais grossas: parte-as em tarefas de 1–4 h quando chegares lá.

## Tarefas

As estimativas deste plano são **preliminares**, feitas pelo Claude para dar uma ordem de grandeza (incluem tempo de aprendizagem de React e Django). Antes de começar cada tarefa, faz **a tua** estimativa e escreve-a na coluna Estimativa, no lugar da preliminar: é essa que conta para o fator de correção, e não se altera depois. No fim, o tempo real vai na coluna Real. Os tempos ficam só neste plano, sem duplicar no [registo de horas](registo-horas.md). As tarefas 1 e 2 não foram estimadas antes de começar, por isso ficam sem estimativa.

| Marco           | Estimativa          |
| --------------- | ------------------- |
| M0              | 2 h (só a tarefa 3) |
| M1              | 7,5 h               |
| M2              | 32 h                |
| M3              | 24 h                |
| M4              | 13 h                |
| **MVP (M0–M4)** | **78,5 h**          |
| M5 (Should)     | 25 h                |
| **Total**       | **103,5 h**         |

| #   | Marco | Tarefa                                                                                                                    | Requisito | Estimativa | Real    | Estado                |
| --- | ----- | ------------------------------------------------------------------------------------------------------------------------- | --------- | ---------- | ------- | --------------------- |
| 1   | M0    | Fechar o README (MVP/Won't) e o CLAUDE.md                                                                                 |           | —          | 0h30min | feito                 |
| 2   | M0    | Escrever os ADRs 0001–0003                                                                                                |           | —          | 0h30min | feito                 |
| 3   | M0    | Desenhar os modelos de dados (Projeto, Etapa, Tarefa, RegistoTempo…) para revisão                                         |           | 2 h        | 0h15min | feito                 |
| 4   | M1    | `.gitignore` (venv, `node_modules`, `.env`, `__pycache__`, builds)                                                        |           | 0,5 h      | 0h15min | feito                 |
| 5   | M1    | Setup do backend: Django, DRF, Postgres, `.env.example`, linter                                                           |           | 3 h        | 1h45min | feito                 |
| 6   | M1    | Setup do frontend: React, linter e formatter                                                                              |           | 2 h        | 1h10min | feito                 |
| 7   | M1    | Ligar o React à API: proxy do Vite (ADR 0004) e um endpoint de teste                                                      |           | 2 h        | 1h25min | feito                 |
| 8   | M2    | Modelos Projeto, Etapa e Tarefa, migrações e admin                                                                        | Must      | 3 h        | 1h40min | feito                 |
| 9   | M2    | API de projetos (CRUD, arquivar)                                                                                          | Must      | 3 h        | 2h50min | feito                 |
| 10  | M2    | API de tarefas, incluindo mudar de etapa e de ordem                                                                       | Must      | 4 h        | 3h35min | feito                 |
| 11  | M2    | React: lista de projetos e formulário                                                                                     | Must      | 3 h        | 2h40min | feito                 |
| 11b | M2    | Setup do Tailwind e migração dos componentes atuais (shadcn só mais tarde)                                                | Must      | 2 h        | 1h40min | feito                 |
| 12  | M2    | React: vista kanban (colunas e cartões, sem drag and drop)                                                                | Must      | 4 h        | 2h      | feito                 |
| 12b | M2    | React: criar e editar tarefa (reaproveitar `Input`, `Textarea` e `Button`)                                                | Must      | 3 h        | 2h      | feito                 |
| 13  | M2    | Protótipo isolado de drag and drop                                                                                        | Must      | 3 h        | 1h40min | feito                 |
| 14  | M2    | Drag and drop no kanban, com a ordem guardada na API                                                                      | Must      | 4 h        | 1h30min | feito                 |
| 15  | M2    | Descrição em texto simples no projeto e na tarefa                                                                         | Must      | 1 h        | 0h      | feito na fase 11 e 12 |
| 16  | M2    | API de autenticação: `me`, login e logout (sessão e CSRF), com testes                                                     | Must      | 2h         | 1h40min | feito                 |
| 16b | M2    | React: página de login e logout                                                                                           | Must      | 2 h        | 1h5min  | feito                 |
| 17  | M3    | Modelos de registo de tempo e sessão, com a regra "um timer ativo"                                                        | Must      | 3 h        | 1h45min | feito                 |
| 18  | M3    | API do timer: start, pause, resume, stop                                                                                  | Must      | 4 h        | 3h45min | feito                 |
| 19  | M3    | Arredondamento no stop, com testes                                                                                        | Must      | 2 h        | 1h05min | feito                 |
| 20  | M3    | React: timer na tarefa (contagem a partir do servidor)                                                                    | Must      | 4 h        | 2h      | feito                 |
| 21  | M3    | Aviso de timer ativo noutra tarefa                                                                                        | Must      | 2 h        |         | por fazer             |
| 22  | M3    | Aviso de sessão esquecida                                                                                                 | Must      | 2 h        |         | por fazer             |
| 23  | M3    | Registos de tempo manuais                                                                                                 | Must      | 2 h        |         | por fazer             |
| 24  | M3    | Totais de horas por tarefa e por projeto                                                                                  | Must      | 2 h        |         | por fazer             |
| 24b | M3    | Estimativa no formulário da tarefa e estimado vs. real                                                                    | Must      | 2 h        |         | por fazer             |
| 25  | M3    | Preferências: bloco de arredondamento                                                                                     | Must      | 1 h        |         | por fazer             |
| 26  | M4    | Dockerfiles do backend e do frontend (`arm64`)                                                                            |           | 4 h        |         | por fazer             |
| 27  | M4    | Docker Compose e stack no Komodo (servir o `index.html` nas rotas do React Router)                                        |           | 3 h        |         | por fazer             |
| 27b | M4    | Segurança de produção: throttling no login, settings seguros (cookies `Secure`, `CSRF_TRUSTED_ORIGINS`), `check --deploy` |           | 2 h        |         | por fazer             |
| 28  | M4    | Cloudflare tunnel                                                                                                         |           | 2 h        |         | por fazer             |
| 29  | M4    | Backup automático do Postgres                                                                                             |           | 2 h        |         | por fazer             |
| 30  | M5    | Pomodoro: preferências, estados e notificações                                                                            | Should    | 8 h        |         | por fazer             |
| 31  | M5    | Markdown estilo GitHub nas descrições                                                                                     | Should    | 2 h        |         | por fazer             |
| 32  | M5    | Separador Documentos                                                                                                      | Should    | 4 h        |         | por fazer             |
| 33  | M5    | Backlog: tarefas do tipo bug / sugestão                                                                                   | Should    | 3 h        |         | por fazer             |
| 34  | M5    | Data limite e serviço `scheduler` com email de aviso                                                                      | Should    | 6 h        |         | por fazer             |
| 35  | M5    | Estimativa em pomodoros e contador feitos / estimados                                                                     | Should    | 2 h        |         | por fazer             |

## Riscos

| Risco                                                                   | Probabilidade | Plano                                                                           |
| ----------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------- |
| Âmbito a crescer (é um projeto pessoal sem prazo)                       | Alta          | Tudo o que for novo entra no README (Could ou fases futuras) antes de ser feito |
| Drag and drop mais difícil do que parece (ordem persistida no servidor) | Média         | Protótipo isolado primeiro (tarefa 13)                                          |
| Recursos limitados da Raspberry                                         | Baixa         | Evitar serviços extra (ver ADR 0003)                                            |
| Perda de dados (backups na própria Raspberry)                           | Baixa         | Risco aceite no ADR 0002; rever quando houver dados importantes                 |
