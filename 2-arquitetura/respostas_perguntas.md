# Respostas às cinco perguntas obrigatórias do caso Ônibus

## 1. Como o validador aceita a passagem sem rede, e como o sistema descobre depois que a mesma passagem foi usada em dois ônibus?

**Aceitar sem rede.** A decisão de aceitar ou recusar roda no próprio validador, com regras e dados mínimos locais, organizada em Arquitetura Hexagonal para isolar leitor de cartão, armazenamento e comunicação. O cartão carrega o saldo operacional e um número de sequência incrementado a cada uso, então o segundo ônibus lê o estado já atualizado mesmo sem rede. Sem conexão, as validações ficam em fila local por até 4 h.

**Descobrir depois.** Quando a rede volta, as validações sobem por evento. Cartões e Recarga detecta sequências repetidas para o mesmo cartão vindas de validadores diferentes e emite um evento de divergência para bloqueio e ajuste. A idempotência dos consumidores trata apenas o reenvio da mesma mensagem, e não o uso em dois ônibus.

**Sustentação:** ADR 0008, ADR 0001, ADR 0002; C4 Contêineres (Validador Embarcado, Cartões e Recarga, Barramento de Eventos).

## 2. Como o saldo do cartão fica consistente entre recarga no aplicativo e uso no ônibus, com atraso de sincronização?

O saldo central é de Cartões e Recarga, que tem consistência forte nas operações que o alteram. No ônibus, o saldo operacional vive no cartão, e o validador o atualiza a cada uso. A recarga do aplicativo só é creditada depois que o adaptador do banco confirma a liquidação, fica como crédito pendente no backend e é gravada no cartão no primeiro uso em um validador que já sincronizou a lista de pendências. Cada recarga tem identificador único, aplicado uma só vez mesmo com reenvio. O custo assumido é que a recarga do aplicativo pode demorar até esse primeiro uso.

**Sustentação:** ADR 0008, ADR 0002, ADR 0003; C4 Contêineres.

## 3. Como a telemetria escala no pico sem derrubar o restante do sistema?

A Telemetria é uma unidade independente, com broker persistente próprio, separado do barramento de eventos financeiros. A ingestão só publica no broker, e um consumidor idempotente grava a série temporal e atualiza o modelo de leitura, então um consumidor lento não trava a ingestão. A Informação ao Passageiro lê apenas o modelo de leitura (CQRS) e escala sozinha no rush. O pico previsto é de cerca de 400 posições por segundo (5 vezes as 80 da média, premissas do caso). Validação, Recarga e Conciliação não compartilham broker nem armazenamento com a telemetria.

**Sustentação:** ADR 0007, ADR 0004, ADR 0001; C4 Contêineres.

## 4. Como o repasse mensal é recalculado se uma regra de tarifa mudou no meio do mês?

As regras tarifárias pertencem à Conciliação e são versionadas por período de vigência, nunca sobrescritas. Os fatos financeiros ficam imutáveis, com suas datas. O fechamento é um pipeline de etapas independentes: recuperar os eventos do período, validar, selecionar a regra vigente na data de cada viagem, calcular, consolidar por operadora e publicar o fechamento. Se uma regra muda, o pipeline roda de novo sobre os mesmos eventos e a versão vigente em cada data, e o ajuste entra como evento de compensação. A contestação registrada pelo Atendimento aciona o mesmo reprocessamento.

**Sustentação:** ADR 0002, ADR 0005, ADR 0006, ADR 0001; C4 Componentes.

## 5. Como o histórico de viagens de uma pessoa é apagado quando ela pede, sem quebrar a conciliação financeira?

Os eventos financeiros guardam apenas uma referência opaca ao passageiro, sem nome, CPF nem hash de CPF. Nome, CPF e demais dados ficam no Cadastro de Passageiros. Quando o pedido chega pelo Atendimento, o cadastro e o vínculo da referência são apagados, e o mesmo vale para as cópias em Banco de Cartões, Modelo de Leitura e registro do Atendimento. Os eventos não são tocados, então o valor, a data, a regra e a operadora de cada viagem continuam reconstruíveis, e o total do repasse não muda. O spike prova exatamente isso: o total conciliado é o mesmo antes, depois da eliminação e depois do reprocessamento.

**Limites assumidos.** A conservação de dados pode ser exigida por lei em certas hipóteses, e a referência ainda liga as viagens entre si, o que é risco residual de reidentificação a validar com a responsável por conformidade. Cópias de segurança precisam de prazo de expiração definido.

**Complemento, pergunta do Envelope E** ("Como vocês guardam tudo para sempre e ainda assim apagam o que a lei manda apagar?"): guarda-se para sempre o fato financeiro, que não identifica ninguém, e apaga-se o dado pessoal, que tem ciclo de retenção próprio.

**Sustentação:** ADR 0005, ADR 0002, ADR 0006; C4 Componentes; spike `3-spike/exemplo.py`.
