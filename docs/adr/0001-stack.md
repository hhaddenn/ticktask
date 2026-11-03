# ADR 0001: Stack — Django + DRF, React e PostgreSQL

**Data:** 2026-11-03 · **Estado:** proposta

## Contexto

Aplicação pessoal com kanban e drag and drop, timer e registo de tempo. Um só utilizador. Um dos objetivos é aprender React e Django.

## Decisão

<Uma frase. Ex: backend em Django com Django REST Framework a expor uma API JSON, frontend em React (SPA) a consumi-la, PostgreSQL como base de dados.>

## Alternativas consideradas

- **Django com templates + HTMX:** <mais simples, um só projeto; porque não?>
- **SQLite em vez de PostgreSQL:** <chegaria para um utilizador; porque não?>
- **<outra>:** <...>

## Consequências

- **Positivas:** <...>
- **Negativas / trade-offs:** <ex: dois projetos para manter, CORS/autenticação entre front e back>
- **O que faria reverter esta decisão:** <...>
