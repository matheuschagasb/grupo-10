# ADR 0004: implantar por unidade com liberação gradual e observabilidade central

**Status:** aceito

**Contexto:** A Telemetria tem pico de 5 vezes a média, a Informação ao Passageiro tem pico de leitura no rush e a Validação precisa funcionar sem nuvem. A operação roda em nuvem pública, com 15 desenvolvedores e 1 responsável por conformidade. O Envelope E exige rastrear as operações relevantes para a fiscalização.

**Decisão:** Cada unidade do ADR 0001 tem pipeline de entrega próprio e sobe por liberação gradual com reversão, e os validadores são atualizados em ondas, a partir de uma linha, mantendo a versão anterior até a confirmação. Telemetria e Informação ao Passageiro escalam pela carga; logs, métricas, rastreamento e chamadas externas ficam em serviço central com identificador de correlação, e o relatório de fechamento é gerado automaticamente.

**Alternativas consideradas:**
- Backend em uma única unidade de implantação: descartado porque cargas diferentes escalariam juntas.
- Todos os subdomínios como unidades independentes: descartado pelo custo operacional.
- Atualizar todos os validadores de uma vez: descartado porque uma versão com defeito pararia a frota inteira.
- Observabilidade por unidade, sem serviço central: descartada porque impede seguir uma operação entre unidades.

**Consequências:**
- Positivas: cada unidade escala e é implantada sem tocar as outras; falha em uma onda de validadores afeta poucas linhas; o relatório automático reduz a carga sobre a responsável por conformidade.
- Negativas: mais unidades para operar; contratos entre unidades devem permanecer compatíveis durante implantações separadas; a atualização gradual mantém versões diferentes de validador em campo ao mesmo tempo.

**Fontes:** ABREU (2026): §9.7 (custo real de Microsserviços), §18.5 (observabilidade e correlação). Premissas de dimensionamento e requisitos do caso Ônibus (enunciado "Um problema, cinco realidades"); Envelope E.
