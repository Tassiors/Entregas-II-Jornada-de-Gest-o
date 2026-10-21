# gestao-usuarios Specification

## Purpose
Permite a governança e o gerenciamento de usuários autorizados do sistema com controle de acesso baseado em papéis (RBAC), incluindo associação de gerentes aos projetos estratégicos e isolamento de privilégios administrativos.

## Requirements

### Requirement: Atribuição de perfil Gerente de Projeto vinculado
O sistema SHALL disponibilizar o perfil "Gerente de Projeto" no cadastro de usuários, exigindo a seleção obrigatória de um dos 5 projetos estratégicos da II Jornada de Gestão aos quais o usuário ficará vinculado.

#### Scenario: Cadastro de gerente com projeto atribuído
- **WHEN** o administrador cadastra ou edita um usuário com o perfil "Gerente de Projeto" e seleciona um dos 5 projetos
- **THEN** o sistema armazena a associação do projeto ao perfil do colaborador no banco de dados

#### Scenario: Validação de projeto obrigatório para gerente
- **WHEN** o administrador seleciona o perfil "Gerente de Projeto" mas não escolhe um projeto associado
- **THEN** o sistema bloqueia a gravação e exige a vinculação do projeto correspondente

### Requirement: Isolamento exclusivo das configurações para administradores
O sistema SHALL restringir a visibilidade do menu de Configurações e o acesso às rotas administrativas exclusivamente para usuários com o perfil de "ADMINISTRADOR".

#### Scenario: Acesso permitido para administrador
- **WHEN** um usuário autenticado com perfil "ADMINISTRADOR" acessa o sistema
- **THEN** o item de menu "Configurações" é exibido na barra lateral e a navegação para `/configuracoes` é autorizada

#### Scenario: Bloqueio de acesso para perfis não-administradores
- **WHEN** um usuário autenticado com perfil diferente de "ADMINISTRADOR" navega no sistema
- **THEN** o menu "Configurações" permanece oculto e qualquer tentativa direta de acesso a `/configuracoes` é redirecionada ou bloqueada com mensagem de acesso restrito

### Requirement: Persistência permanente de usuários autorizados
O sistema SHALL persistir a lista de colaboradores autorizados e seus respectivos papéis RBAC em tabela local do banco de dados relacional com trilha de auditoria para cada inclusão, edição ou inativação.

#### Scenario: Persistência permanente após reinicialização
- **WHEN** o administrador cadastra um novo usuário no sistema
- **THEN** os dados do usuário permanecem preservados de forma imutável no banco de dados local após reinicializações do servidor
