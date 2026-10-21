# Tasks

## 1. Backend e Validação de Esquema do Formulário

- [x] 1.1 Verificar e ajustar os endpoints de formulário (`/form-schema`, `/registro-existente`, `/formulario`) em `src/routers/entregas_jornada.py` e `src/services/redcap_service.py` para compatibilidade total com os campos do REDCap XML. Verificar através da execução dos testes unitários com `pytest`.
- [x] 1.2 Implementar testes automatizados em `tests/test_entregas_jornada.py` cobrindo consulta de esquema, detecção de registro existente e validação de submissão com e sem preenchimento obrigatório. Verificar se a suíte de testes passa com `pytest tests/test_entregas_jornada.py`.

## 2. Construção da Interface do Formulário Vue 3

- [x] 2.1 Criar a visualização `frontend/src/views/entregas/FormularioEntregas.vue` replicando o formulário oficial do REDCap, contendo instruções institucionais, seletores de projeto (P1 a P5) e período (B1 a B6), exibição condicional (*branching logic*) dos cards oficiais de E1 e E2, botões de status de conclusão ("Sim" / "Não") e áreas de texto obrigatórias. Verificar a compilação do componente e layout responsivo.
- [x] 2.2 Implementar a busca reativa e preenchimento automático (*auto-fetch*) de registros existentes ao alterar projeto e período, exibindo alerta contextual caso já exista registro salvo. Verificar através de simulação de seleção de período com e sem registro prévio.
- [x] 2.3 Implementar modal de agradecimento oficial com o texto institucional do REDCap ao concluir a submissão com sucesso, fornecendo botões de ação para novo preenchimento ou retorno ao painel. Verificar abertura do modal pós-salvamento.

## 3. Roteamento, Navegação e Integração com o Painel

- [x] 3.1 Registrar a rota `/formulario` no roteador `frontend/src/router/index.ts` e adicionar item de navegação correspondente na barra lateral em `frontend/src/layouts/DefaultLayout.vue`. Verificar navegação direta pela barra lateral.
- [x] 3.2 Integrar botões de ação rápida ("Preencher Entrega" / "Novo Registro") no cabeçalho e nos cards de projeto em `frontend/src/views/entregas/PainelEntregas.vue`, passando query parameters (`?projeto={id}&periodo={id}`) para pré-seleção. Verificar propagação dos parâmetros para o formulário.

## 4. Compilação, Validação e Conformidade Arquitetural

- [x] 4.1 Executar a compilação do frontend (`npm run build` na pasta `frontend`) e verificar se os tipos TypeScript e componentes Vue são construídos sem erros.
- [x] 4.2 Executar o auditor de conformidade arquitetural do HC-UFPE (`python audit_framework.py .`) e garantir 100% de conformidade nos 11 pilares mandatórios.
