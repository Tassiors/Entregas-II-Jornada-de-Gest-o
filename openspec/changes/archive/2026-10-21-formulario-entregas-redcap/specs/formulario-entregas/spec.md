# Spec Delta: formulario-entregas

## Purpose

Permite o preenchimento, validação e atualização direta das entregas bimestrais dos projetos estratégicos da II Jornada de Gestão do HC-UFPE através de interface web interativa espelhada no modelo oficial do REDCap, gravando auditoria e sincronizando dados em tempo real.

## ADDED Requirements

### Requirement: Seleção de projeto e período com carregamento automático
O sistema SHALL disponibilizar seletores padronizados para os 5 projetos estratégicos (P1 a P5) e para os 6 períodos bimestrais (B1 a B6), consultando a API para carregar dados prévios se o registro já existir.

#### Scenario: Projeto e período selecionados sem registro anterior
- **WHEN** o usuário seleciona um projeto e um período para o qual ainda não há entrega registrada
- **THEN** o formulário inicializa os campos de entrega vazios com status pendente de preenchimento

#### Scenario: Projeto e período com registro existente
- **WHEN** o usuário seleciona uma combinação de projeto e período que já possui registro no sistema
- **THEN** o sistema preenche automaticamente os campos de conclusão e comentários com os valores salvos anteriormente para facilitar a edição

### Requirement: Exibição condicional de entregas conforme projeto selecionado
O sistema SHALL aplicar branching logic dinâmico para renderizar apenas as duas entregas oficiais (E1 e E2) correspondentes ao projeto selecionado, contendo títulos oficiais, campo de conclusão ("Sim" ou "Não") e área de texto para evolução.

#### Scenario: Exibição das entregas do projeto selecionado
- **WHEN** o usuário seleciona um dos 5 projetos no formulário
- **THEN** a interface exibe exclusivamente os cards e labels oficiais de E1 e E2 do respectivo projeto conforme a especificação do REDCap

#### Scenario: Bloqueio de campos antes da seleção
- **WHEN** o usuário ainda não tiver selecionado um projeto ou um período
- **THEN** os campos de entrega permanecem ocultos ou desabilitados com orientação visual clara

### Requirement: Validação de campos obrigatórios e formato
O sistema SHALL validar a obrigatoriedade do preenchimento das justificativas e comentários de evolução para ambas as entregas antes de permitir a submissão.

#### Scenario: Submissão com campos pendentes
- **WHEN** o usuário tenta enviar o formulário sem preencher o texto da evolução de uma das entregas
- **THEN** a submissão é bloqueada e o sistema destaca visualmente os campos obrigatórios não preenchidos

#### Scenario: Submissão com dados válidos
- **WHEN** todos os campos obrigatórios estão preenchidos de acordo com as regras de negócio
- **THEN** o botão de envio é habilitado e a requisição de salvamento é despachada

### Requirement: Submissão, auditoria e feedback institucional
O sistema SHALL enviar o registro para a API do REDCap, registrar trilha de auditoria corporativa com usuário e IP de origem, invalidar o cache analítico e apresentar modal de agradecimento oficial.

#### Scenario: Sucesso na gravação e confirmação institucional
- **WHEN** a submissão é processada com êxito pelo backend e REDCap
- **THEN** o sistema exibe o texto de agradecimento oficial da II Jornada de Gestão e disponibiliza atalhos para um novo registro ou retorno ao painel executivo
