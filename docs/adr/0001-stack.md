# ADR 0001: Stack — Django + DRF, React e PostgreSQL

**Data:** 2026-11-03 · **Estado:** aceite

## Contexto

Aplicação pessoal com kanban e drag and drop, timer e registo de tempo. Na v1 há um só utilizador; nas fases futuras a app terá utilizadores e SSO com a app de finanças (ver README). Um dos objetivos é aprender React e Django.

## Decisão

Backend em Django com Django REST Framework a expor uma API JSON, frontend em React (SPA) a consumi-la, PostgreSQL como base de dados.

## Alternativas consideradas

- **FastAPI:** mais leve e com bom suporte async, mas obriga a juntar à mão o ORM (SQLAlchemy/SQLModel), as migrações (Alembic), a autenticação e um admin. Para um CRUD com poucos utilizadores, o Django já traz tudo isso, e as tarefas agendadas encaixam num management command (ADR 0003).
- **Django com templates + HTMX:** mais simples (um só projeto, sem API nem CORS). Rejeitado porque um dos objetivos é aprender React, e porque o kanban com drag and drop e o timer a atualizar em tempo real são interações ricas onde o React se sente em casa.

## Consequências

- **Positivas:**
  - O Django traz de raiz ORM, migrações e admin: o admin dá uma interface para gerir dados antes de o frontend estar pronto.
  - Autenticação incluída, útil para as fases futuras com utilizadores.
  - O React encaixa nas interações ricas da app (kanban com drag and drop, timer em tempo real, pomodoro) e cumpre o objetivo de aprender React.
- **Negativas / trade-offs:**
  - Dois projetos para manter (`backend/` e `frontend/`), cada um com dependências, linter e build.
  - CORS em dev e autenticação entre o React e a API.
  - Mais uma peça no deploy: servir o build do React (ADR 0002).
- **O que faria reverter esta decisão:** se o frontend acabar por ser maioritariamente formulários simples, Django com templates + HTMX passaria a ser mais simples de manter.
