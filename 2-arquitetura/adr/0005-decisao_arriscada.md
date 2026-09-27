# ADR 0005: limitar Event Sourcing ao histórico financeiro auditável

**Status:** aceito

## Contexto

O sistema precisa preservar informações suficientes para reconstruir operações financeiras, recalcular fechamentos e permitir auditoria dos repasses.

Ao mesmo tempo, o Envelope E exige tratamento adequado dos dados pessoais conforme a LGPD. Armazenar dados pessoais identificáveis diretamente em um histórico imutável criaria conflito com necessidades de retenção e eliminação.

Como Event Sourcing aumenta a complexidade de persistência, projeções e reprocessamento, seu uso deve ser restrito às partes do sistema que realmente precisam de reconstrução histórica.

## Decisão

Adotar Event Sourcing de forma localizada em Cartões/Recarga e Conciliação, apenas para os fatos financeiros necessários à auditoria, reconstrução de saldo e recálculo do fechamento.

Os eventos financeiros serão armazenados em formato append-only e representarão fatos ocorridos no sistema. Correções serão registradas por novos eventos de compensação ou reversão, sem alterar os eventos anteriores.

Os dados pessoais identificáveis não serão armazenados diretamente nesses eventos. Quando for necessário relacionar uma operação a uma pessoa, o evento manterá apenas um identificador de referência, enquanto os dados pessoais ficarão em armazenamento separado.

Dessa forma, os dados pessoais poderão seguir seu próprio ciclo de retenção e eliminação sem apagar os fatos financeiros necessários à auditoria.

As projeções geradas a partir dos eventos deverão poder ser reconstruídas e reprocessadas sem produzir efeitos financeiros duplicados.

O Event Sourcing não será utilizado como mecanismo de persistência geral dos demais subdomínios.

## Alternativas consideradas

- **Armazenar apenas o estado atual:** descartado porque dificultaria reconstruir o estado financeiro a partir dos fatos que produziram o resultado.
- **Aplicar Event Sourcing em todo o sistema:** descartado porque aumentaria a complexidade sem benefício equivalente para todos os subdomínios.
- **Armazenar dados pessoais diretamente nos eventos financeiros:** descartado porque vincularia a auditoria financeira à retenção permanente desses dados.
- **Excluir eventos financeiros junto com os dados pessoais:** descartado porque poderia comprometer a integridade do histórico e impedir auditoria e recálculo.

## Consequências

**Positivas:** permite reconstrução do estado financeiro; facilita auditoria e recálculo; preserva o histórico das operações; e separa os dados pessoais do histórico financeiro permanente.

**Negativas:** exige versionamento de eventos, manutenção de projeções, tratamento de reprocessamento e maior controle sobre a separação entre identificadores e dados pessoais.

## Validação por Spike

A viabilidade desta decisão será validada por um código de prova de conceito que deverá demonstrar:

1. registro de eventos financeiros sem armazenar dados pessoais diretamente no histórico;
2. reconstrução do estado financeiro a partir dos eventos;
3. geração de uma projeção utilizada pela Conciliação;
4. remoção dos dados pessoais associados ao identificador;
5. reconstrução do estado financeiro após essa remoção;
6. reprocessamento dos eventos sem duplicar o resultado financeiro.

A decisão será considerada viável se a remoção dos dados pessoais não impedir a reconstrução do histórico financeiro nem alterar o resultado da Conciliação.