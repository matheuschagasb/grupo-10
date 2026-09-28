# ADR 0001: compor estilos por capacidade, com fronteira explícita entre cada par

**Status:** aceito

**Contexto:** O sistema tem capacidades com perfis muito diferentes: validação embarcada (300 ms, até 4 h sem rede), telemetria (80 posições/s, pico de 400/s), cartões e recarga (saldo e dinheiro), conciliação (auditável e recalculável), informação ao passageiro (pico de leitura no rush), atendimento (baixo volume) e integrações com terceiros. A equipe tem 15 desenvolvedores e 1 responsável por conformidade, em nuvem pública. O Tribunal de Contas exige reconstruir o repasse e a LGPD exige eliminar dados pessoais.

**Decisão:** Adotar arquitetura híbrida, com Microsserviços apenas em Cartões e Recarga, Telemetria, Informação ao Passageiro, Conciliação e Integração Externa, e Monolito Modular no Atendimento. Entre unidades a comunicação padrão é por evento, com chamada só quando a resposta imediata é necessária, e nenhuma unidade acessa o banco de outra.

**Fronteiras entre estilos:**
- Hexagonal ↔ Event-Driven (Validador): o hexágono termina na porta de sincronização e o broker começa depois dela; aceitar ou recusar a passagem nunca cruza essa fronteira (ADR 0008).
- Hexagonal ↔ Pipes and Filters (Conciliação): o hexágono guarda regras e portas; o pipeline é o adaptador que executa o fechamento, e só a porta de liquidação sai dele (ADR 0003).
- Event Sourcing ↔ estado atual: Event Sourcing só em Cartões e Recarga e na Conciliação (ADR 0005).
- Event-Driven ↔ CQRS (Telemetria): a escrita termina no evento de posição; a leitura começa no consumidor que projeta o modelo (ADR 0007).
- Monolito Modular ↔ resto: o Atendimento só fala por interface publicada ou evento (ADR 0006).
- Hexagonal ↔ terceiros: contratos externos ficam no adaptador (ADR 0003).

**Alternativas consideradas:**
- Monolito em Camadas: descartado porque cargas diferentes seriam implantadas e escaladas juntas.
- Monolito Modular único: descartado por não escalar Telemetria e Informação ao Passageiro separadamente.
- Microsserviços em todos os subdomínios: descartado pelo custo operacional para 15 desenvolvedores.
- Event-Driven em tudo: descartado porque a validação precisa ser local e imediata.
- Arquitetura Celular: descartada porque células isoladas dificultam o fechamento, que consolida todas as operadoras.
- Serverless: descartado porque a telemetria é fluxo contínuo e previsível, sem ociosidade que justifique cobrança por invocação, e a validação roda no ônibus.

**Consequências:**
- Positivas: cada capacidade usa o estilo do seu perfil; só cinco unidades escalam de forma independente; cada fronteira pode ser revista sem reescrever as demais.
- Negativas: a equipe precisa dominar vários estilos; eventos trazem consistência eventual e exigem idempotência; cinco unidades independentes elevam o custo operacional; as fronteiras precisam ser vigiadas a cada evolução.

**Fontes:** ABREU (2026), Estilos Arquiteturais de Software: §4.6 (ADR em arquiteturas híbridas), §9.6 e §9.7 (Microsserviços), §12.6 (Serverless), §13.6 (Celular). Premissas de dimensionamento e requisitos do caso Ônibus (enunciado "Um problema, cinco realidades").
