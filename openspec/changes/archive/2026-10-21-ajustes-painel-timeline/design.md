# Design: Ajustes Visuais no Painel da II Jornada, Correção da Timeline e Blindagem RBAC

## Contexto e Motivação
A tela "II Jornada" apresentava redundâncias visuais:
1. 4 cards de topo consumindo espaço útil sem agregar à navegação direta.
2. Texto `'Ver detalhes ->'` em cada card de projeto quando o próprio card já é interativo.
3. Barra de abas duplicando exatamente os botões de seleção de projeto já presentes na matriz de cards.
4. Dropdown de filtro de bimestre no cabeçalho que causava filtragem estrita e ocultação dos registros de outros períodos na timeline.
5. Inconsistência na submissão de formulário quando carregado registro do REDCap (tentativa de `PUT /formularios/{id}` para ID inexistente no banco local), impedindo que os novos dados chegassem à tabela `formulario_respostas` e consequentemente à timeline.

## Decisões Técnicas

### 1. Simplificação do Painel (`PainelEntregas.vue`)
- **Remoção dos 4 cards de topo**: A tela inicia diretamente na matriz dos 5 projetos, com design limpo e focado.
- **Cards dos Projetos como Seletores Únicos**:
  - Cada card exibe código, nome, ícone, badges de E1 e E2.
  - Clicar no card seleciona o projeto ativo imediatamente (`store.setProject(p.proj_key)`).
  - Remoção do texto 'Ver detalhes ->'.
- **Remoção da Barra de Abas**: Eliminada a linha redundante de `<button>` horizontal de projetos.
- **Remoção do Dropdown de Bimestre do Cabeçalho**: O cabeçalho mantém o título institucional, a tag UGERC e o botão "Atualizar Dados".
- **Timeline Completa e Fidedigna**:
  - A timeline do projeto ativo exibe todos os bimestres que possuem dados (banco local e REDCap), ordenados cronologicamente (B1 a B6).
  - Novos registros locais salvos aparecem imediatamente com texto de E1 e E2, status de conclusão e auditoria do responsável.
  - Ao clicar em "Ver no Painel Executivo" após submeter um formulário, a rota navega passando `?projeto={key}`, selecionando automaticamente o projeto recém-atualizado.

### 2. Correção no Fluxo de Persistência e Atualização (`FormularioEntregas.vue` e `src/routers/entregas_jornada.py`)
- Em `FormularioEntregas.vue`, toda submissão de acompanhamento utiliza `POST /api/v1/entregas-jornada/formulario`.
- O endpoint `POST /formulario` no backend opera como um upsert confiável por `(projeto, periodo)`, garantindo que se o registro já existia localmente ele é atualizado com efeito cascata, e se ainda não existia no SQLite ele é criado imediatamente e associado àquele projeto e período.
- No endpoint `PUT /formularios/{id}`, caso o `id` não exista no banco local, é feito fallback para localizar pelo `(projeto, periodo)` do payload e salvar adequadamente.

### 3. Blindagem de RBAC (Gerente de Projeto)
- No frontend:
  - `DefaultLayout.vue` exibe link de "Configurações" apenas se `authStore.isAdmin`.
  - `router/index.ts` intercepta tentativas diretas de acessar `/configuracoes` por qualquer perfil que não seja `ADMINISTRADOR` (incluindo `GERENTE_PROJETO`) e redireciona para a página principal (`/`).
  - `FormularioEntregas.vue` trava o select de projeto no `authStore.assignedProject` quando `authStore.isGerenteProjeto` for verdadeiro.
- No backend:
  - `src/routers/admin.py` protege todas as rotas com `verify_admin_group`, que exige grupo AD ou usuário `admin`. Usuários com perfil `GERENTE_PROJETO` recebem HTTP 403 Forbidden.
  - `src/routers/entregas_jornada.py` invoca `validar_permissao_projeto()`, bloqueando com HTTP 403 qualquer tentativa de um `GERENTE_PROJETO` manipular um projeto diferente do seu `projeto_atribuido`.
