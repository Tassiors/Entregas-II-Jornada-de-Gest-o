# Proposal

## Why

O acompanhamento das metas e entregas dos 5 projetos estratégicos da II Jornada de Gestão (2026–2027) do HC-UFPE exige um painel corporativo integrado aos padrões institucionais de tecnologia do SETISD. A versão anterior em Streamlit serviu como protótipo, mas agora o sistema precisa ser integrado à arquitetura padrão do hospital (FastAPI + Vue 3/Tailwind + Autenticação EBSERH + OpenSpec), garantindo rastreabilidade, persistência de configurações, auditoria e facilidade de manutenção a longo prazo.

## What Changes

- Criação do serviço e cliente de integração com a API do REDCap (com cache inteligente e fallback).
- Estruturação dos modelos de dados para os 5 projetos (P1 a P5), períodos bimestrais (Jul/Ago 2026 a Mai/Jun 2027) e matriz de entregas (E1 e E2).
- Criação dos endpoints da API REST no backend FastAPI (`/api/v1/entregas-jornada/...`) para fornecer resumo executivo, matriz de entregas por projeto, status bimestral e sincronização em tempo real com o REDCap.
- Desenvolvimento da interface corporativa no frontend Vue 3 seguindo a identidade visual oficial do HC-UFPE/EBSERH e o framework do SETISD:
  - Resumo de métricas gerais (taxa de conclusão, total de entregas concluídas).
  - Indicadores visuais de entregas por projeto (chips E1 e E2 com status).
  - Barra compacta de bimestres (B1 a B6) com indicação visual de entrega.
  - Abas para os 5 projetos com cards detalhados por período e timeline de evolução.
  - Filtro interativo por período bimestral e botão de sincronização/atualização forçada.
- Testes automatizados cobrindo os serviços de processamento de dados do REDCap e endpoints da API.

## Capabilities

### New Capabilities
- `painel-entregas`: Coleta e processamento de dados do REDCap, cálculo de métricas executivas de entregas da II Jornada de Gestão, e disponibilização de interface de acompanhamento bimestral por projeto.

### Modified Capabilities

## Impact

- Novos endpoints e serviços sob `src/` no backend FastAPI.
- Novas views, componentes, rotas e stores Pinia no frontend Vue 3 sob `frontend/src/`.
- Adição de variáveis de ambiente para a API do REDCap no `.env` e `.env.example`.
- Sem impactos negativos em módulos existentes do framework SETISD.