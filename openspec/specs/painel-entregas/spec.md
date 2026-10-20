# painel-entregas Specification

## Purpose
Permite o monitoramento executivo em tempo real das entregas e metas dos 5 projetos estratégicos da II Jornada de Gestão do HC-UFPE com dados integrados da API REDCap.

## Requirements

### Requirement: Coleta e filtragem de registros do REDCap
O sistema SHALL consumir a API do REDCap utilizando token de autenticação e filtrar apenas os registros cujos formulários estejam marcados com status concluído (form_1_complete igual a 2).

#### Scenario: Sucesso na coleta de registros completos
- **WHEN** o serviço de integração realiza a requisição à API do REDCap
- **THEN** o sistema processa e armazena em memória apenas registros que possuam form_1_complete igual a 2

#### Scenario: Filtragem de registros incompletos
- **WHEN** a API retorna registros com form_1_complete igual a 0 ou 1
- **THEN** o sistema descarta esses registros para evitar exibição de dados parciais

### Requirement: Cálculo de métricas executivas e matriz de entregas
O sistema SHALL calcular a quantidade total de entregas cadastradas, o quantitativo de entregas concluídas, o percentual de evolução e o status individual das entregas E1 e E2 de cada projeto.

#### Scenario: Cálculo consolidado de entregas
- **WHEN** os dados processados contêm marcações de conclusão de entregas
- **THEN** o sistema retorna a contagem de entregas concluídas e a taxa de conclusão percentual

#### Scenario: Matriz de entregas por período
- **WHEN** o usuário seleciona um período bimestral específico
- **THEN** o sistema avalia o status das entregas E1 e E2 estritamente para o período solicitado

### Requirement: Rastreamento do ciclo bimestral dos projetos
O sistema SHALL mapear a linha temporal dos 6 bimestres da jornada (B1 a B6) para cada um dos 5 projetos estratégicos, informando se há registros entregues.

#### Scenario: Exibição do status dos bimestres
- **WHEN** o painel de um projeto é consultado
- **THEN** o sistema retorna o status de cada um dos 6 bimestres com indicação visual de entrega realizada ou pendente

### Requirement: Interface web corporativa de acompanhamento
O sistema SHALL disponibilizar no frontend corporativo visão detalhada por projeto com abas dedicadas, timeline bimestral com textos de evolução, filtros e acionador de sincronização manual.

#### Scenario: Seleção de projeto por aba
- **WHEN** o usuário clica na aba de um projeto específico
- **THEN** a interface exibe as descrições oficiais de E1 e E2, os cards de evolução por bimestre e o status de cada entrega

#### Scenario: Sincronização manual
- **WHEN** o usuário aciona o botão de atualizar dados
- **THEN** o cache da integração é invalidado e novos dados são coletados da API do REDCap
