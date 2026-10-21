# Proposal: Ajustes Visuais no Painel da II Jornada, Correção da Timeline e Blindagem RBAC

## Why
Usuários identificaram redundâncias visuais no painel da II Jornada (cards de topo, link 'Ver detalhes' e abas redundantes duplicando a função dos cards de projetos), necessidade de remoção do filtro de bimestre no cabeçalho e relataram que as informações submetidas via formulário não estavam sendo refletidas na timeline. Além disso, é mandatório garantir que o perfil de Gerente de Projeto esteja estritamente restrito ao seu respectivo projeto e sem qualquer acesso ao menu de configurações.

## What Changes
1. **Painel II Jornada (`PainelEntregas.vue`):**
   - Remover os 4 cards executivos de topo (`Taxa Global`, `Entregas Finalizadas`, `Bimestres Monitorados` e `Gestão Estratégica`).
   - Remover o texto/link `'Ver detalhes ->'` nos cards dos 5 projetos (os cards continuam clicáveis e atuam diretamente como filtros de seleção).
   - Remover a barra horizontal de abas redundantes (`<div class="flex overflow-x-auto border-b ...">`).
   - Remover o seletor dropdown de Bimestre do cabeçalho do painel.
   - Corrigir a atualização da timeline para que qualquer registro submetido via formulário (ou presente no banco local/REDCap) apareça imediatamente com textos, status e dados de auditoria.
   - Sincronizar o projeto ativo selecionado quando o usuário for direcionado do formulário para o painel.
2. **Formulário de Entregas e Segurança RBAC:**
   - Assegurar que Gerentes de Projeto só submetam informações para seu respectivo projeto atribuído (select travado no frontend e validação com HTTP 403 no backend).
   - Unificar a submissão no endpoint `POST /formulario` para garantir persistência correta no banco local SQLite mesmo quando houver registros semente do REDCap.
   - Garantir que o perfil Gerente de Projeto não visualize o menu de configurações na interface e seja bloqueado caso tente acessar a rota `/configuracoes` ou os endpoints `/api/admin/*`.

## Capabilities
- Visualização limpa, direta e sem redundâncias no painel executivo da II Jornada.
- Exibição em tempo real de todas as evoluções submetidas via sistema na timeline dos projetos.
- Governança estrita de permissões garantindo isolamento total por projeto e proteção absoluta das configurações.
