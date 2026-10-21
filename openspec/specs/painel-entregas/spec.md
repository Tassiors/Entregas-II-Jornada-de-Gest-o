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
O sistema SHALL disponibilizar no frontend corporativo layout executivo limpo sob a identidade institucional da UGERC, com os 5 cards de projetos funcionando como seletores diretos sem texto 'Ver detalhes', sem barra de abas redundante, sem cards de topo, sem filtro de bimestre no cabeçalho, com espaçamento vertical positivo entre <header> e <main>, e com tags/badges destacadas nos cards das entregas quando concluídas.

#### Scenario: Seleção de projeto por aba
- **WHEN** o usuário clica no seletor ou card de um projeto específico
- **THEN** a interface exibe as descrições oficiais de E1 e E2, a timeline de evolução por bimestre e o status de cada entrega

#### Scenario: Seleção de projeto via card direto
- **WHEN** o usuário clica no card de um dos 5 projetos estratégicos
- **THEN** o card é visualmente destacado como ativo e a área de detalhamento exibe a identidade, descrições oficiais e timeline do respectivo projeto

#### Scenario: Ausência de cards de topo e de filtro de bimestre no cabeçalho
- **WHEN** a tela principal da II Jornada é carregada
- **THEN** a interface não exibe os cards de topo de KPIs nem o seletor de bimestre no cabeçalho, focando na matriz e no detalhamento do projeto selecionado

#### Scenario: Espaçamento vertical entre cabeçalho e corpo principal
- **WHEN** a tela do painel ou formulário de entregas é renderizada
- **THEN** o elemento <main> não sobrepõe o elemento <header>, mantendo margem superior positiva e respiro visual entre ambos

#### Scenario: Tags visíveis de conclusão nos cards das entregas
- **WHEN** uma entrega (E1 ou E2) for marcada como concluída no projeto ativo
- **THEN** o card de descrição oficial da entrega exibe uma tag destacada indicando o status de conclusão ("✅ Concluída"), e o card do projeto na matriz exibe badge com a contagem de entregas finalizadas

#### Scenario: Sincronização manual
- **WHEN** o usuário aciona o botão de atualizar dados
- **THEN** o cache da integração é invalidado e novos dados são coletados e consolidados

### Requirement: Acesso rápido e integração com formulário de acompanhamento
O sistema SHALL disponibilizar no painel executivo de entregas ação direta para direcionar o usuário ao formulário de cadastro ou atualização de entregas da II Jornada de Gestão.

#### Scenario: Acionamento da ação de registro a partir do painel
- **WHEN** o usuário clica no botão de registro de entregas no painel executivo
- **THEN** a interface redireciona para a tela do formulário, permitindo pré-selecionar o projeto e o período atualmente ativos no filtro do painel

### Requirement: Identidade institucional UGERC e painel somente-leitura público
O sistema SHALL exibir em todo o painel executivo a vinculação à Unidade de Gestão da Estratégia, de Riscos e Controles Internos (UGERC), mantendo a visualização dos dados aberta para consulta geral e sem o botão de preenchimento no cabeçalho da II Jornada.

#### Scenario: Exibição da identificação institucional da UGERC
- **WHEN** qualquer usuário acessa a página inicial ou o painel de entregas
- **THEN** o cabeçalho e rodapé exibem com destaque "Unidade de Gestão da Estratégia, de Riscos e Controles Internos - UGERC"

#### Scenario: Visualização do painel sem botões de escrita no topo
- **WHEN** a tela principal da II Jornada é carregada
- **THEN** o cabeçalho apresenta apenas o filtro de período e botão de atualização, omitindo o botão de preenchimento de acompanhamento

### Requirement: Linha do tempo fidedigna e dinâmica de registros e evolução
O sistema SHALL consolidar e exibir na timeline do projeto ativo todos os registros preenchidos no banco de dados local SQLite e os dados semente do REDCap, refletindo imediatamente novos acompanhamentos cadastrados.

#### Scenario: Visualização imediata de novo acompanhamento na timeline
- **WHEN** um formulário de entrega é submetido com sucesso no sistema para um determinado projeto e período
- **THEN** ao visualizar o projeto correspondente no painel, a timeline exibe imediatamente o período, comentários de evolução (E1 e E2), status de conclusão e identificação do usuário responsável
