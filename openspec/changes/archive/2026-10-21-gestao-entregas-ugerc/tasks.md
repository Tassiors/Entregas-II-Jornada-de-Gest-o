# Tasks

## 1. Banco de Dados Local, REDCap Read-Only e Efeito Cascata

- [x] 1.1 Criar modelo SQLAlchemy `FormularioResposta` em `src/models/formulario_resposta.py` para armazenar respostas locais (projeto, período, entregas, conclusões e comentários) e registrar no Base. Verificar criação das tabelas no banco SQLite.
- [x] 1.2 Alterar `src/services/redcap_service.py` para operar estritamente em modo de leitura (remover envios de import/escrita para a API do REDCap) e carregar dados locais mesclados. Verificar ausência de chamadas de importação.
- [x] 1.3 Implementar a lógica de efeito cascata na conclusão e cancelamento de entregas bimestrais em `src/services/redcap_service.py` (conclusão em $B_k$ propaga para $B_{k+1..5}$; cancelamento em $B_k$ propaga para bimestres posteriores). Verificar através de testes unitários.
- [x] 1.4 Criar endpoints de CRUD completo em `src/routers/entregas_jornada.py` (`GET /formularios`, `GET /formularios/{id}`, `POST /formulario`, `PUT /formularios/{id}`, `DELETE /formularios/{id}`) com registro de auditoria local. Verificar respostas dos endpoints.

## 2. Gestão de Usuários, Perfil Gerente de Projeto e RBAC

- [x] 2.1 Criar modelo `UsuarioSistema` em `src/models/usuario_sistema.py` para persistir usuários cadastrados, perfis e o campo `projeto_atribuido`. Verificar criação da tabela no banco local.
- [x] 2.2 Criar endpoints administrativos para gestão e persistência de usuários com o perfil `GERENTE_PROJETO` e associação de projeto em `src/routers/admin.py`. Verificar rotas de CRUD de usuários.
- [x] 2.3 Implementar validação de controle de acesso (RBAC) garantindo que o Gerente de Projeto só execute operações de escrita/atualização/exclusão no projeto atribuído a ele, mantendo administradores com acesso irrestrito. Verificar bloqueio com HTTP 403 para projetos não autorizados.
- [x] 2.4 Atualizar `frontend/src/views/Configuracoes.vue` para incluir o perfil "Gerente de Projeto" no modal de cadastro de usuário com seleção de projeto, persistência real via API e isolamento da rota apenas para `ADMINISTRADOR`. Verificar interface de configurações.

## 3. Refatoração da Interface do Formulário e Notificações Toast

- [x] 3.1 Remover da tela `frontend/src/views/entregas/FormularioEntregas.vue` o seletor "Status do Formulário" e o botão "Voltar ao Painel". Verificar limpeza visual dos elementos.
- [x] 3.2 Implementar operações de leitura, edição e exclusão de formulários respondidos na interface, com feedback visual via `useToast` do framework (`vue-toastification`). Verificar disparo de toasts em ações de sucesso e erro.
- [x] 3.3 Bloquear a seleção de projeto para o projeto atribuído quando o usuário logado for `GERENTE_PROJETO`. Verificar bloqueio de seleção no formulário.

## 4. Redesenho do Painel Executivo e Ajustes Institucionais UGERC

- [x] 4.1 Limpar o menu lateral em `frontend/src/layouts/DefaultLayout.vue`, removendo as opções "Início", "Componentes" e "Exemplo", e exibindo "Configurações" apenas para administradores. Verificar itens restantes na barra lateral.
- [x] 4.2 Remover o botão "Preencher Acompanhamento" do cabeçalho da II Jornada em `frontend/src/views/entregas/PainelEntregas.vue`. Verificar cabeçalho limpo.
- [x] 4.3 Redesenhar todo o layout do `PainelEntregas.vue`, reorganizando os cards de métricas, progresso bimestral e visão comparativa por projeto com estética moderna. Verificar visualização responsiva e elegante.
- [x] 4.4 Substituir todas as ocorrências de "Setor de Tecnologia da Informação e Saúde Digital — SETISD" por "Unidade de Gestão da Estratégia, de Riscos e Controles Internos - UGERC" nos layouts, cabeçalhos, rodapés e em `src/version.py`. Verificar textos institucionais atualizados.

## 5. Validação, Testes Automatizados e Auditoria de Conformidade

- [x] 5.1 Atualizar suíte de testes em `tests/test_entregas_jornada.py` para testar persistência local, efeito cascata, CRUD e validação de permissão de gestor. Verificar com `pytest`.
- [x] 5.2 Compilar o frontend com `npm run build` na pasta `frontend` e verificar ausência de erros.
- [x] 5.3 Executar o auditor de conformidade arquitetural (`python audit_framework.py .`) e garantir 100% de conformidade nos 11 pilares mandatórios.
