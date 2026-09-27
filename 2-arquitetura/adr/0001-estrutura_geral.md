# ADR 0001: adotar arquitetura híbrida orientada por capacidades

**Status:** aceito

## Contexto

O sistema possui capacidades com necessidades muito diferentes de carga, disponibilidade e evolução. A validação embarcada precisa operar offline, a telemetria recebe fluxo contínuo com picos, Cartões e Recarga possui operações financeiras e a Conciliação precisa permitir auditoria e recálculo.

Uma única arquitetura para todo o sistema aumentaria o acoplamento ou imporia complexidade desnecessária. A equipe possui 15 desenvolvedores, portanto a quantidade de unidades independentes também deve ser controlada.

O Envelope E exige rastreabilidade, fiscalização e tratamento adequado dos dados pessoais.

## Decisão

Adotar uma arquitetura híbrida orientada por capacidades, aplicando cada estilo apenas onde suas características forem necessárias.

| Capacidade | Estilo adotado | Fronteira / finalidade |
|---|---|---|
| **Atendimento** | Monolito Modular | Mantém seus módulos em uma única unidade de implantação, pois não exige escala independente. |
| **Validação Embarcada** | Hexagonal + Event-Driven | Hexagonal organiza a lógica local e isola hardware, armazenamento e comunicação. Eventos são utilizados apenas para sincronização com o backend. |
| **Cartões e Recarga** | Capacidade independente + Event-Driven | Mantém saldo e operações financeiras dentro de sua fronteira e publica alterações relevantes por eventos. |
| **Telemetria** | Event-Driven + CQRS | Eventos desacoplam ingestão e processamento; CQRS separa o fluxo de escrita dos modelos utilizados em consultas. |
| **Informação ao Passageiro** | CQRS | Utiliza modelos de leitura derivados da telemetria, sem acessar diretamente seu armazenamento interno. |
| **Conciliação** | Hexagonal + Pipes and Filters | Hexagonal isola as regras financeiras; Pipes and Filters organiza as etapas de recuperação, validação, cálculo e consolidação. |
| **Integrações Externas** | Hexagonal / Ports and Adapters | Contratos e formatos de terceiros permanecem nos adaptadores e não entram no domínio. |

Entre capacidades independentes, nenhuma poderá acessar diretamente o armazenamento ou a implementação interna de outra.

Chamadas síncronas serão utilizadas apenas quando houver necessidade de resposta imediata. A propagação de fatos que não exige resposta imediata utilizará eventos.

As decisões específicas sobre dados, integração, implantação e histórico financeiro são detalhadas nos ADRs 0002 a 0005.

## Alternativas consideradas

- **Monolito em Camadas para todo o sistema:** descartado porque obrigaria capacidades com perfis muito diferentes a escalar e evoluir juntas.
- **Monolito Modular para todo o sistema:** descartado porque não permitiria implantação e escala independentes onde elas são necessárias.
- **Microsserviços para todos os subdomínios:** descartado pelo aumento de complexidade operacional para uma equipe de 15 desenvolvedores.
- **Arquitetura Orientada a Eventos para todas as interações:** descartada porque algumas decisões, como a validação da passagem, precisam ser locais e imediatas.

## Consequências

**Positivas:** cada capacidade utiliza um estilo adequado às suas necessidades; Telemetria e Cartões/Recarga podem escalar de forma independente; eventos reduzem acoplamento temporal; Hexagonal protege as regras de negócio; CQRS otimiza as consultas; e Pipes and Filters facilita o reprocessamento da Conciliação.

**Negativas:** a combinação de estilos aumenta a complexidade arquitetural; eventos exigem tratamento de falhas e idempotência; unidades independentes aumentam o custo operacional; e as fronteiras precisam ser mantidas corretamente durante a evolução do sistema.