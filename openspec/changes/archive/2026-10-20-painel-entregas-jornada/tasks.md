# Tasks

## 1. Configuração e Dependências

- [x] 1.1 Configurar variáveis de ambiente do REDCap no `.env` e `.env.example` e verificar leitura das variáveis
- [x] 1.2 Atualizar `src/config.py` para suportar credenciais e parâmetros da API do REDCap

## 2. Backend - Serviço e Endpoints do REDCap

- [x] 2.1 Implementar `src/services/redcap_service.py` com integração à API, cache TTL e regras de filtragem (`form_1_complete == "2"`)
- [x] 2.2 Implementar funções analíticas de sumarização, matriz de entregas e status bimestral no serviço
- [x] 2.3 Criar router FastAPI `src/routers/entregas_jornada.py` com endpoints para dados consolidados, matriz, projetos e renovação de cache
- [x] 2.4 Registrar o router em `src/main.py` e verificar resposta dos endpoints via teste unitário

## 3. Frontend - Store e Interface Vue 3

- [x] 3.1 Criar a store Pinia `frontend/src/stores/entregas.ts` e serviço de API `frontend/src/services/entregasService.ts`
- [x] 3.2 Implementar a view principal `frontend/src/views/entregas/PainelEntregas.vue` com banner, métricas executivas, abas P1-P5, timeline e cards de evolução
- [x] 3.3 Adicionar a rota no Vue Router (`frontend/src/router/index.ts`) e o item de menu na barra lateral de navegação
- [x] 3.4 Validar o build do frontend e renderização dos dados com mock e com dados da API

## 4. Testes, Validação e Finalização

- [x] 4.1 Escrever e executar testes unitários automatizados em `tests/test_entregas_jornada.py`
- [x] 4.2 Executar validação completa do OpenSpec e arquivar a mudança
- [x] 4.3 Fazer commit das alterações e realizar push para o repositório remoto no GitHub

## Workflow follow-up

- Arquivar a mudança com `openspec archive painel-entregas-jornada`.
- Sincronizar especificações para o repositório principal.