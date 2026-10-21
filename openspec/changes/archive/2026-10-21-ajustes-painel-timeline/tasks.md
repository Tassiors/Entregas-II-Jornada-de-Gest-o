# Tasks

## 1. Ajustes Visuais no Painel da II Jornada (`PainelEntregas.vue`)

- [x] 1.1 Remover o bloco dos 4 cards executivos de topo (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5`) da tela `PainelEntregas.vue`.
- [x] 1.2 Remover o texto e link `'Ver detalhes ->'` dos cards da matriz dos 5 projetos em `PainelEntregas.vue`.
- [x] 1.3 Remover a barra horizontal de abas redundantes dos projetos em `PainelEntregas.vue`.
- [x] 1.4 Remover o dropdown de filtro de bimestre do cabeçalho de `PainelEntregas.vue`.
- [x] 1.5 Corrigir a timeline para exibir fidedignamente todos os bimestres reportados com textos de E1 e E2, status de conclusão e responsável.

## 2. Correção da Persistência de Formulários e Atualização da Timeline

- [x] 2.1 Refatorar `FormularioEntregas.vue` para despachar submissões via `POST /api/v1/entregas-jornada/formulario`, garantindo criação/atualização no banco SQLite local.
- [x] 2.2 Ao submeter com sucesso, navegar para o Painel pré-selecionando o projeto recém-atualizado via query param `?projeto={id}`.
- [x] 2.3 Ajustar `src/routers/entregas_jornada.py` em `PUT /formularios/{id}` com fallback para salvar por `(projeto, periodo)` caso o ID não exista na base local.

## 3. Blindagem de Acesso do Gerente de Projeto (RBAC)

- [x] 3.1 Garantir que o formulário de entregas trave o seletor de projeto para `GERENTE_PROJETO` e que o backend rejeite com HTTP 403 qualquer submissão para outro projeto.
- [x] 3.2 Garantir que o perfil `GERENTE_PROJETO` não veja o menu de configurações e não consiga acessar nem a rota `/configuracoes` nem os endpoints `/api/admin/*`.

## 4. Testes, Build e Auditoria

- [x] 4.1 Executar a suíte de testes unitários com `pytest tests/ -v`.
- [x] 4.2 Compilar o frontend com `npm run build` na pasta `frontend`.
- [x] 4.3 Rodar o auditor `audit_framework.py` e garantir 100% de conformidade.
- [x] 4.4 Validar e arquivar a mudança no OpenSpec e reiniciar o servidor para validação do usuário.

