# Timer: regras (v1)

Regras de funcionamento do timer e do registo de tempo. Servem de base ao desenho dos modelos de dados (tarefa 3 do [plano](plano.md)).

## Conceitos

- **Registo de tempo:** um período contínuo a trabalhar numa tarefa, com início e fim.
- **Sessão:** o conjunto de registos entre o primeiro start e o stop (normalmente, um dia de trabalho).
- **Pause:** "fui almoçar". Fecha o registo atual; a sessão continua.
- **Stop:** "acabei o dia". Fecha a sessão e lança as horas arredondadas.

## Timer normal

```text
parado ──start──▶ a correr ──pause──▶ em pausa ──resume──▶ a correr
                     │                    │
                     └──────stop──────────┴──▶ parado
```

1. Cada registo de tempo pertence a uma tarefa.
2. Só há **um timer ativo** em toda a app. Ao iniciar o timer na tarefa B com a tarefa A a correr, aparece um aviso com duas opções:
   - "Parar A e começar B"
   - "Continuar em A" (o timer de B não arranca)
3. **Pause** fecha o registo atual. **Resume** abre um registo novo. A pausa não conta como tempo e pode durar até ao dia seguinte.
4. **Stop** fecha a sessão: soma os registos, arredonda o total e lança as horas no dia.
5. O tempo é sempre calculado no servidor a partir de `started_at` / `ended_at`. O browser só mostra a contagem.

## Arredondamento

6. As horas são registadas ao minuto, arredondadas a um bloco escolhido pelo utilizador (ex: 15 min).
7. O arredondamento aplica-se ao **total da sessão**, no stop, e nunca a cada registo.
8. Os tempos exatos são sempre guardados. O valor arredondado fica guardado à parte.
9. O arredondamento é **sempre para cima**: 10 min de trabalho contam como 15 min, e não como 0. Nenhum trabalho feito fica por registar.

```text
manhã:  a correr 3h02 → pause (almoço)
tarde:  a correr 4h05 → stop (acabei o dia)
sessão = 7h07 → arredondado = 7h15 → lançado no registo de horas do dia
```

## Sessões esquecidas

10. Se ao abrir a app houver uma sessão aberta desde um dia anterior, a app avisa e pergunta se a quer fechar.

## Pomodoro

```text
parado ──start──▶ foco ──(fim do tempo)──▶ à espera ──clique──▶ pausa
                                                                  │
foco ◀──clique── à espera ◀──(fim do tempo)───────────────────────┘
```

11. O utilizador escolhe usar o timer normal ou o pomodoro.
12. Configurável pelo utilizador:
    - duração do foco;
    - duração da pausa;
    - se há pausa longa, quanto dura e ao fim de quantos pomodoros.
13. Só o foco conta como tempo da tarefa. As pausas não contam.
14. Nada começa sozinho: no fim de cada foco ou pausa, o utilizador recebe uma notificação e clica para continuar.
15. O fim de um foco é `started_at + duração`, mesmo que o browser esteja fechado.
16. As notificações (som + Notification API) só funcionam com a app aberta. A app sugere mantê-la aberta ao usar o pomodoro.

## Registos manuais

17. É possível adicionar ou corrigir registos à mão. Um registo manual tem só uma duração, sem início nem fim.

## Fora do timer

18. Terminar uma tarefa é mudá-la de coluna no kanban. Não tem nada a ver com o timer nem com o arredondamento.

## Para mais tarde (Could)

- Notificações com a app fechada (Web Push).
