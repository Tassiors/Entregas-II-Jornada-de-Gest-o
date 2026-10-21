# Design

## Context

A governança do acompanhamento das entregas da II Jornada de Gestão do HC-UFPE foi atribuída à Unidade de Gestão da Estratégia, de Riscos e Controles Internos (UGERC). Para garantir maior autonomia institucional, segurança e conformidade, o sistema deixa de gravar dados diretamente na API do REDCap (que passa a atuar estritamente como fonte de leitura ou semente inicial) e passa a persistir e gerenciar todas as respostas em banco de dados relacional local (`data/app.db`). Adicionalmente, estabelece-se o controle de acesso com perfil específico de Gerente de Projeto restrito ao seu próprio projeto, efeito cascata nas entregas bimestrais e redesenho visual do painel executivo.

## Goals / Non-Goals

**Goals:**
- **Persistência Local e REDCap Read-Only**: Criar o modelo SQLAlchemy `FormularioResposta` para gravar respostas localmente, desativando qualquer chamada de importação/escrita na API do REDCap.
- **Regra de Negócio com Efeito Cascata**: Se uma entrega for marcada como concluída em um bimestre $B_k$, replicar essa conclusão nos bimestres seguintes ($B_{k+1..5}$). Da mesma forma, se a conclusão for cancelada em $B_k$, propagar o cancelamento nos bimestres subsequentes.
- **CRUD Completo de Formulários**: Disponibilizar endpoints e interface para consultar, criar, atualizar e excluir/reinicializar respostas de entregas.
- **Controle de Acesso RBAC Específico**: Criar o perfil `GERENTE_PROJETO` no cadastro de usuários, permitindo associar um dos 5 projetos. No backend, validar que o gerente só consiga criar/editar/excluir dados do seu projeto, enquanto administradores têm acesso pleno e o painel analítico permanece público para consulta.
- **Restrição de Acesso às Configurações**: Restringir o menu e a rota `/configuracoes` estritamente a usuários com o papel `ADMINISTRADOR`.
- **Limpeza da Navegação Lateral**: Remover as opções "Início", "Componentes" e "Exemplo" do menu da barra lateral (`DefaultLayout.vue`).
- **Aprimoramentos de Usabilidade no Formulário**: Remover o campo de seleção "Status do Formulário" e o botão "Voltar ao Painel" de `FormularioEntregas.vue`, substituindo `alert()` nativo por Toasts do framework (`vue-toastification`).
- **Redesenho do Painel Executivo**: Modernizar os cards e indicadores de `PainelEntregas.vue`, removendo o botão "Preencher Acompanhamento" do cabeçalho da II Jornada.
- **Identidade Institucional UGERC**: Atualizar todas as menções a "Setor de Tecnologia da Informação e Saúde Digital — SETISD" por "Unidade de Gestão da Estratégia, de Riscos e Controles Internos - UGERC".

**Non-Goals:**
- Não enviar requisições de escrita/modificação para o servidor remoto do REDCap.
- Não restringir a visualização de leitura do Painel Executivo (mantém-se aberto e acessível).

## Decisions

### 1. Modelo de Dados Local `FormularioResposta` e `UsuarioSistema`
- **Decisão**: Utilizar o banco SQLite da aplicação (`data/app.db`) gerenciado pelo SQLAlchemy para criar as tabelas `formulario_respostas` e `usuarios_sistema`.
- **Justificativa**: Garante persistência permanente local das respostas e dos usuários cadastrados pelo administrador, sem dependência de escrita externa no REDCap e compatível com a arquitetura monolítica do HC-UFPE.

### 2. Algoritmo de Efeito Cascata no Backend
- **Decisão**: Ao gravar ou atualizar um formulário para o período $B_k$, a função de serviço verifica o status das entregas E1 e E2. Se `ent1_conc == "0"` (Sim), atualiza os registros já existentes de períodos $p > k$ e garante que novos registros para períodos posteriores herdem a conclusão. Se `ent1_conc == "1"` (Não), atualiza os períodos $p > k$ para não concluído caso estivessem como concluídos.
- **Justificativa**: Centralizar a lógica no backend garante integridade quer a mutação venha da interface web, quer de chamadas via API REST.

### 3. Autorização e Isolamento de Gestor (RBAC)
- **Decisão**: Implementar dependência FastAPI `verify_project_manager_access(projeto)` que compara o `projeto` alvo da requisição com o `projeto_atribuido` do usuário logado no token JWT/banco.
- **Justificativa**: Impede violações de privilégio no nível da API, enquanto o frontend ajusta a UI para selecionar e travar automaticamente o projeto do gestor.

### 4. Notificações com `vue-toastification`
- **Decisão**: Adotar a biblioteca `vue-toastification` já instalada no projeto para disparar alertas flutuantes elegantes (`toast.success`, `toast.error`, `toast.warning`).
- **Justificativa**: Atende ao requisito 9 eliminando caixas de diálogo modais bloqueantes do navegador (`alert()`).

## Risks / Trade-offs

- **[Risco] Discrepância inicial entre dados do REDCap e banco local**
  → *Mitigação*: Ao inicializar, caso a tabela local não possua registros para um projeto/período, o sistema realiza uma leitura prévia dos dados existentes no REDCap como semente, mas quaisquer respostas preenchidas a partir de então são salvas e lidas exclusivamente da base local.
- **[Risco] Cancelamento acidental com efeito cascata**
  → *Mitigação*: Exibição de aviso informativo via Toast alertando que a alteração do status de conclusão refletirá nos períodos seguintes da jornada.
