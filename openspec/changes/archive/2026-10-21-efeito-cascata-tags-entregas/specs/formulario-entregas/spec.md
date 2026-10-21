# Spec Delta: formulario-entregas

## MODIFIED Requirements

### Requirement: Validação de campos obrigatórios e formato
O sistema SHALL validar a obrigatoriedade dos campos de evolução das entregas antes da submissão, tornando o campo 'COMENTÁRIOS / EVOLUÇÃO DA ENTREGA' estritamente opcional a partir do momento em que a respectiva entrega for marcada como concluída ou já tiver sido concluída em bimestre anterior.

#### Scenario: Submissão com campos pendentes
- **WHEN** o usuário tenta enviar o formulário com uma entrega não concluída sem preencher o texto da evolução
- **THEN** a submissão é bloqueada e o sistema destaca visualmente os campos obrigatórios não preenchidos

#### Scenario: Submissão com dados válidos
- **WHEN** todos os campos obrigatórios estão preenchidos ou as entregas concluídas possuem comentários opcionais
- **THEN** o botão de envio é habilitado e a requisição de salvamento é despachada

#### Scenario: Submissão de entrega concluída com comentários opcionais
- **WHEN** uma entrega está marcada como concluída ("Sim") ou foi concluída em bimestre anterior
- **THEN** o campo de comentários da referida entrega torna-se opcional, permitindo o envio sem preenchimento forçado de texto

### Requirement: Efeito cascata na conclusão e cancelamento de entregas bimestrais
O sistema SHALL propagar automaticamente o status de entrega concluída para todos os bimestres subsequentes, carregando o formulário de bimestres posteriores com a entrega já assinalada como concluída, exibindo tag de conclusão prévia e permitindo cancelamento explícito pelo usuário com efeito cascata também nos bimestres posteriores.

#### Scenario: Propagação de conclusão para bimestres posteriores
- **WHEN** o usuário define uma entrega como concluída no bimestre atual
- **THEN** o sistema registra o status concluído para o período vigente e replica a conclusão nos bimestres seguintes

#### Scenario: Cancelamento em cascata nos bimestres subsequentes
- **WHEN** o usuário altera o status de uma entrega de concluída para não concluída em determinado bimestre
- **THEN** o sistema propaga a alteração de não concluída para os bimestres subsequentes

#### Scenario: Abertura de formulário para bimestre subsequente após conclusão prévia
- **WHEN** o usuário seleciona um projeto e um período onde uma entrega já havia sido concluída em período anterior
- **THEN** o formulário inicializa a entrega automaticamente como concluída ("Sim"), exibe badge informativo de conclusão anterior e torna o comentário opcional
