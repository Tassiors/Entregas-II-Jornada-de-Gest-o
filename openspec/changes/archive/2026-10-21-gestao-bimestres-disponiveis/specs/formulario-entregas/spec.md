# Spec Delta

## MODIFIED Requirements

### Requirement: Seleção de projeto e período com carregamento automático
O sistema SHALL disponibilizar seletores padronizados para os 5 projetos estratégicos (P1 a P5) e para os 6 períodos bimestrais (B1 a B6), consultando a API para carregar dados prévios se o registro já existir e indicando o status de disponibilidade de preenchimento de cada bimestre definido pelo administrador.

#### Scenario: Projeto e período selecionados sem registro anterior
- **WHEN** o usuário seleciona um projeto e um período para o qual ainda não há entrega registrada e o bimestre está habilitado
- **THEN** o formulário inicializa os campos de entrega vazios com status pendente de preenchimento

#### Scenario: Projeto e período com registro existente
- **WHEN** o usuário seleciona uma combinação de projeto e período que já possui registro no sistema
- **THEN** o sistema preenche automaticamente os campos de conclusão e comentários com os valores salvos anteriormente para facilitar a edição

#### Scenario: Bimestre desabilitado sem registro anterior
- **WHEN** o usuário visualiza o seletor de períodos e um determinado bimestre está desabilitado pelo administrador sem registro existente para o projeto
- **THEN** a opção do bimestre é desabilitada para seleção com indicação visual de período fechado para novos cadastros

#### Scenario: Bimestre desabilitado com registro existente
- **WHEN** o usuário seleciona um bimestre desabilitado pelo administrador mas que já possui formulário submetido para o projeto
- **THEN** o sistema carrega normalmente os dados prévios com indicação visual de que o período está fechado para novos cadastros mas mantém permissão total de consulta e edição

### Requirement: Operações de consulta, atualização e exclusão de formulários
O sistema SHALL disponibilizar funcionalidades completas de leitura detalhada, atualização de respostas prévias e exclusão de registros de entregas bimestrais, inclusive se o bimestre correspondente tiver sido desabilitado pelo administrador após a submissão.

#### Scenario: Atualização de formulário existente
- **WHEN** o usuário autenticado edita os dados de um formulário já registrado e confirma a alteração
- **THEN** o sistema atualiza o registro no banco de dados, recalcula os impactos em cascata e emite notificação via Toast

#### Scenario: Exclusão de resposta de formulário
- **WHEN** o usuário autorizado solicita a exclusão de uma resposta registrada para determinado projeto e período
- **THEN** o sistema remove o registro do banco de dados e atualiza a matriz analítica

#### Scenario: Leitura, atualização e remoção em bimestre desabilitado
- **WHEN** o gerente do projeto acessa um formulário previamente submetido cujo bimestre foi posteriormente desabilitado pelo administrador
- **THEN** o sistema garante a integridade de todas as operações de leitura, atualização dos dados salvos e remoção definitiva do registro

## ADDED Requirements

### Requirement: Governança de disponibilidade de bimestres pelo Administrador
O sistema SHALL disponibilizar funcionalidade exclusiva para o perfil ADMINISTRADOR no menu de Configurações para habilitar ou desabilitar cada um dos 6 bimestres (B1 a B6) para novos preenchimentos, gravando cada alteração na trilha de auditoria.

#### Scenario: Administrador altera status de disponibilidade de bimestre
- **WHEN** o administrador altera a chave de ativação de um bimestre e confirma a alteração
- **THEN** o sistema atualiza a configuração no banco de dados local e registra a ação na tabela de auditoria com os estados anterior e novo

#### Scenario: Gerente de projeto tenta acessar configuração de bimestres
- **WHEN** um usuário com perfil GERENTE_PROJETO tenta acessar a interface ou a API de configuração de bimestres
- **THEN** o sistema rejeita o acesso com erro de permissão (HTTP 403) ou redirecionamento

### Requirement: Bloqueio de novas submissões em bimestres desabilitados
O sistema SHALL impedir a submissão de novos formulários em bimestres que tenham sido desabilitados pelo administrador, rejeitando requisições no backend.

#### Scenario: Tentativa de novo cadastro em período fechado
- **WHEN** uma requisição de criação de novo formulário é despachada para um bimestre desabilitado e que não possua registro prévio no banco
- **THEN** o sistema recusa a gravação com código HTTP 400 e mensagem informativa de período fechado para novos preenchimentos
