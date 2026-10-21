# formulario-entregas Specification

## Purpose
Permite o preenchimento, validação e atualização direta das entregas bimestrais dos projetos estratégicos da II Jornada de Gestão do HC-UFPE através de interface web interativa espelhada no modelo oficial do REDCap, gravando auditoria e sincronizando dados em tempo real.

## Requirements

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

### Requirement: Exibição condicional de entregas conforme projeto selecionado
O sistema SHALL aplicar branching logic dinâmico para renderizar apenas as duas entregas oficiais (E1 e E2) correspondentes ao projeto selecionado, contendo títulos oficiais, campo de conclusão ("Sim" ou "Não") e área de texto para evolução.

#### Scenario: Exibição das entregas do projeto selecionado
- **WHEN** o usuário seleciona um dos 5 projetos no formulário
- **THEN** a interface exibe exclusivamente os cards e labels oficiais de E1 e E2 do respectivo projeto conforme a especificação do REDCap

#### Scenario: Bloqueio de campos antes da seleção
- **WHEN** o usuário ainda não tiver selecionado um projeto ou um período
- **THEN** os campos de entrega permanecem ocultos ou desabilitados com orientação visual clara

### Requirement: Validação de campos obrigatórios e formato
O sistema SHALL validar a obrigatoriedade dos campos de evolução das entregas antes da submissão, tornando o campo 'COMENTÁRIOS / EVOLUÇÃO DA ENTREGA' estritamente opcional a partir do momento em que a respectiva entrega for marcada como concluída ou já tiver sido concluída em bimestre anterior.

#### Scenario: Submissão com campos pendentes
- **WHEN** o usuário tenta enviar o formulário com uma entrega não concluída sem preencher o texto da evolução
- **THEN** a submissão é bloqueada e o sistema destaca visualmente os campos obrigatórios não preenchidos

#### Scenario: Submissão com dados válidos
- **WHEN** todos os campos obrigatórios estão preenchidos ou as entregas concluídas possuem comentários opcionais
- **THEN** o botão de envio é habilitado e a requisição de salvamento é despachada

#### Scenario: Submissão de entrega concluída com comentários opcionais
- **WHEN** uma entrega está marcada como concluída ("Sim") ou foi concluída em bimestre anterior
- **THEN** o campo de comentários da referida entrega torna-se opcional, permitindo o envio sem preenchimento forçado de texto

### Requirement: Submissão, auditoria e feedback institucional
O sistema SHALL persistir os dados do formulário respondido em banco de dados local com trilha de auditoria, mantendo o REDCap estritamente somente-leitura, emitindo notificações via Toast e apresentando confirmação oficial.

#### Scenario: Sucesso na gravação e confirmação institucional
- **WHEN** a submissão é gravada com êxito no banco de dados local da aplicação
- **THEN** o sistema exibe notificação em Toast, registra auditoria imutável e disponibiliza modal de agradecimento oficial da II Jornada de Gestão

### Requirement: Efeito cascata na conclusão e cancelamento de entregas bimestrais
O sistema SHALL propagar automaticamente o status de entrega concluída para todos os bimestres subsequentes, carregando o formulário de bimestres posteriores com a entrega já assinalada como concluída, exibindo tag de conclusão prévia e permitindo cancelamento explícito pelo usuário com efeito cascata também nos bimestres posteriores.

#### Scenario: Propagação de conclusão para bimestres posteriores
- **WHEN** o usuário define uma entrega como concluída no bimestre atual
- **THEN** o sistema registra o status concluído para o período vigente e replica a conclusão nos bimestres seguintes

#### Scenario: Cancelamento em cascata nos bimestres subsequentes
- **WHEN** o usuário altera o status de uma entrega de concluída para não concluída em determinado bimestre
- **THEN** o sistema propaga a alteração de não concluída para os bimestres subsequentes

#### Scenario: Abertura de formulário para bimestre subsequente após conclusão prévia
- **WHEN** o usuário seleciona um projeto e um período onde uma entrega já havia sido concluída em período anterior
- **THEN** o formulário inicializa a entrega automaticamente como concluída ("Sim"), exibe badge informativo de conclusão anterior e torna o comentário opcional

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

### Requirement: Bloqueio absoluto do menu de configurações para Gerente de Projeto
O sistema SHALL restringir o acesso ao menu e às rotas de configurações exclusivamente para o perfil de ADMINISTRADOR, impedindo qualquer acesso por usuários com perfil GERENTE_PROJETO.

#### Scenario: Gerente de projeto tenta acessar configurações
- **WHEN** um usuário com perfil GERENTE_PROJETO navega pela aplicação ou tenta acessar a URL /configuracoes
- **THEN** o menu de configurações não é visível na barra lateral e o acesso à rota /configuracoes é redirecionado para a página principal

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
