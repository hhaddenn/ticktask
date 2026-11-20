# CLAUDE.md: Ticktask

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
- **Estilos:** Tailwind CSS, inspirado no Odoo (kanban, cartões, drag and drop). Componentes shadcn/ui só quando fizerem falta (ex: Dialog, Dropdown), depois de dominar o Tailwind
- **Base de dados / backend:** PostgreSQL e Django
- **Alojamento / deploy:** Raspberry Pi própria (ver [docs/adr/0002-deploy-raspberry.md](docs/adr/0002-deploy-raspberry.md))

## Comandos

Os comandos do backend correm na pasta `backend/`, com o ambiente virtual ativo (`source .venv/bin/activate`). O Postgres de dev corre em Docker, a partir da raiz do projeto. Os comandos do frontend correm na pasta `frontend/`.

| Ação | Backend (`backend/`) | Frontend (`frontend/`) |
| --- | --- | --- |
| Instalar | `python -m venv .venv` + `pip install -r requirements.txt` + `cp .env.example .env` (gerar a `SECRET_KEY`) | `npm install` |
| Base de dados (dev) | `docker compose -f docker-compose.dev.yml up -d` (na raiz) + `python manage.py migrate` | n/a |
| Correr em dev | `python manage.py runserver` (`http://localhost:8000`, admin em `/admin/`) | `npm run dev` (`http://localhost:5173`) |
| Testes | `python manage.py test` | a definir (Vitest, quando houver componentes) |
| Linter / formatter | `ruff check .` + `ruff format .` | `npm run lint` + `npm run format` (verificar sem alterar: `npm run format:check`) |
| Build | n/a | `npm run build` (gera `dist/`) |

Notas:

- O Postgres de dev está exposto na porta **5433** do PC (a 5432 está ocupada por um Postgres do sistema).
- O contexto Docker de dev é o `desktop-linux` (Docker Desktop). Confirmar com `docker context ls` antes de comandos Docker: existe também um contexto `raspberry`.

## Estrutura

- `backend/`: projeto Django (API)
  - `config/`: settings, URLs, WSGI/ASGI (só configuração)
  - `accounts/`: `User` próprio e preferências, e a autenticação por sessão em `/api/auth/` (`me/`, `login/`, `logout/`)
  - `projects/`: `Project`, `Stage` e `Task`, com a API em `/api/` (`projects/`, `stages/`, `tasks/`), incluindo arquivar projetos e mover tarefas no kanban
- `docker-compose.dev.yml`: Postgres para desenvolvimento
- `frontend/`: aplicação React (Vite, JavaScript, ESLint, Prettier com tabs)
- `docs/`: plano, ADRs, registo de horas

## Regras específicas deste projeto

- Um só utilizador (eu). Nada de multi-utilizador na v1.
- O tempo do timer é calculado no servidor (`started_at` / `ended_at`), nunca contado no browser.

## Ao começar uma tarefa do plano

Quando eu pedir para avançar com uma tarefa do [plano](docs/plano.md), o Claude dá-me uma checklist em markdown (`- [ ]`) para eu seguir enquanto programo, com esta estrutura:

1. **Antes de começar:** registar a minha estimativa na coluna Estimativa do [plano](docs/plano.md) (os tempos ficam só no plano, não no registo de horas), dizer que docs ler (modelos, timer, ADRs) e avisar se algo sai do marco ou do MVP.
2. **Passos:** pequenos (15 a 30 min cada) e por ordem. Cada passo diz o que fazer, o comando a correr e como verificar que funcionou. Os conceitos novos são explicados numa linha e o Claude não dá o código feito.
3. **Decisões:** as escolhas que tenho de tomar nesta tarefa, com a recomendação do Claude.
4. **Verificar:** testes ou experiências manuais e o linter e o formatter (`ruff` / `npm run lint` + `npm run format`).
5. **Fechar:** pedir revisão ao Claude, lançar o tempo real na coluna Real do plano, atualizar os docs se o desenho mudou e sugerir a mensagem de commit (o commit faço eu).

### Ao avançar para cada passo

Quando eu passar a um passo da checklist (ou pedir ajuda num), o Claude dá-me também uma **checklist curta só desse passo** (`- [ ]`), uma ação por linha e por ordem:

- Cada linha diz o que fazer e onde (ficheiro, método, comando). Pode nomear a API do Django/React a usar (ex: `project.stages.first()`), mas não dá o método completo.
- Termina com a verificação: `ruff` / `npm run lint`, a experiência no shell ou no browser e o que devo ver.
- A última linha é colar o código ao Claude para revisão.
- Explicações mais longas só se eu pedir ou se estiver preso.

## O que estou a aprender neste projeto

- Timers e registo de tempo
- Notificações por email quando uma data limite se aproxima (tarefas agendadas)
- React
- Django
- Styling com Tailwind CSS (e mais tarde shadcn/ui)

Foca as explicações e as revisões nestes temas.
