# Spec Delta: painel-entregas

## MODIFIED Requirements

### Requirement: Interface web corporativa de acompanhamento
O sistema SHALL disponibilizar no frontend corporativo layout executivo remodelado sob a identidade institucional da UGERC, com cards de indicadores reorganizados, visão detalhada por projeto com abas dedicadas, timeline bimestral e sincronização de dados.

#### Scenario: Seleção de projeto por aba
- **WHEN** o usuário clica na aba de um projeto específico
- **THEN** a interface exibe as descrições oficiais de E1 e E2, os cards de evolução por bimestre e o status de cada entrega

#### Scenario: Sincronização manual
- **WHEN** o usuário aciona o botão de atualizar dados
- **THEN** o cache da integração é invalidado e novos dados são coletados da API do REDCap

## ADDED Requirements

### Requirement: Identidade institucional UGERC e painel somente-leitura público
O sistema SHALL exibir em todo o painel executivo a vinculação à Unidade de Gestão da Estratégia, de Riscos e Controles Internos (UGERC), mantendo a visualização dos dados aberta para consulta geral e sem o botão de preenchimento no cabeçalho da II Jornada.

#### Scenario: Exibição da identificação institucional da UGERC
- **WHEN** qualquer usuário acessa a página inicial ou o painel de entregas
- **THEN** o cabeçalho e rodapé exibem com destaque "Unidade de Gestão da Estratégia, de Riscos e Controles Internos - UGERC"

#### Scenario: Visualização do painel sem botões de escrita no topo
- **WHEN** a tela principal da II Jornada é carregada
- **THEN** o cabeçalho apresenta apenas o filtro de período e botão de atualização, omitindo o botão de preenchimento de acompanhamento
