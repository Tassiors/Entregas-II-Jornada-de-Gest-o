# Tasks

## 1. Backend: Modelo e Endpoints de Disponibilidade de Bimestres

- [x] 1.1 Criar o modelo SQLAlchemy `ConfiguracaoBimestre` em `src/models/configuracao_bimestre.py`, registrar em `src/main.py` e criar função de inicialização dos 6 bimestres
- [x] 1.2 Implementar endpoints administrativos em `src/routers/admin.py` (`GET /api/admin/bimestres-config` e `PUT /api/admin/bimestres-config/{periodo_code}`) com verificação de privilégios de administrador e registro na trilha de auditoria
- [x] 1.3 Adicionar endpoint de consulta de status de bimestres em `src/routers/entregas_jornada.py` (`GET /api/v1/entregas-jornada/bimestres-status`) para alimentar o formulário

## 2. Backend: Validação de Regras de Negócio e Sobrevivência de Relatórios

- [x] 2.1 Atualizar `POST /api/v1/entregas-jornada/formulario` para verificar status do bimestre antes de criar novo registro, bloqueando com HTTP 400 se inativo e permitindo atualização caso o relatório já exista
- [x] 2.2 Garantir que operações de leitura, atualização (`PUT /formularios/{id}`) e remoção (`DELETE /formularios/{id}`) permaneçam totalmente operacionais mesmo em bimestres inativos
- [x] 2.3 Escrever testes automatizados em `tests/test_bimestres_config.py` cobrindo consulta/edição por admin, bloqueio para gerente em configurações, rejeição de novo cadastro e manutenção de leitura/edição/exclusão de relatório pré-existente

## 3. Frontend: Gestão de Bimestres e Restrição Amigável no Formulário

- [x] 3.1 Implementar aba "Bimestres da Jornada" em `frontend/src/views/Configuracoes.vue` com controle visual dos 6 períodos para o perfil Administrador
- [x] 3.2 Atualizar `frontend/src/views/entregas/FormularioEntregas.vue` para desabilitar novas seleções de bimestres inativos sem relatório prévio e manter habilitado com aviso informativo para relatórios já existentes
- [x] 3.3 Compilar o frontend com `npm --prefix frontend run build` e validar conformidade de 100% com `python audit_framework.py .`
