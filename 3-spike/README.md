# Spike: dado pessoal fora do histórico financeiro

**Prova o ADR 0005** (`2-arquitetura/adr/0005-decisao-arriscada.md`).

## O que prova

Os fatos financeiros ficam em um Event Store append-only que guarda só uma referência ao passageiro; nome e CPF ficam em um cadastro separado. Eliminar o cadastro de um passageiro não muda o total conciliado (R$ 13,50 em 3 viagens) nem impede reconstruir a projeção, e reprocessar os mesmos eventos não duplica o resultado.

## Como rodar

Python 3.12, somente com a biblioteca padrão, na pasta `3-spike`:

```bash
python exemplo.py
```

Em sistemas onde o comando do Python é `python3`:

```bash
python3 exemplo.py
```

A saída deve ser idêntica a `saida-esperada.txt` (quatro cenários: A processamento, B eliminação, C reconstrução, D idempotência).

## Se a decisão estivesse errada

Se o pedido de eliminação apagasse o evento inteiro, a soma das tarifas deixaria de bater na auditoria do Tribunal de Contas. Se o dado pessoal ficasse dentro do evento, a auditoria dependeria da retenção permanente desse dado, o que conflita com o pedido de eliminação, ressalvadas as hipóteses de conservação previstas na LGPD (ABREU, 2026, §15.7; Lei 13.709/2018).

## Limites

O spike simula só Event Store e cadastro em memória; não cobre cópias de segurança nem os outros armazenamentos citados no ADR.
