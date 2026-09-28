# ADR 0007: separar a ingestão de telemetria do modelo de leitura do passageiro

**Status:** aceito

**Contexto:** A Telemetria recebe 80 posições/s em média e até 5 vezes isso no pico, sem perder dados. A Informação ao Passageiro tolera segundos de atraso, tem pico de acessos no rush e custo baixo fora do pico. Um barramento único para telemetria e eventos financeiros faria os dois disputarem a mesma capacidade.

**Decisão:** A ingestão publica posições em um broker persistente próprio, separado do barramento financeiro, e um consumidor idempotente grava a série temporal e atualiza o modelo de leitura. A Informação ao Passageiro lê apenas esse modelo e escala separadamente.

**Alternativas consideradas:**
- Barramento único para tudo: descartado porque o pico de telemetria competiria com eventos financeiros.
- Ingestão gravando direto no armazenamento: descartada porque a lentidão dele limitaria a absorção do pico.
- Consulta do aplicativo direto no armazenamento de telemetria: descartada porque o pico do rush chegaria à ingestão.

**Consequências:**
- Positivas: o pico de telemetria não atinge Validação, Recarga nem Conciliação; consultas dos passageiros não afetam a ingestão; cada lado escala de forma independente.
- Negativas: um segundo broker para operar; o modelo de leitura fica defasado por alguns segundos; mensagens acumulam durante falha de consumidor e o reprocessamento exige idempotência.

**Fontes:** ABREU (2026): §11.2 (entrega ao menos uma vez), §14.2 (modelo de leitura e defasagem). Premissas de dimensionamento e requisitos do caso Ônibus (enunciado "Um problema, cinco realidades").
