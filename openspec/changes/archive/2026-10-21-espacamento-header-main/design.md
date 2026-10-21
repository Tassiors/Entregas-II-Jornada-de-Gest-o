# Design: Ajuste de Espaçamento e Separação entre Header e Main

## Context

No design original dos templates Tailwind do frontend, utilizava-se a convenção de "overlap card", onde a tag `<main>` possuía a classe utilitária `-mt-6` (no painel) ou `-mt-4` (no formulário). Essa técnica faz com que o primeiro bloco do corpo avance verticalmente para cima da faixa inferior do `<header>` corporativo com gradiente azul.
O usuário solicitou explicitamente que os blocos sejam separados, criando um respiro limpo e bem delineado entre eles.

## Goals / Non-Goals

**Goals:**
- Separar visualmente o container `<header>` do `<main>` no componente [`PainelEntregas.vue`](file:///c:/Users/tassio.silva/OneDrive%20-%20HU%20BRASIL/HC_DEV/Entregas%20II%20Jornada%20de%20Gestao/frontend/src/views/entregas/PainelEntregas.vue).
- Harmonizar o mesmo padrão de espaçamento vertical no [`FormularioEntregas.vue`](file:///c:/Users/tassio.silva/OneDrive%20-%20HU%20BRASIL/HC_DEV/Entregas%20II%20Jornada%20de%20Gestao/frontend/src/views/entregas/FormularioEntregas.vue).
- Garantir visual responsivo em resoluções mobile (`sm`), tablet e desktop (`lg`).

**Non-Goals:**
- Não alterar as cores ou os textos internos do `<header>`.
- Não modificar os cards da matriz de entregas nem seus comportamentos reativos.

## Decisions

- **Decisão 1: Substituição de `-mt-6` por `mt-8` no Painel**:
  - *Alternativa considerada*: Usar `padding-top` no main (`pt-8`).
  - *Razão da escolha*: A margem positiva `mt-8` (32px) no `<main>` cria um espaçamento exterior nítido em relação ao `shadow-lg` do header, evitando qualquer sobreposição e garantindo respiro em qualquer densidade de tela.
- **Decisão 2: Substituição de `-mt-4` por `mt-8` no Formulário**:
  - *Razão da escolha*: Manter a paridade visual e consistência arquitetural entre todas as telas do módulo da II Jornada.

## Risks / Trade-offs

- **[Risco]** Em telas móveis muito pequenas, espaçamentos excessivos podem exigir mais rolagem.
  - *Mitigação*: Utilizar `mt-6 sm:mt-8`, que confere 24px em telas pequenas e 32px em telas maiores.
