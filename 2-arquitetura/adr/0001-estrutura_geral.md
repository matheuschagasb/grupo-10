# ADR 0001: adotar arquitetura híbrida orientada por capacidades

**Status:** aceito

**Contexto:**  
O sistema de transporte coletivo reúne subdomínios com características distintas de carga, disponibilidade e evolução. A validação embarcada deve continuar funcionando durante períodos sem conectividade; cartões e recargas precisam sincronizar operações realizadas em momentos distintos; a telemetria recebe um fluxo contínuo de posições da frota e deve absorver picos de carga; a informação ao passageiro depende desses dados para consultas; a conciliação precisa processar e recalcular o fechamento financeiro; e a integração externa depende de sistemas de terceiros.

Essas características impedem que todos os subdomínios sejam tratados da mesma forma. Ao mesmo tempo, a equipe de 15 desenvolvedores limita a quantidade de unidades independentes que podem ser operadas sem aumentar excessivamente a complexidade.

O Envelope E acrescenta a necessidade de fiscalização e tratamento dos dados pessoais conforme a LGPD, tornando importantes a rastreabilidade e a separação das responsabilidades.

**Decisão:**  
Adotar uma arquitetura híbrida orientada por capacidades, aplicando estilos arquiteturais diferentes apenas onde as características de cada subdomínio justificarem seu uso. Cada composição terá fronteiras explícitas, de modo que seja possível identificar onde um estilo termina e outro começa.

As capacidades e suas fronteiras serão definidas da seguinte forma:

- **Atendimento — Monolito Modular:** o Atendimento permanecerá em uma única unidade de implantação, dividido internamente em módulos com responsabilidades explícitas. Essa fronteira termina nas interfaces disponibilizadas pelo Atendimento para comunicação com outras capacidades. O Monolito Modular é utilizado porque essa capacidade não apresenta necessidade suficiente de escala ou disponibilidade independente que justifique o custo de distribuí-la.

- **Validação embarcada — Arquitetura Hexagonal + Arquitetura Orientada a Eventos:** a Arquitetura Hexagonal organiza internamente a aplicação de validação e isola as regras de negócio dos mecanismos de persistência, comunicação e hardware do validador. Sua fronteira termina nas portas de entrada e saída. A partir das portas responsáveis pela comunicação com o backend, começa a Arquitetura Orientada a Eventos, utilizada para sincronizar posteriormente as operações realizadas no ônibus. A decisão de aceitar ou recusar uma passagem permanece dentro da aplicação embarcada e não depende do processamento de eventos, pois precisa ocorrer localmente e continuar disponível sem conectividade.

- **Cartões e recarga — Unidade independente + Arquitetura Orientada a Eventos:** Cartões e Recarga constituem uma fronteira própria quando houver necessidade de escala e disponibilidade independentes. Internamente ficam as operações relativas a cartões, saldos e recargas. Essa fronteira termina nas interfaces e eventos publicados pela capacidade. A Arquitetura Orientada a Eventos começa na propagação das alterações que precisam ser conhecidas por outras capacidades, permitindo sincronização sem exigir comunicação síncrona para todos os fluxos.

- **Telemetria da frota — Arquitetura Orientada a Eventos + CQRS:** a Arquitetura Orientada a Eventos cobre a recepção e a propagação assíncrona das posições da frota, permitindo absorver o fluxo contínuo e seus picos. Sua responsabilidade termina após a disponibilização dos dados necessários aos consumidores. O CQRS começa na separação entre esse fluxo de escrita/processamento e os modelos destinados às consultas. Essa separação é utilizada porque a ingestão da telemetria e as consultas de posição possuem características diferentes de carga e podem evoluir e escalar separadamente.

- **Informação ao passageiro — CQRS:** a capacidade de Informação ao Passageiro utiliza o lado de leitura da composição com CQRS. Sua fronteira começa nos modelos de leitura derivados da telemetria e termina nas interfaces disponibilizadas para consulta pelos passageiros. Ela não acessa diretamente o armazenamento interno da Telemetria. Essa separação permite otimizar as consultas sem acoplar sua carga ao fluxo de ingestão das posições.

