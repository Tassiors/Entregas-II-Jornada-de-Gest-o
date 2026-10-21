# Proposal

## Why

Atualmente, o acompanhamento das entregas e metas dos 5 projetos estratégicos da II Jornada de Gestão do HC-UFPE depende do preenchimento direto no REDCap ou de coletas externas descentralizadas. Para proporcionar autonomia aos gerentes de projeto e unificar a experiência dentro do sistema institucional, é necessário replicar o formulário oficial do REDCap (`EntregasJornadaDeGes_2026-10-21_0953.REDCap.xml`) diretamente na interface web corporativa Vue 3, com validações em tempo real, lógica condicional de exibição (branching logic), carregamento dinâmico de registros prévios, gravação via API do REDCap e registro de auditoria imutável conforme as diretrizes institucionais do HC-UFPE / EBSERH.

## What Changes

- **Interface Vue 3 para o Formulário de Acompanhamento**: Nova rota e tela `/formulario-entregas` replicando fielmente todos os campos, regras de visibilidade e textos institucionais do REDCap.
- **Lógica Condicional (Branching Logic) e Campos Derivados**: Exibição dinâmica das entregas específicas do projeto selecionado (P1 a P5) com descrições oficiais, campos de conclusão ("Sim"/"Não") e justificativas/comentários de evolução, além do cálculo automático das variáveis derivadas `var_projeto` e `var_periodo`.
- **Carregamento Automático de Registros Anteriores**: Ao selecionar um projeto e período bimestral, a aplicação consulta a API para carregar automaticamente dados previamente salvos, permitindo atualização transparente.
- **Feedback e Modal de Agradecimento**: Ao submeter o formulário com sucesso, exibir o agradecimento oficial do REDCap e invalidar o cache analítico do painel.
- **Acesso Integrado na Navegação e no Painel**: Inclusão de item de navegação no menu lateral (`DefaultLayout.vue`) e botão de ação rápida "Novo Registro / Atualizar Entrega" no `PainelEntregas.vue`.
- **Rastreabilidade e Trilha de Auditoria**: Registro de auditoria local categorizado como `NEGOCIO_CLINICO` via `registrar_auditoria()` com captura de IP e usuário para todas as submissões.

## Capabilities

### New Capabilities
- `formulario-entregas`: Interface web de coleta e atualização de entregas da II Jornada de Gestão, com replicação fiel dos campos, regras condicionais, validação e submissão ao REDCap com auditoria.

### Modified Capabilities
- `painel-entregas`: O painel executivo passa a incorporar ponto de entrada direto para o formulário de entrega e atualização imediata de dados após submissão de novos registros.

## Impact

- **Frontend**: Criação de `frontend/src/views/entregas/FormularioEntregas.vue`, atualização de rotas em `frontend/src/router/index.ts`, menu em `frontend/src/layouts/DefaultLayout.vue` e integração de atalhos em `frontend/src/views/entregas/PainelEntregas.vue`.
- **Backend / APIs**: Utilização e validação dos endpoints `/api/v1/entregas-jornada/form-schema`, `/api/v1/entregas-jornada/registro-existente` e `/api/v1/entregas-jornada/formulario` em `src/routers/entregas_jornada.py`.
- **Auditoria & Segurança**: Garantia de registro de logs imutáveis e conformidade com o framework HC-UFPE (11 pilares mandatórios).
