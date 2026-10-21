# Design

## Context

O sistema conta atualmente com o painel analítico (`PainelEntregas.vue`) e endpoints no backend (`src/routers/entregas_jornada.py` e `src/services/redcap_service.py`) integrados com o REDCap. No entanto, a interface web ainda não dispõe de uma tela para preenchimento direto e edição das entregas bimestrais dos projetos da II Jornada de Gestão, obrigando os gestores a preencherem no ambiente externo do REDCap. O formulário de referência (`EntregasJornadaDeGes_2026-10-21_0953.REDCap.xml`) define campos específicos, textos institucionais, regras de ramificação condicional (*branching logic*) por projeto e opções de status que devem ser replicados fielmente na experiência web corporativa.

## Goals / Non-Goals

**Goals:**
- Implementar a view Vue 3 `FormularioEntregas.vue` compatível com o design system corporativo do HC-UFPE / EBSERH e Tailwind CSS.
- Mapear e renderizar dinamicamente os 5 projetos estratégicos (P1 a P5) e 6 bimestres (B1 a B6), com títulos e descrições exatas de E1 e E2 extraídas do esquema REDCap.
- Replicar fielmente o *branching logic* nativo: ao selecionar o projeto, exibir exclusivamente as entregas E1 e E2 daquele projeto, com campos de conclusão ("Sim" = `0` / "Não" = `1`) e áreas de texto de evolução obrigatórias.
- Consultar registros prévios via endpoint `/registro-existente` para permitir tanto inclusão de novos registros quanto edição rápida de registros já salvos.
- Exibir modal de agradecimento oficial com o texto de reconhecimento institucional do REDCap ao salvar.
- Disponibilizar atalho no menu lateral (`DefaultLayout.vue`) e botão de ação rápida no painel executivo (`PainelEntregas.vue`), aceitando parâmetros de consulta (`?projeto=X&periodo=Y`).
- Manter a trilha de auditoria corporativa (`audit_logs`) ativa para cada gravação realizada.

**Non-Goals:**
- Não criar tabelas adicionais no PostgreSQL hospitalar (os registros de acompanhamento pertencem ao REDCap e o histórico de mutações é auditado no SQLite local).
- Não permitir a exclusão destrutiva de projetos ou períodos estruturais da II Jornada.

## Decisions

### 1. Consumo Dinâmico do Esquema e Metadados via API
- **Decisão**: A tela `FormularioEntregas.vue` consumirá o endpoint `GET /api/v1/entregas-jornada/form-schema` para obter os textos institucionais (instruções, agradecimento), opções de período e nomes/cores dos projetos.
- **Alternativa considerada**: Fixar todos os textos e opções estaticamente no código do componente Vue.
- **Justificativa**: A obtenção centralizada via API garante sincronia com as definições do REDCap e do arquivo `src/config.py`, facilitando manutenção e prevenindo inconsistências.

### 2. Detecção Automática de Registro Existente (*Auto-fetch*)
- **Decisão**: Ao alterar a combinação de `projeto` e `periodo`, disparar automaticamente uma busca por registros existentes via `GET /api/v1/entregas-jornada/registro-existente`.
- **Alternativa considerada**: Exigir que o usuário pesquise manualmente ou informe um `record_id`.
- **Justificativa**: Cada projeto possui apenas uma entrega pactuada por bimestre. A detecção automática oferece excelente usabilidade (UX), evitando duplicidade acidental no REDCap e permitindo revisão contínua.

### 3. Branching Logic no Frontend com Componentes Reativos
- **Decisão**: Utilizar bindings reativos no Vue (`computed` e `v-if/v-show`) para alternar as entregas do projeto ativo e preencher os metadados calculados `var_projeto` e `var_periodo`.
- **Alternativa considerada**: Renderizar 5 formulários separados com abas.
- **Justificativa**: O comportamento de formulário único com branching logic espelha com precisão a semântica de *surveys* do REDCap, simplificando a validação de formulário único e o fluxo de submissão.

### 4. Integração Bidirecional com o Painel Executivo
- **Decisão**: No `PainelEntregas.vue`, adicionar botões "Preencher Entrega" que navegam para `/formulario-entregas?projeto={id}&periodo={id}`. Ao concluir o preenchimento, o formulário oferece botão direto para retornar ao painel, que já apresentará dados atualizados pois o backend invalida o cache do REDCap na submissão.
- **Alternativa considerada**: Abrir o formulário em um iframe do REDCap.
- **Justificativa**: O formulário nativo em Vue 3 respeita a identidade visual do HC-UFPE, é totalmente responsivo para dispositivos móveis e registra auditoria local conforme as normas da EBSERH.

## Risks / Trade-offs

- **[Risco] Indisponibilidade momentânea ou timeout na API do REDCap**
  → *Mitigação*: Exibição de tratamento de erro amigável com mensagem descritiva (toast de erro e alertas na interface), permitindo nova tentativa sem perda dos dados digitados.
- **[Risco] Tentativa de submissão simultânea ou duplo clique**
  → *Mitigação*: Desabilitação do botão de envio com spinner de carregamento (*isSubmitting*) até a conclusão do processamento.
- **[Risco] Edição acidental de bimestre já concluído**
  → *Mitigação*: Alerta visual explícito ("Registro Existente Localizado") quando os dados carregados forem de uma entrega já registrada, informando ao gestor que as alterações sobrescreverão o registro anterior.