- **Conciliação — Arquitetura Hexagonal + Pipes and Filters:** a Arquitetura Hexagonal delimita as regras financeiras e de conciliação, separando-as da infraestrutura, persistência e integrações externas. Dentro dessa fronteira, Pipes and Filters começa no processamento do fechamento e organiza suas etapas de recuperação das viagens, validação dos dados, seleção das regras vigentes, cálculo dos valores e consolidação dos resultados. Pipes and Filters termina após a produção do resultado consolidado. Essa composição permite testar e reexecutar etapas do fechamento sem misturar a lógica financeira com mecanismos de infraestrutura.

- **Integração externa — Arquitetura Hexagonal:** a fronteira de Integração Externa começa nas portas utilizadas pelo domínio para solicitar operações externas e termina nos adaptadores que se comunicam com banco, adquirente, operadoras e demais terceiros. Contratos, protocolos e formatos pertencentes aos terceiros ficam restritos a esses adaptadores e não atravessam a fronteira para o domínio. Essa separação permite substituir ou alterar integrações externas sem propagar seus detalhes para as regras internas.

Entre capacidades implantadas independentemente, cada fronteira termina em sua interface publicada. Nenhuma capacidade deverá acessar diretamente a implementação interna ou o armazenamento pertencente a outra.

Como regra geral de comunicação, operações que exigem resposta imediata utilizam chamadas síncronas apenas quando necessário. A propagação de fatos entre capacidades que não exige resposta imediata utiliza eventos. Dessa forma, a comunicação orientada a eventos começa após a fronteira interna da capacidade produtora e termina na entrada do consumidor responsável pelo processamento daquele evento.

A composição dos estilos pode ser resumida pelas seguintes fronteiras:

`Atendimento [Monolito Modular]`

`Validação [Hexagonal] → eventos → [Backend]`

`Cartões/Recarga [Capacidade independente] → eventos → [Consumidores]`

`Telemetria [Eventos / escrita] → [CQRS / modelos de leitura] → Informação ao Passageiro`

`Conciliação [Hexagonal [Pipes and Filters]]`

`Domínio [Portas] → [Adaptadores] → Sistemas externos`

Decisões específicas sobre propriedade e consistência dos dados, integração com terceiros, operação e implantação e tratamento da decisão de maior risco são detalhadas nos ADRs seguintes.

**Alternativas consideradas:**

- **Adotar um Monolito em Camadas para todo o sistema:** descartada porque os subdomínios possuem perfis distintos de carga, disponibilidade e evolução. Uma única unidade obrigaria capacidades com necessidades diferentes a serem implantadas e escaladas em conjunto.

- **Adotar um Monolito Modular para todo o sistema:** descartada porque, embora forneça fronteiras internas com menor custo operacional, manteria uma única unidade de implantação e impediria escala e disponibilidade independentes das capacidades que apresentam necessidades distintas, especialmente Telemetria e Cartões/Recarga.

- **Adotar Microsserviços para todos os subdomínios:** descartada porque aumentaria a quantidade de serviços, contratos distribuídos e componentes operacionais sem que todos os subdomínios apresentem necessidade de implantação ou escala independente. Esse custo seria especialmente relevante para uma equipe de 15 desenvolvedores.

- **Adotar Arquitetura Orientada a Eventos para todas as interações:** descartada porque nem todas as operações podem depender de processamento assíncrono. A decisão de aceitar ou recusar uma passagem, por exemplo, precisa ser local e imediata, inclusive durante períodos sem conectividade.

**Consequências:**

- **Positivas:** cada capacidade utiliza o estilo adequado às suas características; as fronteiras entre os estilos ficam explicitamente definidas; Telemetria e Cartões/Recarga podem possuir independência operacional quando necessário; eventos reduzem o acoplamento temporal nas operações assíncronas; a Arquitetura Hexagonal mantém regras críticas isoladas da infraestrutura e das integrações externas; CQRS permite separar o fluxo de ingestão das consultas ao passageiro; Pipes and Filters permite decompor e reexecutar as etapas da conciliação; e as responsabilidades explícitas facilitam a rastreabilidade necessária à fiscalização.

- **Negativas:** a combinação de estilos aumenta a complexidade arquitetural e exige conhecimento de diferentes modelos de comunicação; as fronteiras precisam ser preservadas durante a evolução do sistema para evitar acoplamento indevido; eventos introduzem consistência eventual e exigem tratamento de falhas de publicação e consumo; unidades independentes aumentam o custo operacional; CQRS exige manter modelos distintos de escrita e leitura; e Pipes and Filters adiciona etapas e mecanismos adicionais ao processamento da conciliação.