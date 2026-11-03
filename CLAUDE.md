# CLAUDE.md: taskManager

@~/Desktop/Projects/devHelper/CLAUDE.md

As regras acima são a base e mantêm-se sempre: git só para consulta, nada de edições sem autorização, eu programo e o Claude ensina.
Os guias referidos nelas estão em ~/Desktop/Projects/devHelper/docs/.

## O projeto

- **O que é:** gestão de projetos, tarefas e backlog (bugs e sugestões recebidos por email), com registo de horas e timer por tarefa. Vista kanban com drag and drop, inspirada no Odoo.
- **Tipo:** pessoal
- **Cliente:** nenhum, é para mim
- **Estado:** requisitos

## Âmbito (pessoal)

- **MVP (Must) e Won't:** ver [README.md](README.md)
- **Plano e backlog:** ver [docs/plano.md](docs/plano.md)
- **Prazo:** não há

Avisa-me se um pedido parecer fora do MVP.

## Stack

- **Linguagem / framework:** React (frontend) e Django + Django REST Framework (API)
- **Estilos:** inspirado no Odoo (kanban, cartões, drag and drop)
- **Base de dados / backend:** PostgreSQL e Django
- **Alojamento / deploy:** Raspberry Pi própria (ver [docs/adr/0002-deploy-raspberry.md](docs/adr/0002-deploy-raspberry.md))

## Comandos

A definir no setup (tarefas 4 e 5 do plano). Vai haver comandos separados para `backend/` e `frontend/`.

| Ação          | Backend (`backend/`) | Frontend (`frontend/`) |
| ------------- | -------------------- | ---------------------- |
| Instalar      | a definir            | a definir              |
| Correr em dev | a definir            | a definir              |
| Testes        | a definir            | a definir              |
| Linter        | a definir            | a definir              |
| Build         | n/a                  | a definir              |

## Estrutura

- `backend/`: projeto Django (API)
- `frontend/`: aplicação React
- `docs/`: plano, ADRs, registo de horas

## Regras específicas deste projeto

- Um só utilizador (eu). Nada de multi-utilizador na v1.
- O tempo do timer é calculado no servidor (`started_at` / `ended_at`), nunca contado no browser.

## O que estou a aprender neste projeto

- Timers e registo de tempo
- Notificações por email quando uma data limite se aproxima (tarefas agendadas)
- React
- Django

Foca as explicações e as revisões nestes temas.
