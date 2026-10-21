# Tasks

## 1. Backend: Efeito Cascata, Verificação Prévia e Campos Opcionais

- [x] 1.1 Atualizar `find_existing_record` em [`src/services/redcap_service.py`](file:///c:/Users/tassio.silva/OneDrive%20-%20HU%20BRASIL/HC_DEV/Entregas%20II%20Jornada%20de%20Gestao/src/services/redcap_service.py) para calcular `cascade_info` com base nos bimestres anteriores do projeto.
- [x] 1.2 Atualizar o schema `FormularioEntregaSchema` em [`src/routers/entregas_jornada.py`](file:///c:/Users/tassio.silva/OneDrive%20-%20HU%20BRASIL/HC_DEV/Entregas%20II%20Jornada%20de%20Gestao/src/routers/entregas_jornada.py) para tornar `ent1_txt` e `ent2_txt` opcionais quando a entrega for concluída.
- [x] 1.3 Assegurar que `save_local_form_record` e `get_all_merged_records` propaguem fidedignamente o status de conclusão para bimestres subsequentes.

## 2. Frontend: Formulário de Entregas (`FormularioEntregas.vue`)

- [x] 2.1 Atualizar `checkExistingRecord` para consumir `cascade_info`, inicializar as entregas previamente concluídas como "Sim" ("0") e exibir badge informativa de conclusão prévia.
- [x] 2.2 Tornar os campos de comentários e evolução opcionais no template e na validação do `handleSubmit` quando a respectiva entrega estiver concluída.

## 3. Frontend: Tags nos Cards das Entregas (`PainelEntregas.vue`)

- [x] 3.1 Adicionar tags de status (`✅ Concluída` / `⏳ Em andamento`) nos cards das entregas pactuadas (E1 e E2) do projeto ativo.
- [x] 3.2 Adicionar tag/badge indicativa de conclusão nos cards dos projetos na Matriz Geral.

## 4. Testes, Build e Validação

- [x] 4.1 Executar a suíte de testes unitários com `pytest tests/ -v`.
- [x] 4.2 Compilar o frontend com `npm --prefix frontend run build`.
- [x] 4.3 Rodar o auditor `audit_framework.py .` garantindo 100% de conformidade.
- [x] 4.4 Validar e arquivar a mudança no OpenSpec e reiniciar o servidor para validação do usuário.
