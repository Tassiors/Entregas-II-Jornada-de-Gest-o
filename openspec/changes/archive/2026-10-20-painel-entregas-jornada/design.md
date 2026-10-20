# Design

## Context

A II Jornada de Gestão do HC-UFPE possui 5 projetos estratégicos (P1: HC-UFPE 360°, P2: Jornada do Paciente, P3: Logística de Suprimentos, P4: Valorização do Trabalhador e P5: Qualidade da Preceptoria), cada um com duas entregas principais (E1 e E2). Os dados de acompanhamento são registrados no REDCap da EBSERH ao longo de 6 bimestres entre Julho de 2026 e Junho de 2027.

O sistema precisa migrar do modelo Streamlit isolado para a arquitetura corporativa do SETISD HC-UFPE (FastAPI no backend e Vue 3 + TailwindCSS no frontend), mantendo fidelidade total às regras de negócio e apresentando uma interface rica, responsiva e alinhada à identidade visual do hospital.

## Goals / Non-Goals

**Goals:**
- Implementar cliente assíncrono para o REDCap com cache em memória (TTL configurável de 300 segundos) e mecanismo de renovação sob demanda.
- Construir endpoints REST sob `/api/v1/entregas-jornada` que entreguem dados limpos e agregados (resumo executivo, status bimestral, matriz de projetos e detalhamento por projeto).
- Desenvolver interface completa no frontend Vue 3 utilizando componentes Tailwind e layout corporativo do SETISD.
- Garantir testes unitários e de integração para os serviços de processamento de dados e rotas.

**Non-Goals:**
- Edição ou gravação de dados de volta no REDCap (a aplicação opera em modo leitura/dashboard).
- Criação de novos instrumentos de pesquisa no REDCap.

## Decisions

- **Decisão 1: Arquitetura de Serviço de Integração REDCap no Backend**:
  - *Opção escolhida*: Centralizar a chamada HTTP e processamento analítico no backend FastAPI (`src/services/redcap_service.py` e `src/routers/entregas_jornada.py`), com cache com TTL.
  - *Alternativa considerada*: Chamar o REDCap diretamente do frontend. Descartada por questões de segurança (exposição do token de API institucional) e CORS.

- **Decisão 2: Preservação das Regras de Domínio e Filtragem do REDCap**:
  - Somente registros com `form_1_complete == "2"` são considerados nas análises.
  - Valores de conclusão `"0"` indicam conclusão confirmada, `"1"` em andamento, e vazio ou outro valor como não informado.
  - Agrupamento bimestral padronizado em 6 períodos oficiais (Jul/Ago 26 a Mai/Jun 27).

- **Decisão 3: Frontend Vue 3 com Pinia e TailwindCSS**:
  - Criação de uma store dedicada `useEntregasStore` para gerenciamento de estado e requisições à API.
  - Interface com visual corporativo moderno: banner com cores institucionais, cards de KPI, barra de progresso bimestral compacta, abas dinâmicas de projetos e cards de evolução com timeline.

## Risks / Trade-offs

- [Instabilidade ou lentidão na API do REDCap EBSERH] → Implementação de cache de dados com fallback em caso de erro temporário e tratamento resiliente de timeout.
- [Alteração na nomenclatura de campos no formulário REDCap] → Mapeamento centralizado de campos no arquivo de configuração do backend.

## Migration Plan

1. Configurar variáveis de ambiente do REDCap (`REDCAP_API_URL` e `REDCAP_TOKEN`) no `.env`.
2. Implementar serviços de dados e rotas no backend FastAPI.
3. Implementar a view e componentes no frontend Vue 3.
4. Validar os dados e testes.
5. Fazer commit e subir para o repositório GitHub.