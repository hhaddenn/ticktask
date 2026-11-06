# ADR 0003: Tarefas agendadas (emails de aviso de data limite)

**Data:** 2026-11-03 · **Estado:** aceite

## Contexto

Quero receber um email quando a data limite de uma tarefa se aproxima. Isso precisa de algo que corra periodicamente, fora dos pedidos HTTP. Um só utilizador, poucas tarefas, a correr numa Raspberry com Docker e Komodo (ADR 0002).

## Decisão

Um management command do Django, corrido periodicamente por um cron num serviço `scheduler` próprio no Docker Compose, que usa a mesma imagem do backend.

## Alternativas consideradas

- **Celery + Redis (ou RabbitMQ):** obriga a correr mais dois serviços (worker e broker) na Raspberry, a gastar RAM permanentemente, para um trabalho de poucos segundos de X em X tempo. É pensado para filas com muito volume, que este caso não tem.
- **Cron no host (a Raspberry) a chamar o container:** funciona, mas fica configuração fora da stack, o que obriga a entrar na Raspberry e contraria o ADR 0002.

## Consequências

- **Positivas:**
  - Simples: o código é um management command normal, testável à mão (`python manage.py <comando>`).
  - Sem serviços extra além do `scheduler`, que só acorda para correr o comando.
  - Tudo dentro da stack do Komodo.
- **Negativas / trade-offs:**
  - Precisão limitada ao intervalo do cron (ex: de hora a hora).
  - Avisos duplicados: o comando corre muitas vezes para a mesma tarefa. Para evitar isso, guarda-se na tarefa quando o aviso foi enviado, e esse valor é limpo se a data limite mudar.
- **O que faria reverter esta decisão:** precisar de trabalho em segundo plano com volume ou urgência (ex: muitos utilizadores, emails a enviar logo após uma ação), aí uma fila como Celery passa a fazer sentido.
