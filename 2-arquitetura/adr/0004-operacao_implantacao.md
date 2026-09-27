# ADR 0004: implantar e escalar independentemente as capacidades críticas

**Status:** aceito

## Contexto

As capacidades do sistema possuem perfis operacionais diferentes. A Telemetria precisa suportar picos de até cinco vezes a carga normal, a Informação ao Passageiro possui grande volume de consultas e a Validação Embarcada precisa responder em até 300 ms mesmo durante períodos de até quatro horas sem conexão.

A solução será executada em nuvem pública e mantida por uma equipe de 15 desenvolvedores. Portanto, a independência operacional deve ser aplicada apenas onde houver necessidade concreta.

O Envelope E também exige rastreabilidade das operações relevantes para fiscalização.

## Decisão

Implantar e escalar separadamente apenas as capacidades que possuem necessidades próprias de carga, disponibilidade ou evolução.

| Capacidade | Decisão operacional |
|---|---|
| **Validação Embarcada** | Executar localmente nos validadores dos ônibus, sem depender da disponibilidade da nuvem para aceitar ou recusar uma passagem. Operações pendentes ficam armazenadas localmente até a sincronização. |
| **Cartões e Recarga** | Manter como unidade independente quando necessário para permitir evolução e escala próprias das operações financeiras. |
| **Telemetria** | Implantar como unidade independente, com ingestão desacoplada do processamento por mensageria persistente, permitindo absorver picos sem bloquear o recebimento de dados. |
| **Informação ao Passageiro** | Escalar separadamente utilizando os modelos de leitura do CQRS, sem aumentar diretamente a carga sobre a ingestão da Telemetria. |
| **Conciliação** | Executar separadamente dos fluxos de resposta imediata, permitindo fechamento e reprocessamento sem bloquear Validação, Recarga ou Telemetria. |
| **Atendimento** | Manter agrupado em uma única unidade modular enquanto não houver necessidade concreta de escala independente. |

As unidades independentes deverão permitir implantação e escala sem exigir a implantação simultânea de todo o sistema.

A Telemetria utilizará mensageria persistente entre ingestão e processamento. Mensagens não processadas com sucesso poderão ser entregues novamente, e os consumidores deverão ser idempotentes para impedir efeitos duplicados.

A operação deverá possuir observabilidade centralizada, incluindo logs, métricas e rastreamento das transações relevantes. Identificadores de correlação serão utilizados quando necessário para acompanhar uma operação entre serviços, eventos e integrações externas.

## Alternativas consideradas

- **Implantar todo o backend como uma única unidade:** descartado porque capacidades com cargas diferentes teriam de escalar e ser implantadas juntas.
- **Transformar todos os subdomínios em microsserviços:** descartado pelo aumento de complexidade operacional para uma equipe de 15 desenvolvedores.
- **Depender do backend para validar uma passagem:** descartado porque a operação precisa continuar funcionando sem conectividade.
- **Processar Telemetria de forma totalmente síncrona:** descartado porque consumidores lentos poderiam limitar a ingestão e comprometer a absorção dos picos.

## Consequências

**Positivas:** capacidades críticas podem escalar separadamente; picos de Telemetria ficam mais isolados; a Validação continua disponível sem rede; consultas dos passageiros não competem diretamente com a ingestão; e logs, métricas e rastreamento favorecem operação e fiscalização.

**Negativas:** múltiplas unidades aumentam a complexidade operacional; a equipe precisa tratar sincronização após períodos offline; mensagens podem acumular durante falhas; e contratos entre unidades precisam permanecer compatíveis durante implantações independentes.