# 🏥 II Jornada de Gestão HC-UFPE — Painel de Entregas

> **Painel Corporativo de Acompanhamento de Entregas (FastAPI + Vue 3 / Vite + OpenSpec)**  
> *Desenvolvido sobre o Framework SETISD do Hospital das Clínicas da UFPE (HC-UFPE / EBSERH).*

---

## 🎯 Sobre o Sistema

O **Painel de Entregas da II Jornada de Gestão do HC-UFPE** é um sistema corporativo para monitoramento em tempo real do cumprimento das metas e entregas dos 5 projetos estratégicos da instituição (Ciclo 2026–2027), consumindo dados diretamente da **API do REDCap da EBSERH**.

O projeto foi inteiramente estruturado com o **[OpenSpec](https://openspec.dev/)** seguindo a metodologia orientada a especificações (*spec-driven development*), migrando o protótipo anterior em Streamlit para o padrão web full-stack oficial do SETISD HC-UFPE.

### 📊 Funcionalidades
- **Painel Executivo por Projeto:** Abas dedicadas aos 5 projetos da Jornada (P1 a P5).
- **Indicadores Executivos (KPIs):** Taxa percentual de conclusão, quantidade de entregas finalizadas e total monitorado.
- **Matriz de Entregas E1 e E2:** Status binário de conclusão com cores institucionais e tooltips informativos.
- **Rastreamento Bimestral:** Visualização do ciclo de 6 bimestres (Jul/Ago 2026 até Mai/Jun 2027) com indicativo visual de entrega.
- **Timeline de Evolução:** Histórico bimestral com relatos textuais de avanço e badges de status.
- **Sincronização em Tempo Real:** Integração assíncrona com a API do REDCap com cache TTL inteligente e botão de sincronização forçada.
- **Metodologia OpenSpec:** Especificações duráveis em `openspec/specs/` e histórico arquivado em `openspec/changes/archive/`.

---
# Framework-SETISD-HC-UFPE

> **Arquitetura Web Full-Stack de ReferÃªncia (Python / FastAPI + Vue 3 / Vite)**  
> *PadrÃ£o Oficial de Desenvolvimento de Sistemas para o Hospital das ClÃ­nicas da UFPE (HC-UFPE / EBSERH).*

---

## ðŸ›ï¸ VisÃ£o Geral

O **Framework-SETISD-HC-UFPE** Ã© a base arquitetural monolÃ­tica limpa, desacoplada e padronizada para a criaÃ§Ã£o de novas aplicaÃ§Ãµes web corporativas no HC-UFPE. 

Ele consolida as melhores prÃ¡ticas de engenharia de software da equipe de TI (SETISD), garantindo que todos os novos sistemas sigam os mesmos padrÃµes de **tecnologia, seguranÃ§a, acesso a dados (AGHU) e interface visual**, alÃ©m de oferecer suporte pronto para **conteinerizaÃ§Ã£o opcional (Podman / Docker)**.

---

## ðŸš€ Pilares da Arquitetura

- **ðŸ›¡ï¸ AutenticaÃ§Ã£o HÃ­brida & SeguranÃ§a Corporativa (AD + RBAC + Security Headers):**
  - Suporte nativo ao **Active Directory (AD/LDAP Ebserh)** em produÃ§Ã£o com busca/validaÃ§Ã£o prÃ©via de usuÃ¡rios (`displayName`, `mail`, `department`).
  - Provedor **Mock** automÃ¡tico para desenvolvimento local sem dependÃªncia de rede.
  - Controle de sessÃ£o via **JWT Access Tokens** e **Refresh Tokens HttpOnly** com auto-renovaÃ§Ã£o transparente no frontend.
  - **ProteÃ§Ã£o de Rotas por PadrÃ£o (*Default-Private Router Pattern*):** Bloqueio automÃ¡tico de rotas hospitalares diretamente no `APIRouter` com `Depends(auth_handler.decode_token)`, liberando apenas exceÃ§Ãµes pÃºblicas explÃ­citas (`/api/login`, `/api/health`).
  - **Middleware de Security Headers:** ProteÃ§Ã£o nativa no backend FastAPI contra armazenamento de dados hospitalares em cache (`no-store, no-cache`), Clickjacking (`X-Frame-Options: DENY`), MIME sniffing (`nosniff`) e Cross-Site Scripting (XSS).
- **âš¡ Backend Moderno e AssÃ­ncrono (FastAPI):**
  - ConstruÃ­do com Python 3.12+, FastAPI e SQLAlchemy 2.0 com pools de conexÃµes assÃ­ncronas para o **PostgreSQL do AGHU**.
  - DocumentaÃ§Ã£o interativa **Swagger UI (`/docs`)** com autenticaÃ§Ã£o integrada via botÃ£o cadeado (**Authorize**).
  - Manipulador global de erros garantindo respostas padronizadas em formato JSON (`{"detail": "..."}`).
- **ðŸŽ¨ Frontend Reativo, UI Standard & Versionamento (Vue 3 / Vite / SemVer):**
  - Vue 3 (Composition API / TypeScript) empacotado e servido diretamente pelo FastAPI.
  - **Versionamento SemÃ¢ntico (SemVer `vX.Y.Z`):** ExibiÃ§Ã£o visÃ­vel da versÃ£o no rodapÃ© do menu lateral/layout frontend e alinhamento com Git Tags.
  - Interceptadores Axios automÃ¡ticos para injeÃ§Ã£o de tokens `Bearer` e renovaÃ§Ã£o de sessÃ£o sem deslogar o usuÃ¡rio.
  - Biblioteca de componentes base reusÃ¡veis (`DataTable`, `Modal`, `Button`, `Card`, `ProfileDropdown`).
- **ðŸ©º Monitoramento & ResiliÃªncia:**
  - Rota dedicada de diagnÃ³stico de infraestrutura `GET /api/health` para sondagem de status do servidor e dos bancos de dados.
- **ðŸ§ª Garantia de Qualidade & Testes Automatizados:**
  - SuÃ­te de testes integrada com `pytest` e `httpx` para validaÃ§Ã£o imediata de status do servidor, autenticaÃ§Ã£o e rotas.
- **ðŸš€ Deploy FlexÃ­vel & DevOps (Systemd / Podman / Docker):**
  - Suporte nativo Ã  execuÃ§Ã£o como serviÃ§o de segundo plano no Linux (`systemd`) para implantaÃ§Ã£o direta e leve em VMs.
  - Receita de build multi-estÃ¡gio em `Dockerfile` e orquestraÃ§Ã£o `compose.yaml` prontas para deploy em contÃªineres (Podman / Docker).

---

## ðŸ“‚ Estrutura do Projeto

```text
Framework-SETISD-HC-UFPE/
â”œâ”€â”€ .env.example          # Modelo de variÃ¡veis de ambiente
â”œâ”€â”€ AGENTS.md             # Diretrizes universais para Agentes de IA (Gemini, Claude, ChatGPT, Cursor)
â”œâ”€â”€ audit_framework.py    # Auditor de Conformidade Arquitetural
â”œâ”€â”€ Dockerfile            # Receita de build multi-estÃ¡gio (opcional para Podman / Docker)
â”œâ”€â”€ compose.yaml          # OrquestraÃ§Ã£o de contÃªiner para VMs (opcional)
â”œâ”€â”€ pyproject.toml        # DependÃªncias e configuraÃ§Ãµes do projeto Python (uv)
â”œâ”€â”€ requirements.txt      # Lista congelada de pacotes Python
â”œâ”€â”€ dev.sh                # Script de execuÃ§Ã£o paralela para desenvolvimento
â”œâ”€â”€ start.sh              # Script de build e execuÃ§Ã£o local do servidor
â”œâ”€â”€ docs/                 # DocumentaÃ§Ã£o detalhada da arquitetura e manuais
â”‚   â”œâ”€â”€ especificacao/    # Gabarito oficial de EspecificaÃ§Ã£o de Software (VisÃ£o, Requisitos, SDD)
â”‚   â”œâ”€â”€ ARCHITECTURE.md   # Arquitetura em camadas e padrÃ£o Provider
â”‚   â”œâ”€â”€ AUTHENTICATION.md # Sistema de AutenticaÃ§Ã£o (AD / Mock / JWT)
â”‚   â”œâ”€â”€ GUIA_DESENVOLVIMENTO.md # Tutorial passo a passo para criar novas telas/rotas
â”‚   â””â”€â”€ SETUP.md          # Guia de instalaÃ§Ã£o, testes e deploy
â”œâ”€â”€ frontend/             # AplicaÃ§Ã£o SPA Vue 3 (Vite + TypeScript)
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ components/   # Componentes visuais reusÃ¡veis (DataTable, Modal, etc.)
â”‚   â”‚   â”œâ”€â”€ layouts/      # Layouts de pÃ¡gina (DefaultLayout, LoginLayout)
â”‚   â”‚   â”œâ”€â”€ router/       # Roteamento e guards de autenticaÃ§Ã£o
â”‚   â”‚   â”œâ”€â”€ services/     # Cliente HTTP Axios com interceptadores de token
â”‚   â”‚   â”œâ”€â”€ stores/       # Gerenciamento de estado Pinia (auth, ui)
â”‚   â”‚   â””â”€â”€ views/        # Telas da aplicaÃ§Ã£o (Home, Login, Pacientes, Admin)
â”‚   â””â”€â”€ package.json      # DependÃªncias do frontend (Node.js)
â”œâ”€â”€ src/                  # Backend em Python FastAPI
â”‚   â”œâ”€â”€ auth/             # MÃ³dulos de autenticaÃ§Ã£o AD, JWT e Mock
â”‚   â”œâ”€â”€ controllers/      # Regras de negÃ³cio e casos de uso
â”‚   â”œâ”€â”€ helpers/          # FunÃ§Ãµes utilitÃ¡rias (sql_helper)
â”‚   â”œâ”€â”€ models/           # Modelos de dados SQLAlchemy (banco local)
â”‚   â”œâ”€â”€ providers/        # Acesso a dados desacoplado (Interfaces, Postgres, CSV, SQLs)
â”‚   â”œâ”€â”€ resources/        # Gerenciamento de conexÃµes de banco de dados
â”‚   â”œâ”€â”€ routers/          # Endpoints HTTP da API REST (Swagger)
â”‚   â””â”€â”€ main.py           # Ponto de entrada FastAPI e servidor SPA
â””â”€â”€ tests/                # Testes automatizados assÃ­ncronos (pytest)
    â”œâ”€â”€ conftest.py       # Fixtures de teste do FastAPI TestClient
    â”œâ”€â”€ test_auth.py      # Testes de login Mock e validaÃ§Ã£o de tokens
    â””â”€â”€ test_status_servidor.py # Testes de status da aplicaÃ§Ã£o e infraestrutura
```

---

## ðŸš¦ InÃ­cio RÃ¡pido (Quick Start)

### 1. ConfiguraÃ§Ã£o do Ambiente
```bash
# Clone o repositÃ³rio
git clone https://github.com/HCUFPE/Framework-SETISD-HC-UFPE.git
cd Framework-SETISD-HC-UFPE

# Copie o arquivo de exemplo de ambiente
cp .env.example .env
```

### 2. Executar em Modo Desenvolvimento (Hot Reload)
Executa o Backend (`http://localhost:8000`) e o Frontend Vite (`http://localhost:5173`) em paralelo:
```bash
./dev.sh
```

### 3. Rodar a SuÃ­te de Testes Automatizados
```bash
uv run pytest
```

---

## ðŸš€ OpÃ§Ãµes de Deploy em Servidores e VMs

O framework oferece flexibilidade total para colocar o sistema no ar:

### 1. ImplantaÃ§Ã£o Direta na VM (Sem ContÃªineres / Systemd)
Para quem prefere rodar direto no sistema operacional sem overhead de contÃªiner:
```bash
# 1. Instalar dependÃªncias e compilar frontend
uv sync && cd frontend && npm install && npm run build && cd ..

# 2. Teste rÃ¡pido manual (opcional)
./start.sh

# 3. ExecuÃ§Ã£o permanente como serviÃ§o do Linux (systemd)
sudo systemctl enable meu-sistema && sudo systemctl start meu-sistema
```

### 2. ImplantaÃ§Ã£o em ContÃªineres (Podman / Docker)
Para quem prefere isolamento completo:
```bash
# 1. Build da imagem e inicializaÃ§Ã£o do contÃªiner em background
podman compose up -d --build
# (ou com docker: docker compose up -d --build)

# 2. Verificar os logs da aplicaÃ§Ã£o
podman compose logs -f
```

A aplicaÃ§Ã£o ficarÃ¡ disponÃ­vel consolidada em `http://IP-DA-VM:8000/`. Para o passo a passo completo da configuraÃ§Ã£o do arquivo de serviÃ§o do Linux (`systemd`), consulte o [Guia de InstalaÃ§Ã£o e Deploy (`docs/SETUP.md`)](./docs/SETUP.md).

---

## ðŸ” Auditoria Automatizada de Conformidade Arquitetural

Para garantir que o desenvolvimento (seja feito por programadores ou com auxÃ­lio de copilotos de IA) esteja **100% conforme** com as diretrizes do hospital, o repositÃ³rio disponibiliza o script auditor [`audit_framework.py`](./audit_framework.py).

O auditor inspeciona automaticamente **11 pilares mandatÃ³rios**:
1. Stack Backend (Python 3.12+ / FastAPI / Uvicorn).
2. AutenticaÃ§Ã£o Corporativa (AD/LDAP Ebserh + RBAC HÃ­brido).
3. Conectividade HÃ­brida / Multi-provedor (Interfaces desacopladas PostgreSQL / CSV / Mocks).
4. AutenticaÃ§Ã£o Persistente e Cookies `HttpOnly` para Refresh Token.
5. ProteÃ§Ã£o de Rotas por PadrÃ£o (*Default-Private Router Pattern* no `APIRouter`).
6. Middleware de Security Headers HTTP (Defense-in-Depth contra XSS, Clickjacking e Cache).
7. GovernanÃ§a de Segredos (`src/config.py` e `.env.example` sem hardcode).
8. Trilha de Auditoria ImutÃ¡vel (`audit_logs` com `dados_anteriores`, `dados_novos` e `ip_origem`).
9. Layout Frontend Vue 3 SPA & Versionamento (SidebarNav Ã  esquerda + Marca + VersÃ£o **SemVer** no rodapÃ©).
10. SuÃ­te de Testes Automatizados (Testes de status HTTP e auth com `pytest`).
11. Monitoramento Zabbix (`/api/health`) e Manifesto para IA ([`AGENTS.md`](./AGENTS.md)).

### Como executar a verificaÃ§Ã£o:
```bash
# Auditar o prÃ³prio Framework ou o seu projeto em desenvolvimento:
uv run python audit_framework.py /caminho/para/o/seu/projeto
```
*(O script exibirÃ¡ o relatÃ³rio detalhado com a **Taxa de Conformidade (%)** e apontarÃ¡ o que precisa ser ajustado em caso de pendÃªncias).*

---

## ðŸ“š DocumentaÃ§Ã£o Detalhada

Para se aprofundar nos padrÃµes arquiteturais do hospital, consulte a documentaÃ§Ã£o oficial na pasta `docs/`:

- **[ Guia de InstalaÃ§Ã£o, ExecuÃ§Ã£o e Deploy (`docs/SETUP.md`)](./docs/SETUP.md)**
- **[ Gabarito de EspecificaÃ§Ã£o de Requisitos - SDD (`docs/especificacao/README.md`)](./docs/especificacao/README.md)**
- **[ Diretrizes e Regras para Agentes de IA (`AGENTS.md`)](./AGENTS.md)**
- **[ Arquitetura em Camadas e PadrÃ£o Provider (`docs/ARCHITECTURE.md`)](./docs/ARCHITECTURE.md)**
- **[ Manual de AutenticaÃ§Ã£o AD, Mock e JWT (`docs/AUTHENTICATION.md`)](./docs/AUTHENTICATION.md)**
- **[ PadrÃ£o de ConfiguraÃ§Ãµes e GestÃ£o de Segredos (`docs/SECRETS_E_CONFIGURACOES.md`)](./docs/SECRETS_E_CONFIGURACOES.md)**
- **[ PadrÃ£o de Auditoria e Trilha de MudanÃ§as (`docs/AUDITORIA_E_LOGS.md`)](./docs/AUDITORIA_E_LOGS.md)**
- **[ Tutorial de CriaÃ§Ã£o de Novas Funcionalidades (`docs/GUIA_DESENVOLVIMENTO.md`)](./docs/GUIA_DESENVOLVIMENTO.md)**

---

**SETISD - Setor de TI e SaÃºde Digital | HC-UFPE (EBSERH)**
