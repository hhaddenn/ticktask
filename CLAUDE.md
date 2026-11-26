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
  - `timesheets/`: `TimeEntry` (sessão / lançamento de horas) e `TimerInterval` (período a correr), com as constraints do timer na base de dados (um timer aberto por utilizador, um intervalo a correr por sessão). API do timer em `/api/timer/` (`GET` devolve a sessão aberta, com `is_forgotten` se for de um dia anterior em Lisboa, ou 204 se não houver; `start/`, `pause/`, `resume/`, `stop/`), com a lógica em `services.py`, incluindo o arredondamento do total no stop. O `stop/` aceita um `ended_at` opcional, para as sessões esquecidas: dá 400 se a hora for inválida (no futuro, ou antes do intervalo a correr) e 409 se a sessão estiver em pausa. Registos de horas em `/api/time-entries/` (`TimeEntryViewSet` + `TimeEntryRecordSerializer`): listar (`?task=`), criar registos manuais, corrigir (`PATCH`) e apagar. A sessão aberta não aparece aqui (404)
- `docker-compose.dev.yml`: Postgres para desenvolvimento
- `frontend/`: aplicação React (Vite, JavaScript, ESLint, Prettier com tabs)
  - `src/components/AppLayout.jsx`: cabeçalho e rotas, só depois do login. Chama o `useTimer` e mostra o aviso de sessão esquecida
  - `src/hooks/useTimer.js`: estado do timer (sessão aberta e âncora `syncedAt`) e as ações start, pause, resume e stop (com hora de fim opcional), mais `stopAndRestart`, `dismissForgotten` e o derivado `isForgotten`. Chamado uma só vez, no `AppLayout`, e passado por props
  - `src/components/ForgottenSessionDialog.jsx`: aviso de sessão esquecida, com a hora de fim (só com a sessão a correr) e as três opções da regra 10 da [timer.md](docs/timer.md)
  - `src/components/TimerDisplay.jsx`: contador ao vivo, derivado do `elapsed_seconds` do servidor mais o tempo local desde a resposta
  - `src/components/TimeEntryList.jsx`: registos de horas da tarefa, no dialog de editar tarefa. Vai buscar os seus dados e trata de editar (uma linha de cada vez, `editingId`) e apagar
  - `src/components/TimeEntryForm.jsx`: adicionar um registo manual (sem `entry`) ou corrigir um registo (com `entry`; a data fica bloqueada nas sessões do timer)
  - `src/timer.js`: `formatDuration` (segundos → `H:MM:SS`) e `formatMinutes` (minutos → `H:MM`), os dois como exports com nome
- `docs/`: plano, ADRs, registo de horas

## Regras específicas deste projeto

- Um só utilizador (eu). Nada de multi-utilizador na v1.
- O tempo do timer é calculado no servidor (`started_at` / `ended_at`), nunca contado no browser.

## Ao começar uma tarefa do plano

Segue o fluxo de "Tarefas com vários passos" do devHelper (overview primeiro, depois passo a passo). Neste projeto acrescenta:

- **Antes de começar:** registar a minha estimativa na coluna Estimativa do [plano](docs/plano.md) (os tempos ficam só no plano, não no registo de horas) e avisar se a tarefa sai do marco ou do MVP. Os docs a ler são os modelos, o timer e os ADRs em `docs/`.
- **Verificar:** usar os comandos da tabela de Comandos (`ruff` / `npm run lint` + `npm run format`).
- **Fechar:** lançar o tempo real na coluna Real do plano.

## O que estou a aprender neste projeto

- Timers e registo de tempo
- Notificações por email quando uma data limite se aproxima (tarefas agendadas)
- React
- Django
- Styling com Tailwind CSS (e mais tarde shadcn/ui)

Foca as explicações e as revisões nestes temas.
