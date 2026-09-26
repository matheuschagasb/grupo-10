### 1. Como o validador aceita passagem sem rede e detecta duplicidade depois?

O validador embarcado utiliza internamente a Arquitetura Hexagonal para isolar as regras de negócio dos mecanismos de hardware e comunicação, permitindo que a decisão de aceitar ou recusar uma passagem ocorra localmente em até 300 ms, mesmo durante falhas de conectividade de até quatro horas[cite: 6, 9]. 

Para que a operação decorra sem rede, a arquitetura delega ao subdomínio de Validação Embarcada a manutenção de uma cópia local dos dados (uma visão necessária à operação *offline*, e não a fonte central de verdade)[cite: 8]. A detecção de duplicidade e a conciliação ocorrem posteriormente:
* Quando a conectividade é restabelecida, uma Arquitetura Orientada a Eventos entra em ação[cite: 9].
* Os registros locais são enviados de forma assíncrona para o *backend*[cite: 8].
* O *backend* processa o fluxo de eventos, sendo responsável por tratar a duplicação, ordenação e eventuais falhas de entrega resultantes desta sincronização atrasada[cite: 8].

**Sustentação:** ADR 0001[cite: 9], ADR 0002[cite: 8], ADR 0004[cite: 6] e Diagrama de Contêineres[cite: 11].

---

### 2. Como manter a consistência do saldo do cartão entre a aplicação e o ônibus com atraso de sincronização?

A consistência do saldo é assegurada através de uma estratégia distribuída de propriedade de dados combinada com mecanismos de consistência forte e eventual[cite: 8].

* O subdomínio "Cartões e recarga" é o único proprietário dos dados de saldo e aplica consistência forte internamente, garantindo as invariantes financeiras[cite: 8]. 
* Como o validador no ônibus opera *offline*, a comunicação com este e com os restantes subdomínios utiliza consistência eventual através da publicação de eventos[cite: 8].
* Quando o passageiro utiliza o cartão no ônibus, o validador registra a operação localmente[cite: 8]. Assim que existe rede, a operação é propagada via eventos para o subdomínio central de Cartões e Recarga, que recalcula e consolida o saldo de forma assíncrona, tolerando defasagens temporárias entre as visualizações na aplicação móvel e as transações reais não sincronizadas da frota[cite: 8].

**Sustentação:** ADR 0002[cite: 8] e Diagrama de Contexto[cite: 10].

---

### 3. Como a telemetria escala no pico sem derrubar o resto do sistema?

A telemetria foi desenhada como uma unidade de implantação independente, permitindo a sua escalabilidade isolada para absorver picos de até cinco vezes a carga normal, sem afetar subdomínios críticos como a validação ou as recargas[cite: 6]. 

O fluxo é gerido pela combinação de Arquitetura Orientada a Eventos e CQRS (*Command Query Responsibility Segregation*):
* A ingestão do fluxo contínuo de posições é totalmente desacoplada do processamento posterior através da emissão de eventos, impedindo que consumidores lentos ou indisponíveis bloqueiem a recepção de dados[cite: 6, 9].
* O subdomínio de Informação ao Passageiro utiliza o lado de leitura (*Query*) do CQRS, consumindo modelos de leitura derivados da telemetria[cite: 9].
* Isto garante que o aumento massivo de consultas na aplicação pelos passageiros não incida sobre o armazenamento transacional da telemetria, mantendo a estabilidade global do sistema[cite: 8, 9].

**Sustentação:** ADR 0001[cite: 9], ADR 0004[cite: 6] e Diagrama de Contêineres[cite: 11].

---

### 4. Como recalcular o repasse mensal se a regra de divisão mudar no meio do mês?

O subdomínio de Conciliação combina Arquitetura Hexagonal com o padrão *Pipes and Filters* para processar o fechamento financeiro[cite: 9]. 

* O processamento ocorre numa sequência de etapas isoladas (filtros): recuperação de eventos de viagem, validação de dados, seleção das regras vigentes, cálculo de valores e consolidação final[cite: 9].
* O sistema mantém o histórico das operações financeiras preservado de modo a permitir o recálculo[cite: 8].
* Quando uma regra tarifária é alterada retroativamente no meio do mês, o sistema não necessita de alterar a lógica de domínio transversal; basta reexecutar o *pipeline* de conciliação[cite: 9]. O filtro responsável pela "seleção de regras vigentes" aplicará automaticamente a regra correta baseada na data de cada fato histórico preservado, gerando um novo fechamento consolidado sem impactar as validações diárias[cite: 8, 9].

**Sustentação:** ADR 0001[cite: 9], ADR 0002[cite: 8] e Diagrama de Componentes[cite: 12].

---

### 5. (Envelope E) Como guardar tudo para sempre para o Tribunal de Contas, e ainda assim apagar o que a LGPD manda apagar?

O conflito arquitetural entre a auditoria rigorosa do Tribunal de Contas e o direito ao esquecimento exigido pela LGPD é resolvido limitando rigorosamente o padrão *Event Sourcing* apenas ao histórico financeiro e segregando os dados pessoais[cite: 5].

* O sistema armazena todos os eventos financeiros (Cartões/Recargas e Conciliação) de forma imutável (*append-only*), garantindo que o estado financeiro pode sempre ser reconstruído e fiscalizado sem que operações passadas sejam apagadas[cite: 5].
* Para cumprir a legislação de privacidade, os **dados pessoais identificáveis nunca são armazenados diretamente nestes eventos financeiros**[cite: 5, 8].
* Os eventos imutáveis contêm apenas identificadores de referência (pseudonimização)[cite: 5]. Os dados pessoais reais são mantidos fora do fluxo de *Event Sourcing*, num ciclo de vida próprio[cite: 5]. 
* Quando ocorre um pedido de esquecimento ao abrigo da LGPD, o sistema elimina os dados pessoais identificáveis da sua base segregada[cite: 5]. O identificador no *Event Store* imutável permanece, mantendo a integridade da auditoria e dos totais arrecadados, mas a identidade do passageiro torna-se irremediavelmente inacessível[cite: 5, 8].

**Sustentação:** ADR 0005[cite: 5] e ADR 0002[cite: 8].