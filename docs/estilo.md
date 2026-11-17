# Estilo: Seixo frio

Guia visual do Ticktask. Antes de estilizar um componente novo, consultar este guia. A direção foi escolhida a partir da [página de comparação de estilos](https://claude.ai/artifact/NL2eCqZ2e3tLa8w3xcQ3Fo) (separador "Seixo frio").

## Direção

Minimalista e calmo. Forma suave (cantos redondos, botões em pílula, cartões que flutuam com uma sombra leve) e cores sóbrias e frias. A cor aparece pouco, e por isso tem força quando aparece.

## Cores

| Papel | Família | Notas |
| --- | --- | --- |
| Neutro | `slate` | o único cinzento da app, nos dois modos |
| Destaque | `accent` (= `teal`) | definido no `@theme inline` do [index.css](../frontend/src/index.css) |
| Erro e perigo | `red` | só para erros e ações destrutivas |

Regras:

1. **Um só cinzento.** Nada de `gray`, `zinc`, `stone` ou `neutral`: só `slate`.
2. **Nos componentes escreve-se `accent-*`, nunca `teal-*`.** Para mudar a cor de destaque, muda-se só o `index.css`.
3. **O destaque é raro.** Aparece apenas no logótipo, no botão principal, no foco dos inputs e no timer ativo. Em mais lado nenhum.
4. **O vermelho não se mistura com o destaque.** Fica reservado para mensagens de erro e para o hover de ações como Archive.

## Texto

| Uso | Claro | Escuro |
| --- | --- | --- |
| Títulos | `text-slate-900` | `dark:text-slate-50` |
| Texto normal | `text-slate-700` | `dark:text-slate-300` |
| Texto secundário (descrições, datas, contagens) | `text-slate-500` | `dark:text-slate-400` |
| Placeholder | `placeholder:text-slate-400` | `dark:placeholder:text-slate-500` |

- Nunca usar `text-black` nem `text-white` para o texto normal: o 900 e o 50 são mais suaves.
- A hierarquia faz-se com o tamanho (`text-xs`, `text-sm`, `text-base`, `text-lg`), o peso (`font-medium`, `font-semibold`) e o tom, e não com cor.
- Números que mudam ou que se alinham em coluna (timer, totais de horas): `font-mono tabular-nums`.

## Superfícies

| Camada | Claro | Escuro |
| --- | --- | --- |
| Fundo da página | `bg-slate-100` | `dark:bg-slate-950` |
| Cabeçalho, cartões e formulários | `bg-white` | `dark:bg-slate-900` |
| Colunas do kanban | `bg-slate-200/60` | `dark:bg-slate-900` |
| Cartões dentro das colunas | `bg-white` | `dark:bg-slate-800` |
| Linhas e bordas | `border-slate-200` | `dark:border-slate-800` |

Cada camada fica um tom acima da que está por baixo. No escuro, "mais acima" quer dizer mais claro.

## Forma

- **Raio:** `rounded-xl` em cartões, formulários, inputs e colunas; `rounded-full` em botões e no logótipo.
- **Cartões:** sem borda. Usar `shadow-xs ring-1 ring-slate-900/10` (no escuro, `dark:ring-white/10`). No hover, `hover:shadow-md`.
- **Sombras:** só `shadow-xs` em repouso, e `shadow-md` no hover ou no cartão que se está a arrastar.

## Espaço

- Sempre com `flex` ou `grid` e `gap-*`, nunca com margens soltas entre elementos.
- Passos usados: `gap-1` e `gap-2` (dentro de um componente), `gap-4` (entre cartões e campos) e `gap-6` (entre secções).
- Padding interior: `p-5` em cartões e formulários, `p-3` nos cartões de tarefa e `p-2` nas colunas.
- Largura do conteúdo: `mx-auto max-w-7xl px-4`, igual no `header` e no `main`.

## Modo escuro

- As classes `dark:` escrevem-se já, junto com as do modo claro, em cada componente.
- Por agora, o `dark:` segue a preferência do sistema operativo (o comportamento por defeito do Tailwind v4). Um botão para alternar à mão fica para depois e não faz parte do MVP.
- O modo escuro não é o claro invertido: os fundos usam os tons 900/950 e o destaque fica mais claro (500 em vez de 700) para manter o contraste.
- Para testar sem mudar o tema do Windows: DevTools → Rendering → "Emulate CSS media feature prefers-color-scheme".

## Componentes

### Regra: elemento repetido → componente em `components/ui/`

- Os elementos de interface genéricos (botões, campos) vivem em [frontend/src/components/ui/](../frontend/src/components/ui/), e as classes ficam **só lá**. Nos outros componentes usa-se o componente e nunca se copiam as classes.
- Um conjunto de classes que se vai repetir passa a componente logo à 2.ª utilização, se já se souber que vai haver mais. Usa-se um componente React, nunca `@apply`.
- Uma cor ou um tamanho novo é uma **variante nova** no mapa do componente. Não se passa `className` de fora para alterar cores: duas classes de fundo no mesmo elemento entram em conflito.
- Elementos que só existem num sítio (o cartão de projeto, o formulário) não precisam de componente: as classes ficam no próprio ficheiro.

### Botões: `<Button>`

Ficheiro: [ui/Button.jsx](../frontend/src/components/ui/Button.jsx). O `type` é `"button"` por defeito; o botão que submete um formulário passa `type="submit"`.

| Variante | Uso | Exemplo |
| --- | --- | --- |
| `primary` (por defeito) | uma ação principal por ecrã | `<Button type="submit">Create</Button>` |
| `secondary` | ação alternativa | `<Button variant="secondary" onClick={onCancel}>Cancel</Button>` |
| `ghost` | ações discretas nos cartões | `<Button variant="ghost">Edit</Button>` |
| `danger` | ações destrutivas | `<Button variant="danger">Archive</Button>` |

### Formulários: `<Input>` e `<Textarea>`

Ficheiro: [ui/Input.jsx](../frontend/src/components/ui/Input.jsx). Os dois partilham as mesmas classes; o `Textarea` tem `rows={3}` por defeito.

Ainda sem componente (classes a usar diretamente):

| Elemento | Classes |
| --- | --- |
| Grupo label + input | `flex flex-col gap-1.5` |
| Label | `text-sm font-medium text-slate-700 dark:text-slate-300` |
| Erro | `text-sm text-red-600 dark:text-red-400` |
| Checkbox | `size-4 accent-accent-700 dark:accent-accent-500` |

A checkbox usa `accent-accent-700`: o primeiro `accent-` é a utilidade (a propriedade CSS `accent-color`) e o segundo é o nome da cor do tema.

### Timer ativo

- Cartão da tarefa: `ring-2 ring-accent-400` (no escuro, `dark:bg-accent-950/60 dark:ring-accent-500`)
- Contador: `font-mono text-xs font-medium tabular-nums text-accent-700 dark:text-accent-300`

As classes dos restantes elementos (cabeçalho, cartões de projeto, colunas do kanban) estão na receita da página de comparação, no separador "Seixo frio". Nessa página aparecem como `teal-*`, que aqui se escreve `accent-*`.
