# Design

## Context

Atualmente, o sistema permite que gerentes de projeto preencham relatórios bimestrais para qualquer um dos 6 bimestres (Julho/Agosto 2026 até Maio/Junho 2027) disponíveis na matriz da II Jornada de Gestão. O acesso a configurações é restrito a administradores (`ADMIN_GROUP` ou perfil `ADMINISTRADOR`), enquanto gerentes de projeto operam estritamente no seu respectivo projeto atribuído.
Para governança institucional dos prazos de entrega, a administração do hospital necessita habilitar ou fechar bimestres específicos para novos relatórios, resguardando o direito dos gerentes de consultar, atualizar ou excluir relatórios que já haviam sido submetidos antes do fechamento.

## Goals / Non-Goals

**Goals:**
- Prover interface visual e endpoints para o Administrador controlar a disponibilidade de cada um dos 6 bimestres (`0` a `5`).
- Garantir que bimestres desabilitados bloqueiem novas criações em branco tanto no frontend quanto no backend (rejeição com HTTP 400).
- Preservar integralmente as operações de leitura, atualização e exclusão de relatórios já gravados em bimestres inativos para o respectivo gerente do projeto.
- Registrar todas as alterações de disponibilidade de bimestres na trilha de auditoria (`audit_logs`) com dados anteriores e novos.

**Non-Goals:**
- Não altera o schema dos relatórios de entrega (`FormularioResposta`) nem a lógica de somente-leitura do REDCap.
- Não remove ou oculta dados históricos dos dashboards consolidados (painel analítico continua exibindo histórico normalmente).

## Decisions

### 1. Modelo de Persistência `ConfiguracaoBimestre` no SQLite Local
- **Escolha**: Criar modelo SQLAlchemy `ConfiguracaoBimestre` (`src/models/configuracao_bimestre.py`) mapeando tabela `configuracao_bimestres`:
  - `periodo_code` (String, PK / Unique, '0' a '5')
  - `periodo_nome` (String, descritivo ex: 'Julho/Agosto 2026')
  - `ativo` (Boolean, default True)
  - `updated_by` (String)
  - `updated_at` (DateTime)
- **Bootstrap automático**: Caso a tabela esteja vazia na inicialização do serviço, o sistema auto-insere os 6 bimestres com `ativo = True`.
- **Alternativa descartada**: Variável em arquivo `.env` (não permitiria alteração dinâmica em tempo de execução via tela de administração com auditoria).

### 2. Endpoints no Backend
- `GET /api/admin/bimestres-config`: Retorna a lista de configurações dos 6 bimestres. Requer `verify_admin_group`.
- `PUT /api/admin/bimestres-config/{periodo_code}`: Atualiza status `ativo` (True/False) de um período. Requer `verify_admin_group` e registra log em `audit_logs`.
- `GET /api/v1/entregas-jornada/bimestres-status`: Endpoint autenticado (qualquer usuário logado) que retorna o dicionário com status de cada bimestre (`{"0": {"ativo": True, ...}}`) para consumo pelo formulário.

### 3. Validação Diferencial: Novo Cadastro vs Atualização Prévia
- No endpoint `POST /api/v1/entregas-jornada/formulario`:
  - O backend verifica se já existe registro no banco para `(projeto, periodo)`.
  - Se NÃO existir (`existing is None`): verifica se o período está ativo em `ConfiguracaoBimestre`. Se inativo, rejeita com HTTP 400 (`O período selecionado está fechado para novos preenchimentos.`).
  - Se JÁ existir (`existing is not None`): trata-se de atualização permitida de relatório pré-existente. A operação prossegue normalmente com atualização e recálculo de cascata.
- Nos endpoints `PUT /formularios/{id}` e `DELETE /formularios/{id}`:
  - Operam estritamente sobre registros pré-existentes, sendo permitidos para o gerente autorizado mesmo se o bimestre estiver inativo.

### 4. Interface Frontend
- **Configurações (`Configuracoes.vue`)**:
  - Nova aba "Bimestres da Jornada" com tabela ou cards dos 6 bimestres, badges de status ("Disponível" / "Encerrado") e toggles interativos para ativar/desativar com Toast de confirmação.
- **Formulário de Entregas (`FormularioEntregas.vue`)**:
  - Ao carregar ou ao trocar de projeto, mapeia os bimestres que já possuem relatórios para o projeto.
  - Para bimestres inativos:
    - Se o projeto NÃO tem registro: exibe texto `[Encerrado para novo preenchimento]` e desabilita a opção (`disabled`).
    - Se o projeto JÁ tem registro: exibe badge explicativo informando `[Bimestre encerrado - Permissão de edição mantida]`, permitindo selecionar, visualizar, alterar ou excluir o formulário.

## Risks / Trade-offs

- **[Risco] Tentativa de submissão direta contornando interface desabilitada** → *Mitigação*: Backend valida no `POST /formulario` consultando o banco antes de inserir e rejeita requisições não autorizadas com HTTP 400.
- **[Risco] Bloqueio indevido de edição de relatórios legítimos** → *Mitigação*: A checagem de bimestre inativo só barra inserções se não houver registro prévio daquele projeto e período no banco.
- **[Risco] Perda de performance ao consultar status** → *Mitigação*: A tabela possui apenas 6 linhas indexadas por chave primária, com consulta assíncrona instantânea.
