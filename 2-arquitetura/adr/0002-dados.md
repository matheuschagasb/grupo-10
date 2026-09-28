# ADR 0002: atribuir cada dado a um único subdomínio dono

**Status:** aceito

**Contexto:** Saldo e recarga exigem consistência forte, a validação embarcada decide sem rede, a telemetria chega continuamente e a conciliação precisa de histórico para recalcular. Uma base compartilhada acoplaria todos os subdomínios. O Envelope E exige que o histórico financeiro não dependa de dados pessoais permanentes.

**Decisão:** Cada dado tem um único subdomínio escritor, acessado pelos demais só por interface publicada ou evento, com consistência forte apenas em saldo, recarga e fechamento. Cartões e Recarga é dono de cartões, saldo, recargas, perfil de gratuidade, sincronização das validações e Cadastro de Passageiros (dados pessoais); a Conciliação, das regras tarifárias versionadas e dos fechamentos; Telemetria, Informação ao Passageiro e Atendimento, dos seus próprios dados.

**Alternativas consideradas:**
- Banco único compartilhado: descartado por acoplar os subdomínios.
- Consistência forte global: descartada por exigir conexão contínua, inviável no ônibus.
- Consistência eventual em tudo: descartada porque saldo e fechamento têm invariantes financeiras.
- Cadastro de Passageiros dentro do Atendimento: descartado porque o Atendimento é de baixo volume e não é dono do cartão a que o cadastro se liga.

**Consequências:**
- Positivas: menor acoplamento; consistência forte só onde há dinheiro; consultas de passageiros não competem com dados transacionais; o dado pessoal tem dono único e ciclo de retenção próprio.
- Negativas: o mesmo fato tem representações diferentes; sincronizações têm atraso; Cartões e Recarga concentra várias responsabilidades e pode virar gargalo de evolução.

**Fontes:** ABREU (2026): §9.2 (banco por serviço), §11.2 (consistência eventual e idempotência), §14.2 (modelo de leitura). Premissas de dimensionamento e requisitos do caso Ônibus (enunciado "Um problema, cinco realidades"); Envelope E.
