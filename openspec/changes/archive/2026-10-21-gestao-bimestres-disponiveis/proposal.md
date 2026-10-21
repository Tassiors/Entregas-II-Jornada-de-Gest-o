# Proposal

## Why

A gestão dos prazos de envio de relatórios da II Jornada de Gestão exige que o Administrador possa abrir ou fechar bimestres específicos para novos preenchimentos, impedindo a submissão de novos acompanhamentos fora da janela institucional de cada ciclo.
Entretanto, o fechamento de um período não pode prejudicar gerentes que já registraram seus dados: relatórios previamente submetidos em bimestres agora desabilitados devem permanecer acessíveis para consulta detalhada, correções/atualizações e até mesmo exclusão pelo gerente responsável pelo respectivo projeto.

## What Changes

- **Painel Administrativo de Disponibilidade de Bimestres**: Criação de controle visual na tela de Configurações exclusivo para administradores, permitindo habilitar ou desabilitar cada um dos 6 períodos bimestrais (B1 a B6) para novos preenchimentos.
- **Persistência e Trilha de Auditoria**: Tabela de banco de dados para armazenar o estado ativo/inativo de cada bimestre, com registro de alterações na trilha de auditoria corporativa (`audit_logs`).
- **Validação Inteligente de Submissão**:
  - Tentativa de **novo preenchimento** (sem registro anterior) em bimestre desabilitado é bloqueada na interface e rejeitada pelo backend com HTTP 400.
  - Se o projeto **já possuir relatório registrado** no bimestre desabilitado, as permissões de leitura, atualização e exclusão continuam ativas para o respectivo gerente do projeto.
- **Adaptação Visual no Formulário**: O seletor de bimestres na tela de preenchimento sinaliza claramente quais períodos estão abertos para novos cadastros e quais estão encerrados, destacando a manutenção das funções de leitura/edição para formulários já enviados.

## Capabilities

### Modified Capabilities
- `formulario-entregas`: Inclusão de requisitos e cenários para governança de disponibilidade de bimestres pelo Administrador, bloqueio de novas submissões em bimestres inativos e garantia de manutenção de leitura, atualização e remoção para formulários previamente submetidos.

## Impact

- **Backend**:
  - Novo modelo SQLAlchemy `ConfiguracaoBimestre` em `src/models/configuracao_bimestre.py`.
  - Novos endpoints administrativos em `src/routers/admin.py`: `GET /api/admin/bimestres-config` e `PUT /api/admin/bimestres-config/{periodo_code}` com registro de auditoria.
  - Endpoint de consulta de disponibilidade para usuários autenticados em `src/routers/entregas_jornada.py`: `GET /api/v1/entregas-jornada/bimestres-status`.
  - Validação no endpoint `POST /api/v1/entregas-jornada/formulario` para impedir inserção de novas combinações de `(projeto, periodo)` desabilitadas, permitindo atualizações de registros pré-existentes.
- **Frontend**:
  - Nova aba/card "Disponibilidade de Bimestres" em `frontend/src/views/Configuracoes.vue` acessível a administradores.
  - Ajuste no seletor de bimestres em `frontend/src/views/entregas/FormularioEntregas.vue` para exibir status de bloqueio para novas submissões e liberar edição/exclusão se houver registro prévio.
- **Testes & Conformidade**:
  - Cobertura de testes automatizados com `pytest` e conformidade 100% com `audit_framework.py`.
