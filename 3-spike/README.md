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

É necessário apenas Python 3.

No diretório `3-spike`, execute:

```bash
python exemplo.py