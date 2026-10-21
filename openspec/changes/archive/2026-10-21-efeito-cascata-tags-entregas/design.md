# Design: Efeito Cascata de Entregas, Campos Opcionais e Tags nos Cards

## Context

A II Jornada de Gestão avalia o cumprimento de entregas estratégicas (E1 e E2) ao longo de 6 bimestres (Julho/2026 a Junho/2027). A regra de negócio estabelece que, uma vez pactuada a entrega e marcada como concluída ("Sim" / "0"), sua conclusão perdura nos bimestres seguintes, a menos que haja cancelamento explícito. No entanto:
1. O formulário ao ser aberto para um bimestre subsequente iniciava sem herdar a conclusão anterior.
2. O formulário e o backend exigiam comentários obrigatórios mesmo para entregas já concluídas.
3. Faltavam tags e badges visíveis identificando o status nos cards de entregas.

## Goals / Non-Goals

**Goals:**
- Herança ativa no formulário: ao selecionar um projeto e período, verificar o histórico anterior e assinalar como concluída qualquer entrega finalizada em bimestres passados.
- Tornar o campo de comentários/evolução opcional tanto no frontend quanto no backend quando a entrega estiver com status de conclusão "Sim" ("0") ou quando já concluída anteriormente.
- Exibir tags visuais nos cards das entregas (E1 e E2) no painel executivo e badges de contagem na matriz de projetos.
- Assegurar que a propagação cascata reflita tanto nos registros salvos quanto na visualização analítica (matriz e timeline).

**Non-Goals:**
- Não alterar a estrutura de banco de dados (as colunas existentes no SQLite `formulario_respostas` já atendem).
- Não gravar dados no REDCap (apenas leitura de sementes).

## Decisions

- **Decisão 1: Informações de Cascata no endpoint `/registro-existente`**:
  - O endpoint retornará um objeto `cascade_info`: `{ e1_concluida: bool, e1_origem: str, e2_concluida: bool, e2_origem: str }`.
  - Se não houver registro para o período atual, os campos `form.ent1_conc` e `form.ent2_conc` serão inicializados com `"0"` se `cascade_info` indicar conclusão prévia.
- **Decisão 2: Comentários Opcionais após Conclusão**:
  - Em `FormularioEntregaSchema` (backend): `ent1_txt` e `ent2_txt` passam a ter default `""`. Se `ent_conc == "0"`, não há obrigatoriedade de caracteres.
  - No frontend: remover o atributo `required` do `<textarea>` e o asterisco vermelho `<span class="text-red-500">*</span>` quando a entrega estiver concluída. No `handleSubmit`, ignorar validação de texto para entregas concluídas.
- **Decisão 3: Tags nos Cards das Entregas**:
  - No `PainelEntregas.vue`, nos cards de descrição de E1 e E2, incluir `<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black ...">✅ Concluída</span>` se a entrega estiver concluída (`e1_done`/`e2_done`), ou `⏳ Em andamento` se pendente.
  - Na Matriz dos 5 Projetos, adicionar tag de progresso (`✅ 2/2 Concluídas`, `⚡ 1/2 Concluída` ou `⏳ Em andamento`).

## Risks / Trade-offs

- **[Risco] Cancelamento acidental**: O usuário pode clicar em "Não" e desfazer a conclusão.
  - *Mitigação*: Exibir badge informativa indicando que a entrega foi herdada de bimestre anterior, e nota explicativa de que alterar para "Não" propaga o cancelamento para os bimestres subsequentes.
