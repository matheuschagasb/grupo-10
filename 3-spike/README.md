# Spike: separação entre dados pessoais e histórico financeiro auditável

**ADR validado:** `2-arquitetura/adr/0005-decisao_arriscada.md`

## Objetivo

Este spike valida a decisão de manter os fatos financeiros necessários à auditoria em um histórico imutável, enquanto os dados pessoais identificáveis permanecem em armazenamento separado.

O objetivo é demonstrar que a remoção dos dados pessoais não impede a reconstrução do estado financeiro nem altera o resultado utilizado pela Conciliação.

## O que o código demonstra

O código implementa:

- um armazenamento separado para dados pessoais;
- um Event Store financeiro append-only;
- eventos financeiros que armazenam apenas uma referência ao usuário;
- reconstrução de uma projeção de Conciliação a partir dos eventos;
- eliminação dos dados pessoais de um passageiro;
- nova reconstrução da projeção após a eliminação;
- processamento idempotente, evitando que o mesmo evento seja contabilizado duas vezes.

## Como executar

É necessário apenas Python 3.12, sem bibliotecas externas.

No diretório `3-spike`, execute:

```bash
python3 exemplo.py
```

A saída impressa no terminal deve ser idêntica ao conteúdo de `saida-esperada.txt`.

## O que aconteceria se a decisão estivesse errada

Se, em vez desta separação, o sistema tivesse optado por uma **exclusão física tradicional** (`DELETE`) do evento inteiro para atender a um pedido de esquecimento da LGPD, o evento da viagem desapareceria do histórico financeiro. Ao recalcular o repasse mensal, ou durante uma auditoria do Tribunal de Contas, a soma das tarifas validadas não bateria mais com o valor total arrecadado — configurando um indício de inconsistência ou fraude e quebrando diretamente a exigência de reconstrução auditável do Envelope E.

Por outro lado, se o sistema optasse por **nunca apagar nenhum dado pessoal**, para preservar a auditoria financeira a qualquer custo, o consórcio ficaria exposto a sanções por descumprimento do direito ao esquecimento previsto na LGPD.

A separação entre identificador de referência (mantido no Event Store) e dado pessoal (mantido à parte, e elimináveis independentemente) é o que permite atender às duas exigências ao mesmo tempo, sem sacrificar nenhuma delas.
