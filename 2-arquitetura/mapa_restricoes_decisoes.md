# Mapa de restrições e decisões

**Caso Ônibus, Envelope E (operação fiscalizada).** Cada linha liga uma restrição do envelope (**E**) ou um requisito que aperta do caso (**C**) à decisão que a atende. Fontes das restrições: enunciado "Um problema, cinco realidades" (premissas de dimensionamento, subdomínios e Envelope E).

| ID | Origem | Restrição / requisito | Decisão que a atende | ADR | Diagrama |
|---|---|---|---|---|---|
| C01 | Caso | Validação responde em até 300 ms, mesmo sem conexão | Decisão de aceitar ou recusar executada localmente no validador (Hexagonal), com o estado no cartão | 0001, 0008 | Contêineres |
| C02 | Caso | Ônibus fica até 4 h sem rede | Validações ficam em fila local e sincronizam por evento quando a rede volta | 0008, 0001 | Contêineres |
| C03 | Caso | Nunca aceitar a mesma passagem duas vezes; descobrir depois o uso em dois ônibus | Número de sequência no cartão; Cartões e Recarga detecta sequências repetidas de validadores diferentes na sincronização; consumidores idempotentes | 0008, 0002 | Contêineres |
| C04 | Caso | Saldo consistente entre recarga no aplicativo e uso no ônibus, com atraso de sincronização | Cartões e Recarga é dono do saldo; recarga do aplicativo fica pendente e é gravada no cartão no primeiro uso em validador sincronizado | 0002, 0008 | Contêineres |
| C05 | Caso | Fraude de recarga zero | Recarga só é creditada após o adaptador do banco confirmar a liquidação | 0003 | Contêineres |
| C06 | Caso | Conciliação com o banco | Eventos financeiros imutáveis e adaptador de banco e adquirente conferem cada recarga contra o extrato | 0005, 0003 | Contêineres, Componentes |
| C07 | Caso | Telemetria absorve 80 posições/s e até 5 vezes isso no pico sem perder dados | Broker persistente próprio para telemetria, consumidor idempotente, unidade que escala sozinha | 0007, 0004 | Contêineres |
| C08 | Caso | Informação ao passageiro: pico no rush e custo baixo fora do pico | CQRS: modelo de leitura próprio, escalado separadamente pela carga | 0007, 0004 | Contêineres |
| C09 | Caso | Recalcular o mês com as regras vigentes na data de cada viagem | Regras tarifárias versionadas por vigência, dentro da Conciliação; fatos financeiros imutáveis | 0002, 0005 | Componentes |
| C10 | Caso | Fechamento em etapas e reprocessável | Pipes and Filters no fechamento, dentro de um hexágono com regras e portas | 0001 | Componentes |
| C11 | Caso | Contestação do repasse em até 30 dias | Atendimento registra a contestação e aciona o reprocessamento; ajustes entram como eventos de compensação | 0006, 0005 | Contêineres, Componentes |
| C12 | Caso | 25% dos cartões com gratuidade ou desconto | Perfil de gratuidade pertence a Cartões e Recarga, pedido pelo Atendimento; o desconto é regra tarifária versionada | 0002, 0006 | Contêineres |
| C13 | Caso | Banco, adquirente, operadoras e legado impõem formatos | Um adaptador por sistema externo, sem ESB; legado só lido por adaptador | 0003 | Contexto, Contêineres |
| C14 | Caso | Janelas de indisponibilidade dos terceiros | Falha contida no adaptador; recarga fica pendente e é reenviada | 0003 | Contêineres |
| C15 | Caso | Atendimento com trilha de quem alterou o quê | Log append-only próprio do Atendimento, com evento de alteração | 0006 | Contêineres |
| C16 | Caso | Subdomínios com cargas e evolução diferentes | Microsserviços só onde há carga própria; Atendimento em Monolito Modular | 0001, 0004 | Contêineres |
| C17 | Caso | Fechamento consolida todas as operadoras | Arquitetura Celular descartada; consolidação na Conciliação | 0001 | Componentes |
| E01 | Envelope E | Tribunal de Contas audita o repasse; tudo precisa ser reconstruível | Event Sourcing localizado em Cartões e Recarga e na Conciliação, eventos append-only com compensação | 0005, 0002 | Contexto, Componentes |
| E02 | Envelope E | LGPD com direito ao esquecimento | Eventos guardam só referência opaca; dados pessoais no Cadastro de Passageiros, cuja eliminação não toca os eventos | 0005, 0002 | Contêineres, Componentes |
| E03 | Envelope E | Trilha de auditoria completa na nuvem pública | Trilha financeira no Event Store; trilha do Atendimento no log próprio; chamadas externas rastreadas com correlação | 0005, 0006, 0004 | Contêineres |
| E04 | Envelope E | Rastreabilidade operacional na nuvem pública | Logs, métricas e rastreamento centralizados, com identificador de correlação | 0004 | Contêineres |
| E05 | Envelope E | 15 desenvolvedores | Microsserviços limitados a cinco unidades; nada de microsserviços em todos os subdomínios | 0001, 0004 | Contêineres |
| E06 | Envelope E | 1 responsável por conformidade | Relatório de fechamento gerado automaticamente; eliminação de dados pessoais local e automatizável | 0004, 0005 | Componentes |

## Síntese

Arquitetura híbrida com um estilo por perfil de capacidade e uma fronteira explícita por composição (ADR 0001). Serverless e Arquitetura Celular foram consideradas e descartadas, com motivo, no mesmo ADR.
