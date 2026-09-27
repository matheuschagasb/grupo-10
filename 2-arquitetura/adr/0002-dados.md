# ADR 0002: distribuir a propriedade dos dados por subdomínio

**Status:** aceito

## Contexto

O sistema possui dados com diferentes requisitos de consistência, volume e retenção. Cartões e recargas lidam com saldo financeiro, a validação precisa continuar funcionando durante períodos sem conexão, a telemetria recebe dados continuamente e a conciliação precisa preservar histórico suficiente para auditoria e recálculo.

Uma base compartilhada entre todas as capacidades aumentaria o acoplamento. Ao mesmo tempo, a separação dos dados exige definir claramente quem é responsável por cada informação e onde será utilizada consistência forte ou eventual.

O Envelope E também exige que o histórico financeiro auditável não dependa da retenção permanente de dados pessoais identificáveis.

## Decisão

Distribuir a propriedade dos dados conforme as fronteiras definidas na ADR 0001. Cada subdomínio será responsável pela escrita de seus próprios dados e os demais deverão acessá-los apenas por interfaces ou eventos.

| Subdomínio | Propriedade dos dados | Consistência |
|---|---|---|
| **Cartões e Recarga** | Cartões, saldos, recargas e movimentações financeiras. | Forte nas operações que alteram saldo. |
| **Validação Embarcada** | Dados mínimos para operação offline e validações ainda não sincronizadas. | Local durante a desconexão e eventual com o backend. |
| **Telemetria** | Posições e demais dados enviados pela frota. | Assíncrona por eventos. |
| **Informação ao Passageiro** | Modelos de leitura derivados da telemetria. | Eventual, com atraso de alguns segundos aceitável. |
| **Conciliação** | Fechamentos, resultados e informações necessárias para auditoria e recálculo. | Forte na consolidação financeira. |
| **Atendimento** | Informações próprias do atendimento. | Consulta dados externos por interfaces publicadas pelos respectivos proprietários. |

Para permitir validação durante períodos sem conectividade, o cartão manterá o **estado operacional necessário à utilização offline**, incluindo o saldo utilizado pela validação e informações de controle da operação.

Quando uma passagem for aceita, o validador atualizará esse estado no cartão e registrará localmente a validação. Dessa forma, outro validador poderá obter o estado atualizado diretamente do cartão mesmo sem conexão com o backend.

Quando a conectividade retornar, as operações registradas localmente serão sincronizadas com Cartões e Recarga por eventos. Cada operação financeira possuirá identificador único e será processada de forma idempotente, evitando aplicação duplicada em casos de reenvio.

Entre subdomínios será utilizada consistência eventual sempre que não houver necessidade de resposta imediata. Consistência forte ficará limitada às operações que possuem invariantes financeiras.

Os dados pessoais identificáveis permanecerão separados dos fatos financeiros necessários à auditoria, permitindo ciclos distintos de retenção e exclusão.

## Alternativas consideradas

- **Banco único compartilhado:** descartado por aumentar o acoplamento entre os subdomínios.
- **Consistência forte global:** descartada porque dependeria de comunicação contínua, incompatível com a operação offline dos ônibus.
- **Consistência eventual para todos os dados:** descartada porque saldo, recarga e consolidação financeira possuem invariantes que precisam ser preservadas.
- **Manter apenas uma cópia do saldo central nos validadores:** descartado porque diferentes ônibus offline poderiam tomar decisões utilizando versões desatualizadas do mesmo saldo.
- **Armazenar dados pessoais diretamente no histórico financeiro permanente:** descartado por criar conflito entre a necessidade de auditoria e o ciclo de retenção e eliminação previsto para dados pessoais.

## Consequências

**Positivas:** reduz o acoplamento entre capacidades; permite operação offline; mantém consistência forte onde ela é necessária; evita que consultas da Informação ao Passageiro sobrecarreguem dados transacionais; e separa o histórico financeiro dos dados pessoais.

**Negativas:** existem diferentes representações do mesmo fato no sistema; sincronizações podem apresentar atraso; operações offline exigem idempotência e tratamento de falhas; e o estado operacional mantido no cartão aumenta a responsabilidade e a complexidade da validação embarcada.