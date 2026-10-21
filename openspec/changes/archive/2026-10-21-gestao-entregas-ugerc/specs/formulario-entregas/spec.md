# Spec Delta: formulario-entregas

## MODIFIED Requirements

### Requirement: Submissão, auditoria e feedback institucional
O sistema SHALL persistir os dados do formulário respondido em banco de dados local com trilha de auditoria, mantendo o REDCap estritamente somente-leitura, emitindo notificações via Toast e apresentando confirmação oficial.

#### Scenario: Sucesso na gravação e confirmação institucional
- **WHEN** a submissão é gravada com êxito no banco de dados local da aplicação
- **THEN** o sistema exibe notificação em Toast, registra auditoria imutável e disponibiliza modal de agradecimento oficial da II Jornada de Gestão

## ADDED Requirements

### Requirement: Efeito cascata na conclusão e cancelamento de entregas bimestrais
O sistema SHALL propagar automaticamente o status de entrega concluída para todos os bimestres subsequentes ao período atual e, de forma equivalente, propagar o cancelamento da conclusão para os bimestres posteriores.

#### Scenario: Propagação de conclusão para bimestres posteriores
- **WHEN** o usuário define uma entrega como concluída no bimestre atual
- **THEN** o sistema registra o status concluído para o período vigente e replica a conclusão nos bimestres seguintes

#### Scenario: Cancelamento em cascata nos bimestres subsequentes
- **WHEN** o usuário altera o status de uma entrega de concluída para não concluída em determinado bimestre
- **THEN** o sistema propaga a alteração de não concluída para os bimestres subsequentes

### Requirement: Operações de consulta, atualização e exclusão de formulários
O sistema SHALL disponibilizar funcionalidades completas de leitura detalhada, atualização de respostas prévias e exclusão/reinicialização de registros de entregas bimestrais.

#### Scenario: Atualização de formulário existente
- **WHEN** o usuário autenticado edita os dados de um formulário já registrado e confirma a alteração
- **THEN** o sistema atualiza o registro no banco de dados, recalcula os impactos em cascata e emite notificação via Toast

#### Scenario: Exclusão de resposta de formulário
- **WHEN** o usuário autorizado solicita a exclusão de uma resposta registrada para determinado projeto e período
- **THEN** o sistema remove o registro do banco de dados e atualiza a matriz analítica

### Requirement: Restrição de operações CRUD por projeto para Gerentes de Projeto
O sistema SHALL garantir que usuários com perfil "Gerente de Projeto" só possam criar, editar ou excluir formulários correspondentes estritamente ao projeto que lhes foi atribuído, enquanto administradores possuem acesso a todos os projetos.

#### Scenario: Gerente operando no seu próprio projeto
- **WHEN** um gerente de projeto executa operações de gravação ou edição no projeto a ele atribuído
- **THEN** a operação é autorizada e processada com sucesso

#### Scenario: Bloqueio de operação em projeto não atribuído
- **WHEN** um gerente de projeto tenta enviar, alterar ou excluir formulário de um projeto diferente do seu
- **THEN** o sistema rejeita a operação com erro de permissão insuficiente (HTTP 403)
