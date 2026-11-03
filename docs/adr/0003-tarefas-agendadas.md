# ADR 0003: Tarefas agendadas (emails de aviso de data limite)

**Data:** 2026-11-03 · **Estado:** proposta

## Contexto

Quero receber um email quando a data limite de uma tarefa se aproxima. Isso precisa de algo que corra periodicamente, fora dos pedidos HTTP. Um só utilizador, poucas tarefas, a correr numa Raspberry.

## Decisão

<Uma frase. Ex: um management command do Django corrido por cron de X em X tempo.>

## Alternativas consideradas

- **Celery + Redis (ou RabbitMQ):** <a opção "óbvia"; porque não para este caso?>
- **django-q / APScheduler:** <...>
- **<outra>:** <...>

## Consequências

- **Positivas:** <...>
- **Negativas / trade-offs:** <ex: precisão limitada ao intervalo do cron; como evito enviar o mesmo aviso duas vezes?>
- **O que faria reverter esta decisão:** <...>
