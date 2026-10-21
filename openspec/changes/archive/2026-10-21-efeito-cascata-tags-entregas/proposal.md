# Proposal: Efeito Cascata de Entregas, Campos Opcionais e Tags nos Cards

## Why

Identificou-se que a submissão de formulários em bimestres subsequentes não estava herdando automaticamente o status de conclusão das entregas concluídas em bimestres anteriores, exigindo que o usuário remarcasse manualmente ou causando reversão acidental para "não concluída". Além disso, os campos de comentários continuavam obrigatórios mesmo após a conclusão da entrega, e os cards das entregas no painel executivo necessitavam de uma tag/badge explícita destacando o status de conclusão para maior clareza visual.

## What Changes

- **Efeito Cascata no Formulário de Entregas (`FormularioEntregas.vue`)**:
  - Ao carregar um projeto e bimestre para preenchimento, se alguma entrega (E1 ou E2) já foi concluída em bimestre anterior, o formulário já inicializa a entrega marcada como concluída ("Sim" / "0") e exibe uma badge informativa (ex: "✅ Concluída no B1").
  - O campo "COMENTÁRIOS / EVOLUÇÃO DA ENTREGA" torna-se **opcional** para entregas que estão concluídas (ou já foram concluídas em bimestres anteriores), dispensando preenchimento forçado.
- **Efeito Cascata no Backend (`redcap_service.py` e `entregas_jornada.py`)**:
  - O endpoint `GET /registro-existente` passa a inspecionar o histórico prévio do projeto e retornar se E1/E2 já foram concluídas anteriormente, com seus respectivos períodos de origem.
  - O esquema de validação `FormularioEntregaSchema` flexibiliza os campos de texto para aceitar comentários vazios/opcionais quando a entrega estiver concluída.
  - A persistência `save_local_form_record` e a consolidação `get_all_merged_records` garantem que bimestres subsequentes herdem confiavelmente a conclusão da entrega, exceto mediante cancelamento explícito.
- **Tags de Conclusão nos Cards das Entregas (`PainelEntregas.vue`)**:
  - Nos cards das entregas pactuadas (E1 e E2) do projeto ativo, inclusão de tags visíveis de status (`✅ Concluída` / `⏳ Em andamento`).
  - Nos cards dos projetos da Matriz Geral, inclusão de tag/badge indicativa da contagem de metas atingidas (ex: `✅ 2/2 Concluídas`, `⚡ 1/2 Concluída`).

## Capabilities

### Modified Capabilities

- `formulario-entregas`: Herança automática de status de conclusão de bimestres anteriores, flexibilização de comentários como opcionais após conclusão e alerta visual de conclusão prévia.
- `painel-entregas`: Exibição de tags/badges de status nos cards de descrição oficial das entregas e nos cards da matriz de projetos.

## Impact

- **Backend**: Atualização de [`src/routers/entregas_jornada.py`](file:///c:/Users/tassio.silva/OneDrive%20-%20HU%20BRASIL/HC_DEV/Entregas%20II%20Jornada%20de%20Gestao/src/routers/entregas_jornada.py) e [`src/services/redcap_service.py`](file:///c:/Users/tassio.silva/OneDrive%20-%20HU%20BRASIL/HC_DEV/Entregas%20II%20Jornada%20de%20Gestao/src/services/redcap_service.py).
- **Frontend**: Atualização de [`FormularioEntregas.vue`](file:///c:/Users/tassio.silva/OneDrive%20-%20HU%20BRASIL/HC_DEV/Entregas%20II%20Jornada%20de%20Gestao/frontend/src/views/entregas/FormularioEntregas.vue), [`PainelEntregas.vue`](file:///c:/Users/tassio.silva/OneDrive%20-%20HU%20BRASIL/HC_DEV/Entregas%20II%20Jornada%20de%20Gestao/frontend/src/views/entregas/PainelEntregas.vue) e [`entregasService.ts`](file:///c:/Users/tassio.silva/OneDrive%20-%20HU%20BRASIL/HC_DEV/Entregas%20II%20Jornada%20de%20Gestao/frontend/src/services/entregasService.ts).
