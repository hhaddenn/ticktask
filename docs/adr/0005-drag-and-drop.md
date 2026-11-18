# ADR 0005: Drag and drop com `@hello-pangea/dnd`

**Data:** 2026-11-18 · **Estado:** aceite

## Contexto

O kanban tem de permitir arrastar tarefas dentro da mesma coluna e entre colunas (README, Must). A nova posição é guardada no servidor pela ação `move` da API de tarefas, que recebe `{ stage, position }`, sendo `position` o índice na coluna de destino sem contar com a própria tarefa (ver [modelos.md](../modelos.md), "Ordem no drag and drop").

Requisitos para a biblioteca:

- Ordenar dentro de uma lista e mover entre várias listas, incluindo para uma coluna vazia.
- Funcionar com rato, toque e teclado.
- Não trazer estilos próprios, porque o aspeto vem do Tailwind (ver [estilo.md](../estilo.md)).
- Ser compatível com React 19.
- Ter boa documentação e exemplos, porque um dos objetivos do projeto é aprender React.

Estado das opções em novembro de 2026 (npm):

| Pacote                                | Versão         | Última publicação | Estado                     |
| ------------------------------------- | -------------- | ----------------- | -------------------------- |
| `@hello-pangea/dnd`                   | 18.0.1         | fevereiro de 2025 | estável, sem novas versões |
| `@dnd-kit/core` / `@dnd-kit/sortable` | 6.3.1 / 10.0.0 | dezembro de 2024  | estável, sem novas versões |
| `@dnd-kit/react`                      | 0.5.3          | outubro de 2026   | ativa, ainda em 0.x        |
| `@atlaskit/pragmatic-drag-and-drop`   | 4.0.0          | setembro de 2026  | ativa                      |
| `react-beautiful-dnd`                 | 13.1.1         | —                 | descontinuada              |
| `react-dnd`, `react-sortablejs`       | —              | junho de 2022     | abandonadas                |

## Decisão

Usar a `@hello-pangea/dnd` (18.x), a continuação mantida pela comunidade da `react-beautiful-dnd` da Atlassian.

É uma biblioteca feita só para listas e kanbans, que é exatamente o caso do Ticktask. O `onDragEnd` devolve `source` e `destination` como `{ droppableId, index }`, que mapeia diretamente para o `{ stage, position }` da ação `move`.

A biblioteca é experimentada primeiro num protótipo isolado (tarefa 13), sem API, e só depois ligada ao kanban (tarefa 14).

## Alternativas consideradas

- **dnd-kit clássica (`@dnd-kit/core` + `@dnd-kit/sortable`):** a mais usada e mais flexível (grelhas, arrastar livre, sensores e deteção de colisões configuráveis). Rejeitada porque, para um kanban, obriga a mais código: mover entre colunas em tempo real (`onDragOver`), tornar as colunas vazias em alvos (`useDroppable`) e calcular a `position` à mão. Essa flexibilidade não é precisa no Ticktask. Também não tem novas versões desde dezembro de 2024.
- **`@dnd-kit/react`:** a nova API do dnd-kit, ativamente mantida. Rejeitada por agora porque ainda está em 0.x (a API pode mudar entre versões) e tem poucos exemplos e tutoriais.
- **Pragmatic drag and drop (Atlassian):** mantida e muito leve. Rejeitada porque é mais baixo nível: não traz ordenação pronta nem suporte de teclado, que teriam de ser feitos à mão.
- **API nativa do HTML5 (`draggable`, `onDragStart`, `onDrop`):** sem dependências. Rejeitada porque não funciona com toque, tem fraco suporte de teclado e as animações durante o arrasto são difíceis de fazer.
- **`react-beautiful-dnd`, `react-dnd`, `react-sortablejs`:** descontinuadas ou sem versões desde 2022.

## Consequências

- **Positivas:**
  - Pouco código para o kanban: `DragDropContext`, um `Droppable` por coluna e um `Draggable` por cartão. Mover entre colunas e largar numa coluna vazia funcionam sem código extra.
  - O `destination` do `onDragEnd` dá diretamente o pedido à API: `{ stage: destination.droppableId, position: destination.index }`.
  - Teclado, toque e anúncios para leitores de ecrã de série, com animações durante o arrasto.
  - Os elementos interativos dentro do cartão (como o botão "Edit") não iniciam o arrasto, por isso continuam a funcionar.
  - Sem estilos próprios: o aspeto do cartão a arrastar define-se com Tailwind (`shadow-md`, ver estilo.md), a partir do `snapshot.isDragging`.
- **Negativas / trade-offs:**
  - Só serve para listas (verticais ou horizontais). Se um dia for preciso arrastar numa grelha ou livremente, é preciso outra biblioteca.
  - Usa render props (`{(provided, snapshot) => ...}`), um padrão de React mais antigo do que os hooks.
  - O `droppableId` e o `draggableId` têm de ser strings, por isso os `id` numéricos da API são convertidos nos dois sentidos.
  - Sem novas versões desde fevereiro de 2025. Funciona com React 19, mas pode deixar de acompanhar versões futuras.
- **O que faria reverter esta decisão:** a biblioteca deixar de funcionar com uma versão nova do React, ou o kanban precisar de algo que não seja uma lista. Nesse caso, migrar para a `@dnd-kit/react` (se já estiver na 1.0) ou para a dnd-kit clássica. A atualização do estado e o pedido `move` mantêm-se, e só muda a forma de obter o `{ stage, position }`.

## Notas

A preencher no fim da tarefa 13: o que se aprendeu no protótipo e o que levar para a tarefa 14.
