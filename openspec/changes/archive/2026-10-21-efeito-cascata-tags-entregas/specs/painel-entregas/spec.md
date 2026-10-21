# Spec Delta: painel-entregas

## MODIFIED Requirements

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
