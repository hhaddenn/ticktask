# CLAUDE.md: taskManager

@~/Desktop/Projects/devHelper/CLAUDE.md

As regras acima são a base e mantêm-se sempre: git só para consulta, nada de edições sem autorização, eu programo e o Claude ensina.
Os guias referidos nelas estão em ~/Desktop/Projects/devHelper/docs/.

## O projeto

- **O que é:** gestão de projetos, tarefas e backlog (bugs e sugestões recebidos por email), com registo de horas e timer por tarefa. Vista kanban com drag and drop, inspirada no Odoo.
- **Tipo:** pessoal
- **Cliente:** nenhum, é para mim
- **Estado:** desenvolvimento (M1: setup)

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

Os comandos do backend correm na pasta `backend/`, com o ambiente virtual ativo (`source .venv/bin/activate`). O Postgres de dev corre em Docker, a partir da raiz do projeto.

| Ação | Backend (`backend/`) | Frontend (`frontend/`) |
| --- | --- | --- |
| Instalar | `python -m venv .venv` + `pip install -r requirements.txt` + `cp .env.example .env` (gerar a `SECRET_KEY`) | a definir (tarefa 6) |
| Base de dados (dev) | `docker compose -f docker-compose.dev.yml up -d` (na raiz) + `python manage.py migrate` | n/a |
| Correr em dev | `python manage.py runserver` (`http://localhost:8000`, admin em `/admin/`) | a definir (tarefa 6) |
| Testes | `python manage.py test` | a definir (tarefa 6) |
| Linter / formatter | `ruff check .` + `ruff format .` | a definir (tarefa 6) |
| Build | n/a | a definir (tarefa 6) |

Notas:

- O Postgres de dev está exposto na porta **5433** do PC (a 5432 está ocupada por um Postgres do sistema).
- O contexto Docker de dev é o `desktop-linux` (Docker Desktop). Confirmar com `docker context ls` antes de comandos Docker: existe também um contexto `raspberry`.

## Estrutura

- `backend/`: projeto Django (API)
  - `config/`: settings, URLs, WSGI/ASGI (só configuração)
  - `accounts/`: `User` próprio e preferências
- `docker-compose.dev.yml`: Postgres para desenvolvimento
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
