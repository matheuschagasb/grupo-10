# ADR 0006: registrar as alterações do Atendimento em log append-only próprio

**Status:** aceito

**Contexto:** O caso exige trilha de quem alterou o quê no Atendimento (gratuidade, segunda via, contestação, correção de cadastro), e o Envelope E exige que tudo seja reconstruível. O ADR 0005 limita Event Sourcing aos fatos financeiros. Uma trilha central de todo evento de negócio duplicaria o Event Store e guardaria referências pessoais de todos os subdomínios.

**Decisão:** O Atendimento grava cada alteração (quem, o quê, quando e referência opaca do passageiro, sem dados pessoais) em log append-only próprio e publica um evento de alteração, sem trilha central de todos os eventos. Pedidos de gratuidade e de eliminação vão por interface publicada de Cartões e Recarga, e a contestação do repasse aciona o reprocessamento da Conciliação.

**Alternativas consideradas:**
- Trilha central de todo evento de negócio: descartada por duplicar o Event Store e ferir o ADR 0005.
- Log de aplicação comum: descartado por ser alterável e sem garantia de completude.
- Atendimento escrevendo direto em Cartões e Recarga: descartado por quebrar a propriedade de dados do ADR 0002.

**Consequências:**
- Positivas: trilha completa onde a lei pede, com escopo pequeno; o log não tem dado pessoal do passageiro; a fronteira do monolito fica clara.
- Negativas: a identidade do atendente é dado pessoal do funcionário e exige retenção própria; reconstruir uma operação entre subdomínios junta dois registros, o log e o Event Store.

**Fontes:** ABREU (2026): §6.1 (interface pública do módulo), §15.7 (custo real). Premissas de dimensionamento e requisitos do caso Ônibus (enunciado "Um problema, cinco realidades"); Envelope E.
