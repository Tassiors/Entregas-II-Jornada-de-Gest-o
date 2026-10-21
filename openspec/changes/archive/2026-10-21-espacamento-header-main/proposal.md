# Proposal: Separação Visual entre Header e Main no Painel e Formulário

## Why

Atualmente, o elemento `<main>` nas telas de acompanhamento da II Jornada utiliza uma margem negativa superior (`-mt-6` ou `-mt-4`), fazendo com que o conteúdo do corpo avance e sobreponha a faixa do `<header>` corporativo. Para conferir maior clareza visual, respiro e elegância na hierarquia dos blocos, é necessário separar o `<header>` do `<main>` aplicando espaçamento positivo (`mt-8` / `mt-6`) entre ambos.

## What Changes

- **Separação no Painel da II Jornada (`PainelEntregas.vue`)**: Substituição da margem negativa `-mt-6` no `<main>` por margem positiva `mt-8` (ou espaçamento equivalente), garantindo que o banner azul do header e a matriz de projetos fiquem visivelmente destacados e separados.
- **Harmonização no Formulário de Entregas (`FormularioEntregas.vue`)**: Ajuste de `-mt-4` para margem positiva `mt-6`, mantendo a consistência visual em todo o módulo da II Jornada.

## Capabilities

### Modified Capabilities

- `painel-entregas`: Ajuste de requisitos de layout visual e hierarquia de espaçamento vertical entre cabeçalho institucional e conteúdo principal.

## Impact

- **Frontend**: Componentes [`PainelEntregas.vue`](file:///c:/Users/tassio.silva/OneDrive%20-%20HU%20BRASIL/HC_DEV/Entregas%20II%20Jornada%20de%20Gestao/frontend/src/views/entregas/PainelEntregas.vue) e [`FormularioEntregas.vue`](file:///c:/Users/tassio.silva/OneDrive%20-%20HU%20BRASIL/HC_DEV/Entregas%20II%20Jornada%20de%20Gestao/frontend/src/views/entregas/FormularioEntregas.vue).
- **Sem impacto em APIs, banco de dados ou regras de negócio.**
