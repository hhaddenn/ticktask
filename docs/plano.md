# Plano de implementação: taskManager

## Marcos

| Marco | Entregável | Data |
| --- | --- | --- |
| M0 | Requisitos, ADRs e modelos de dados fechados | |
| M1 | Backend e frontend a correr em dev, ligados um ao outro | |
| M2 | Projetos e tarefas em kanban com drag and drop | |
| M3 | Timer e registo de tempo, com totais | |
| M4 | Deploy na Raspberry | |
| M5 | Backlog e avisos de data limite por email (Should) | |

## Tarefas

Estima antes de começar cada tarefa e não alteres o estimado depois.

| # | Tarefa | Requisito | Estimativa | Real | Estado |
| --- | --- | --- | --- | --- | --- |
| 1 | Fechar o README (MVP/Won't) e o CLAUDE.md | | | | em curso |
| 2 | Escrever os ADRs 0001–0003 | | | | por fazer |
| 3 | Desenhar os modelos de dados (Projeto, Etapa, Tarefa, RegistoTempo…) para revisão | | | | por fazer |
| 4 | Setup do backend: Django, DRF, Postgres, `.env.example`, linter | | | | por fazer |
| 5 | Setup do frontend: React, linter e formatter | | | | por fazer |
| 6 | `.gitignore` (venv, `node_modules`, `.env`, `__pycache__`, builds) | | | | por fazer |

## Riscos

| Risco | Probabilidade | Plano |
| --- | --- | --- |
| Âmbito a crescer (é um projeto pessoal sem prazo) | Alta | Tudo o que for novo entra como Could no README antes de ser feito |
| Drag and drop mais difícil do que parece (ordem persistida no servidor) | Média | Fazer primeiro um protótipo isolado só com o drag and drop |
| Recursos limitados da Raspberry | Baixa | Evitar serviços extra (ver ADR 0003) |

## Notas

- Pergunta em aberto sobre a origem dos emails: ver README.
