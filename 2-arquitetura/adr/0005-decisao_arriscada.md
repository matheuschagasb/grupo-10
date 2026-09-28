# ADR 0005: separar dados pessoais dos eventos financeiros por referência opaca

**Status:** aceito

**Contexto:** O Tribunal de Contas audita o repasse e exige reconstruí-lo a partir de fatos imutáveis. A LGPD dá ao titular o direito de pedir a eliminação de dados pessoais, ressalvadas as hipóteses de conservação previstas na própria lei. Um armazenamento imutável não apaga registros sem quebrar a integridade do fluxo, e Event Sourcing tem custo alto de versionamento e reprocessamento.

**Decisão:** Usar Event Sourcing só em Cartões e Recarga e na Conciliação, com eventos que guardam apenas uma referência opaca ao passageiro (identificador aleatório, sem CPF nem hash de CPF) e dados pessoais no Cadastro de Passageiros. A eliminação apaga o cadastro, o vínculo e as cópias em Banco de Cartões, Modelo de Leitura e registro do Atendimento, sem tocar nos eventos, e correções entram como eventos de compensação.

**Alternativas consideradas:**
- Crypto-shredding (chave por titular): descartado por acrescentar cifra em toda leitura e gestão de chaves para uma equipe pequena; volta a ser candidato se a auditoria exigir dado pessoal dentro do evento.
- Apagar o evento junto com o dado pessoal: descartado porque a soma do repasse deixa de bater na auditoria.
- Dado pessoal dentro do evento: descartado porque prende a auditoria à retenção permanente desse dado.
- Event Sourcing em todo o sistema: descartado por custo sem benefício e por conflito com a eliminação.

**Consequências:**
- Positivas: o repasse continua reconstruível após a eliminação; a eliminação é local e automatizável; o cadastro tem ciclo de retenção próprio.
- Negativas: a referência continua ligando as viagens entre si, e o cruzamento de trajetos pode reidentificar a pessoa, risco residual a validar com a responsável por conformidade; cópias de segurança precisam de prazo de expiração definido; exige versionamento de eventos e de regras tarifárias.

**Validação:** provado por `3-spike/exemplo.py` (registro, eliminação, reconstrução e reprocessamento sem duplicar). O spike cobre apenas Event Store e cadastro, não as cópias nem os backups.

**Fontes:** ABREU (2026): §15.7 (custo real; dados pessoais e crypto-shredding). BRASIL. Lei nº 13.709/2018 (LGPD). Requisitos do Envelope E (enunciado).
