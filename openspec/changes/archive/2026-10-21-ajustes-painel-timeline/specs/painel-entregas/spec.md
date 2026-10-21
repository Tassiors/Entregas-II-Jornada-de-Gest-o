# painel-entregas Specification

## MODIFIED Requirements

### Requirement: Interface web corporativa de acompanhamento
O sistema SHALL disponibilizar no frontend corporativo layout executivo limpo sob a identidade institucional da UGERC, com os 5 cards de projetos funcionando como seletores diretos sem texto 'Ver detalhes', sem barra de abas redundante, sem cards de topo e sem filtro de bimestre no cabeçalho.

#### Scenario: Seleção de projeto por aba
- **WHEN** o usuário clica no seletor ou card de um projeto específico
- **THEN** a interface exibe as descrições oficiais de E1 e E2, a timeline de evolução por bimestre e o status de cada entrega

#### Scenario: Seleção de projeto via card direto
- **WHEN** o usuário clica no card de um dos 5 projetos estratégicos
- **THEN** o card é visualmente destacado como ativo e a área de detalhamento exibe a identidade, descrições oficiais e timeline do respectivo projeto

#### Scenario: Ausência de cards de topo e de filtro de bimestre no cabeçalho
- **WHEN** a tela principal da II Jornada é carregada
- **THEN** a interface não exibe os cards de topo de KPIs nem o seletor de bimestre no cabeçalho, focando na matriz e no detalhamento do projeto selecionado

#### Scenario: Sincronização manual
- **WHEN** o usuário aciona o botão de atualizar dados
- **THEN** o cache da integração é invalidado e novos dados são coletados e consolidados

## ADDED Requirements

### Requirement: Linha do tempo fidedigna e dinâmica de registros e evolução
O sistema SHALL consolidar e exibir na timeline do projeto ativo todos os registros preenchidos no banco de dados local SQLite e os dados semente do REDCap, refletindo imediatamente novos acompanhamentos cadastrados.

#### Scenario: Visualização imediata de novo acompanhamento na timeline
- **WHEN** um formulário de entrega é submetido com sucesso no sistema para um determinado projeto e período
- **THEN** ao visualizar o projeto correspondente no painel, a timeline exibe imediatamente o período, comentários de evolução (E1 e E2), status de conclusão e identificação do usuário responsável
