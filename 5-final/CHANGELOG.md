# CHANGELOG — Entrega 5: versão final

## Revisão de 10/10/2026

Base: commit `7c38c29ac3636a7434d6d6e42ea67e2b0527e8fd` do Grupo 10. Motivação: oito objeções do Grupo 07 e respostas da Entrega 4b, preservadas em `4-leitura-cruzada/respostas-recebidas.md` como registro histórico.

| Objeção | O que mudou | Por quê | Artefatos |
|---|---|---|---|
| 1 — fonte de auditoria | Removida trilha central; fontes oficiais por dono, correlação e precedência | O diagrama mostrava alternativa rejeitada pelo ADR 0006 | C4 contêineres; adendo ADR 0006; mapa |
| 2 — pseudonimização tardia | Guarda de contrato é a primeira barreira do pipeline; evento minimizado na origem; rejeição sem copiar payload pessoal | Evitar identificação passando pela Conciliação antes da proteção | C4 componentes; contrato; adendo ADR 0005; spike |
| 3 — eliminação incompleta | Referência aleatória, vínculo separado, eliminação em cinco armazenamentos e verificação que detecta resíduo; política de backups e restauração | O spike anterior usava ID do cadastro e não cobria cópias nem vínculos | Spike, README, saída esperada; ADR 0009; resposta 5 |
| 4 — cartão offline | Tecnologia de referência, confiança, commit, recuperação e exposição a clones; corrigida a afirmação de que todo segundo uso é recusado | Saldo e contador sozinhos não provam prevenção criptográfica ou garantia global offline | Novo ADR 0011 substitui ADR 0008; resposta 1; mapa |
| 5 — telemetria | Broker persistente de telemetria separado do financeiro, com consumidor e store próprios | Um único broker contradizia o isolamento decidido | C4 contêineres; ADR 0007 mantido |
| 6 — observabilidade não é evidência | Separadas fontes oficiais e logs; retenção, proteção, acesso, horário e recuperação definidos como proposta | Correlação operacional não garante completude nem preservação | Adendo ADR 0004; ADR 0009; operação |
| 7 — integrações financeiras | Chave persistida por confirmação e unicidade por recarga; repetida sem efeito, divergente em exceção; inbox/outbox | Evitar crédito duplicado, inclusive com IDs de confirmação diferentes | Adendo ADR 0003; contrato |
| 8 — custo operacional | Removido serviço backend de validação; seis unidades de negócio, cinco microsserviços; gateway só infraestrutura; responsáveis, orçamento e metas | A contagem do C4 não coincidia com ADR e faltava responsabilidade operacional | Novo ADR 0010 substitui ADR 0001; C4; operação; mapa; README |

## Decisões e histórico

- ADR 0009: aceito; complementa retenção e restauração, sem alegar prazo legal obrigatório.
- ADR 0010: status **“substitui o ADR 0001”**; define a topologia vigente.
- ADR 0011: status **“substitui o ADR 0008”**; reformula a garantia offline e seus limites.
- ADRs 0001 e 0008 permanecem com nota histórica; suas decisões vigentes são as substitutas.
- ADRs 0003, 0004, 0005 e 0006 recebem adendos compatíveis, sem apagar o texto anterior. ADRs 0002 e 0007 mantidos.
- Diagramas PNG revisados têm fontes `.dot` editáveis; contexto permanece igual porque atores e escopo não mudaram.

## Validação e limites

Spike executado com sucesso: total R$ 13,50 e três viagens antes da eliminação, após reconstrução e após reprocessamento. Verificações negativas detectam resíduo pessoal e rejeitam evento com nome. Duas execuções produzem saída idêntica ao arquivo esperado. Código tem 156 linhas, usa biblioteca padrão e valores em centavos. Diagramas foram inspecionados e referências de arquivos conferidas.

Retenção, hardware, criptografia, metas de desempenho, disponibilidade e restauração em AWS são especificações propostas: não foram implantadas nem provadas pelo spike. Referência opaca não prova anonimização; clones com chaves comprometidas continuam risco. Não se afirma prevenção absoluta de fraude nem conservação permanente irrestrita.
