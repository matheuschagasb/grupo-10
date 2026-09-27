# Mapa de Restrições e Decisões

## Caso Ônibus — Envelope E: Fiscalização e LGPD

O mapa abaixo relaciona as principais restrições do caso e do Envelope E às decisões arquiteturais adotadas. As referências apontam para os ADRs e diagramas C4 que sustentam cada decisão.

| ID | Restrição / requisito | Decisão arquitetural | Referências |
|---|---|---|---|
| **R01** | Validação embarcada deve responder em até **300 ms**, mesmo sem conexão. | Executar a decisão de validação localmente no equipamento embarcado, com regras e dados mínimos disponíveis no validador. A aplicação embarcada utiliza Arquitetura Hexagonal para separar a lógica de negócio da infraestrutura. | ADR 0001, ADR 0004, C4 Contêineres |
| **R02** | O ônibus pode permanecer até **4 horas sem conexão 4G**. | Registrar localmente as operações pendentes e sincronizá-las de forma assíncrona quando a conectividade retornar, utilizando eventos. | ADR 0001, ADR 0002, ADR 0004, C4 Contêineres |
| **R03** | Uma mesma validação não pode ser processada duas vezes. | Atribuir identificador único a cada validação, manter controle local das operações registradas e utilizar processamento idempotente no backend para evitar efeitos duplicados em reenvios. | ADR 0002, ADR 0004, ADR 0005, C4 Contêineres |
| **R04** | Saldo e recargas precisam manter consistência e não permitir crédito duplicado. | Manter Cartões e Recarga como proprietário do saldo, utilizando consistência forte nas operações financeiras e idempotência para impedir aplicação repetida de recargas. | ADR 0002, ADR 0005, C4 Contêineres |
| **R05** | Telemetria recebe cerca de **80 posições/s**, podendo atingir **5× o pico**, sem perda de dados. | Isolar Telemetria como capacidade independente e utilizar mensageria persistente com eventos, reentrega e consumidores idempotentes para desacoplar ingestão e processamento. | ADR 0001, ADR 0004, C4 Contêineres |
| **R06** | Informação ao passageiro possui alto volume de leitura e tolera atraso de alguns segundos. | Utilizar CQRS, mantendo modelos de leitura próprios derivados da telemetria e atualizados de forma assíncrona. | ADR 0001, ADR 0002, C4 Contêineres |
| **R07** | O fechamento mensal precisa ser recalculado com as regras vigentes na data de cada viagem. | Preservar os fatos financeiros necessários à reconstrução e manter regras tarifárias versionadas por período de vigência. Event Sourcing é utilizado apenas nos pontos em que o histórico precisa ser reconstruído. | ADR 0002, ADR 0005, C4 Componentes |
| **R08** | O processo de conciliação possui várias etapas e precisa permitir reprocessamento. | Utilizar Pipes and Filters para separar recuperação dos fatos, validação, seleção de regra vigente, cálculo e consolidação em etapas independentes. | ADR 0001, C4 Componentes |
| **R09** | O Tribunal de Contas precisa auditar e reconstruir os repasses financeiros. | Manter histórico financeiro auditável, regras utilizadas, resultados de conciliação e eventos necessários à reconstrução das operações. | ADR 0002, ADR 0005, C4 Contexto, C4 Componentes |
| **R10** | Histórico identificado de viagens é dado pessoal e está sujeito à LGPD. | Manter dados pessoais identificáveis separados dos eventos financeiros permanentes. A exclusão dos dados pessoais não remove os fatos financeiros necessários à auditoria. | ADR 0002, ADR 0005, C4 Componentes |
| **R11** | Banco, adquirente, operadoras e legado utilizam contratos e formatos impostos por terceiros. | Isolar integrações por Ports and Adapters, utilizando adaptadores específicos para traduzir os contratos externos para o modelo interno. ESB não será obrigatório. | ADR 0003, C4 Contexto, C4 Contêineres |
| **R12** | Os subdomínios possuem diferentes necessidades de carga, disponibilidade e evolução. | Implantar separadamente somente as capacidades que realmente necessitam de escala ou isolamento independentes, evitando microsserviços para todo o sistema. | ADR 0001, ADR 0004, C4 Contêineres |
| **R13** | A equipe possui **15 desenvolvedores e 1 responsável por compliance**. | Utilizar arquitetura híbrida com granularidade controlada. Capacidades simples ou de baixo volume, como Atendimento, permanecem agrupadas em Monolito Modular. | ADR 0001, ADR 0004, C4 Contêineres |
| **R14** | A solução será executada em nuvem pública e precisa permitir fiscalização e rastreabilidade. | Centralizar logs, métricas, rastreamento e registros de auditoria, utilizando identificadores de correlação entre serviços, eventos e integrações. | ADR 0003, ADR 0004, C4 Contêineres |
| **R15** | O fechamento precisa consolidar dados de diferentes operadoras e validações. | Não utilizar Arquitetura Celular, pois a separação rígida em células dificultaria consolidações globais. A consolidação fica sob responsabilidade da Conciliação. | ADR 0001, ADR 0002, C4 Componentes |

## Síntese das decisões

A solução adota uma arquitetura híbrida, utilizando diferentes estilos de acordo com as características de cada subdomínio. A Arquitetura Hexagonal é utilizada em Validação, Conciliação e Integrações; a Arquitetura Orientada a Eventos atende os fluxos assíncronos; CQRS é aplicado às consultas de informação ao passageiro; Pipes and Filters estrutura o fechamento financeiro; e Event Sourcing é utilizado de forma localizada nos dados financeiros que precisam ser reconstruídos.

Microsserviços são adotados somente quando existe necessidade concreta de escala ou isolamento, enquanto capacidades mais simples podem permanecer agrupadas. Serverless e Arquitetura Celular não são utilizados como estilos principais da solução.