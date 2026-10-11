# Responsabilidades, metas e recuperação

Valores abaixo são premissas propostas pelo grupo, não medições ou SLA de fornecedor.

| Time | Desenvolvedores | Unidades e responsabilidade |
|---|---:|---|
| Financeiro | 4 | Cartões e Recarga; contrato financeiro e sincronização |
| Frota | 3 | Telemetria e validador embarcado; contrato GPS e firmware |
| Passageiro | 2 | Informação ao Passageiro; modelos de leitura |
| Repasse | 2 | Conciliação; regras e fechamento |
| Integração | 2 | Adaptadores externos e contratos de liquidação |
| Plataforma e Atendimento | 2 | Atendimento, gateway, brokers, backups e automação |
| Conformidade | 1 responsável, fora dos 15 | Revisar retenção, acesso e exceções; não substituir equipe de incidentes |

Cada time mantém responsável primário e substituto para incidentes das suas unidades e versiona seu contrato; Plataforma coordena incidentes compartilhados. Atendimento recebe apoio do Financeiro. A distribuição não comprova cobertura presencial 24×7; escala de plantão e suporte do provedor são pendências de produção.

Estimativa inicial: seis pipelines backend × 2 h/semana = 12 h; embarcado = 4 h; infraestrutura, backup e ensaios = 8 h; revisão de contratos/incidentes = 6 h. Total reservado: 30 h/semana (5% de 15 × 40 h). Não inclui construção inicial nem picos de incidente. Revisar mensalmente por 8 semanas; acima de 60 h/semana por dois ciclos, reavaliar fronteiras e capacidade por novo ADR. É orçamento estimado, não prova de operação sustentável.

| Fluxo | Meta proposta | RTO | RPO |
|---|---|---|---|
| Validação | 99,9% de respostas em até 300 ms em hardware homologado, inclusive offline até 4 h, salvo limite de risco | 30 min para substituir equipamento defeituoso | Zero para recibos confirmados persistidos; perda física antes de sincronizar é risco residual |
| Recarga backend | 99,9% mensal; crédito até 1 min após confirmação recebida, excluída espera externa | 1 h | Zero para crédito confirmado em armazenamento replicado |
| Telemetria | Sustentar 400 posições/s; projeção p95 até 15 s | 1 h | Zero após confirmação de persistência; fila embarcada antes disso |
| Fechamento | Concluir até 24 h após corte mensal | 4 h | Até 15 min de projeção; fatos confirmados preservados |
| Event Stores e log oficial | 99,9% mensal para escrita; publicação de evidência acompanhada por sequência | 4 h | Zero para escrita confirmada replicada; desastre regional pode perder até 15 min ainda não exportados |

RPO zero pressupõe confirmação após replicação síncrona em zonas distintas; não se afirma zero para desastre de toda a região. Em região alternativa, recuperar exportações e reconciliar recibos antes de confirmar saldos ou fechamento.

## Procedimentos de recuperação

- **Event Stores/log:** suspender crédito e fechamento; restaurar cópia em isolamento; validar manifesto, hash, sequência e divergências; recuperar outbox/inbox e deduplicar; reaplicar eliminações; recalcular totais e liberar após revisão de dois responsáveis.
- **Brokers:** recuperar filas persistentes; reiniciar consumidores por checkpoint; republicar outbox sem novo efeito; telemetria permanece separada do financeiro. Alarmar profundidade/idade e capacidade de disco antes de esgotar buffer.
- **Projeções:** reconstruir a partir da fonte dona; bloquear consultas pessoais até reaplicar eliminações e validar ausência de vínculos removidos.
- **Embarcado:** recuperar diário, resolver commits incertos pelo estado do cartão; sincronizar recibos e bloqueios; não liberar a catraca por uma mensagem apenas recebida na rede.

Ensaiar recuperação trimestralmente e registrar resultado. Nenhuma dessas metas foi validada pelo spike em memória.
