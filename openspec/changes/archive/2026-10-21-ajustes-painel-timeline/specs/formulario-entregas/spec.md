# formulario-entregas Specification

## MODIFIED Requirements

### Requirement: Restrição de operações CRUD por projeto para Gerentes de Projeto
O sistema SHALL garantir que usuários com perfil "Gerente de Projeto" só possam criar, editar ou excluir formulários correspondentes estritamente ao projeto que lhes foi atribuído, com seletor bloqueado na interface e rejeição pelo backend em caso de divergência.

#### Scenario: Gerente operando no seu próprio projeto
- **WHEN** um gerente de projeto executa operações de gravação ou edição no projeto a ele atribuído
- **THEN** a operação é autorizada e processada com sucesso

#### Scenario: Bloqueio de operação em projeto não atribuído
- **WHEN** um gerente de projeto tenta enviar, alterar ou excluir formulário de um projeto diferente do seu
- **THEN** o sistema rejeita a operação com erro de permissão insuficiente (HTTP 403)

#### Scenario: Bloqueio estrito de projeto não atribuído
- **WHEN** um usuário com perfil GERENTE_PROJETO acessa a tela de formulário ou tenta submeter dados
- **THEN** o seletor de projeto permanece fixado no seu projeto atribuído e qualquer requisição direta para outro projeto é rejeitada com HTTP 403 Forbidden

## ADDED Requirements

### Requirement: Bloqueio absoluto do menu de configurações para Gerente de Projeto
O sistema SHALL restringir o acesso ao menu e às rotas de configurações exclusivamente para o perfil de ADMINISTRADOR, impedindo qualquer acesso por usuários com perfil GERENTE_PROJETO.

#### Scenario: Gerente de projeto tenta acessar configurações
- **WHEN** um usuário com perfil GERENTE_PROJETO navega pela aplicação ou tenta acessar a URL /configuracoes
- **THEN** o menu de configurações não é visível na barra lateral e o acesso à rota /configuracoes é redirecionado para a página principal
