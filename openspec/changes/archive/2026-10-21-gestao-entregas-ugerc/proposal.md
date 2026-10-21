# Proposal

## Why

A gestão e o acompanhamento das entregas da II Jornada de Gestão do HC-UFPE evoluíram de um protótipo integrado ao REDCap para um sistema corporativo completo sob a governança da Unidade de Gestão da Estratégia, de Riscos e Controles Internos (UGERC). Para garantir segurança dos dados, isolamento de papéis e integridade das metas, faz-se necessário:
1. Desacoplar a gravação do REDCap, tornando-o estritamente somente-leitura e persistindo todas as respostas localmente em banco de dados;
2. Implementar regra de negócio com efeito cascata para a conclusão de entregas ao longo dos bimestres;
3. Estabelecer controle de acesso baseado em papéis (RBAC), criando o perfil "Gerente de Projeto" com escopo estritamente restrito ao seu respectivo projeto e isolando as configurações para administradores;
4. Oferecer operações completas de CRUD (Criação, Leitura, Atualização e Exclusão) para formulários;
5. Modernizar o layout do painel analítico e aprimorar a experiência do usuário com notificações em Toast e limpeza dos menus.

## What Changes

- **Armazenamento Local e REDCap Read-Only**: Criação de modelo e tabela de banco de dados (`formulario_respostas`) para persistir todas as respostas preenchidas. O serviço REDCap passa a ser estritamente somente-leitura (sem importação remota).
- **Efeito Cascata na Conclusão de Entregas**: Quando uma entrega (E1 ou E2) for marcada como concluída em um bimestre $B_k$, seu status permanece concluído nos bimestres seguintes ($B_{k+1}$ a $B_5$). O cancelamento da conclusão em $B_k$ também propaga o cancelamento nos bimestres subsequentes.
- **CRUD Completo de Formulários**: Endpoints e interface para listagem, consulta detalhada, edição e exclusão de formulários de entrega respondidos.
- **Perfil Gerente de Projeto e RBAC Específico**: Inclusão do perfil `GERENTE_PROJETO` vinculado a um dos 5 projetos no cadastro de usuários. Gestores só podem executar operações CRUD sobre seu próprio projeto, enquanto o painel analítico permanece público para consulta.
- **Acesso Exclusivo a Configurações**: A rota e o item de menu de Configurações tornam-se de acesso estritamente restrito a usuários com perfil `ADMINISTRADOR`.
- **Limpeza do Menu Lateral**: Remoção dos links desnecessários ("Início", "Componentes" e "Exemplo") da barra lateral (`DefaultLayout.vue`), mantendo foco em "Painel II Jornada", "Formulário de Entregas" e "Configurações" (para administradores).
- **Ajustes na Interface do Formulário**: Remoção do seletor de "Status do Formulário", remoção do botão "Voltar ao Painel" e substituição de alertas nativos pelos Toasts do framework (`vue-toastification`).
- **Remodelação do Painel Executivo**: Novo layout dos cards e indicadores no `PainelEntregas.vue`, remoção do botão "Preencher Acompanhamento" do cabeçalho da II Jornada e modernização visual.
- **Padronização Institucional UGERC**: Substituição de referências a "Setor de Tecnologia da Informação e Saúde Digital — SETISD" por "Unidade de Gestão da Estratégia, de Riscos e Controles Internos - UGERC" nos cabeçalhos, rodapés e metadados.

## Capabilities

### New Capabilities
- `gestao-usuarios`: Gerenciamento centralizado de usuários locais com perfis RBAC, incluindo perfil de Gerente de Projeto associado a projeto específico e bloqueio de acesso a configurações para não-administradores.

### Modified Capabilities
- `formulario-entregas`: O formulário passa a persistir localmente em banco de dados, com REDCap em modo read-only, suporte a CRUD completo (edição e exclusão), efeito cascata de conclusão bimestral, restrição de acesso por projeto para gestores e feedback via Toasts.
- `painel-entregas`: Redesenho executivo da interface do painel da II Jornada, remoção do botão de preenchimento do cabeçalho, atualização da identidade visual para UGERC e leitura combinada de entregas a partir do banco de dados local.

## Impact

- **Banco de Dados**: Criação do modelo `FormularioResposta` e `UsuarioSistema` no banco de dados SQLite (`data/app.db`).
- **Backend / APIs**: Novos endpoints de CRUD em `src/routers/entregas_jornada.py`, validação de permissão de gestor por projeto em `src/routers/entregas_jornada.py` e persistência de usuários em `src/routers/admin.py`.
- **Frontend**: Reformulação de `PainelEntregas.vue`, atualização de `FormularioEntregas.vue`, `DefaultLayout.vue`, `Configuracoes.vue`, `router/index.ts` e serviços `entregasService.ts`.
- **Governança**: 100% de conformidade com o auditor de conformidade arquitetural do HC-UFPE.
