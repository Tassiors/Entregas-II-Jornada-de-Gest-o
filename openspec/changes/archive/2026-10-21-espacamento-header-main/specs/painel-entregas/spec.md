# Spec Delta

## MODIFIED Requirements

### Requirement: Interface web corporativa de acompanhamento
O sistema SHALL disponibilizar no frontend corporativo layout executivo limpo sob a identidade institucional da UGERC, com os 5 cards de projetos funcionando como seletores diretos sem texto 'Ver detalhes', sem barra de abas redundante, sem cards de topo, sem filtro de bimestre no cabeçalho e com espaçamento vertical positivo separando o cabeçalho (<header>) do conteúdo principal (<main>).

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

#### Scenario: Sincronização manual
- **WHEN** o usuário aciona o botão de atualizar dados
- **THEN** o cache da integração é invalidado e novos dados são coletados e consolidados
