# Mapa de Restrições e Decisões

## Caso Ônibus --- Envelope E: Fiscalização e LGPD

Este mapa relaciona as principais restrições do caso e do Envelope E às
decisões arquiteturais adotadas. As decisões mantêm coerência com a
matriz de estilos entregue na Entrega 1 e deverão ser vinculadas aos
ADRs e aos diagramas C4 correspondentes quando esses artefatos forem
consolidados pelo grupo.

  --------------------------------------------------------------------------------
  ID                Restrição /        Impacto na          Decisão arquitetural
                    requisito          arquitetura         
  ----------------- ------------------ ------------------- -----------------------
  **R01**           A validação        O funcionamento do  Manter a regra de
                    embarcada deve     validador não pode  validação e os dados
                    funcionar mesmo    depender de         mínimos necessários
                    sem conexão, com   comunicação         localmente no
                    decisão local e    síncrona com a      equipamento embarcado,
                    imediata.          nuvem.              utilizando arquitetura
                                                           Hexagonal para isolar a
                                                           regra de negócio da
                                                           infraestrutura. A
                                                           sincronização com os
                                                           sistemas centrais
                                                           ocorre posteriormente
                                                           por eventos.

  **R02**           Os ônibus podem    Validações e outras Utilizar Arquitetura
                    permanecer sem     operações           Orientada a Eventos,
                    conexão por        produzidas durante  mantendo os eventos
                    períodos           a desconexão não    localmente até que
                    prolongados.       podem ser perdidas. possam ser
                                                           sincronizados. O
                                                           processamento central é
                                                           desacoplado da operação
                                                           imediata do equipamento
                                                           embarcado.

  **R03**           Uma mesma viagem   O processamento     Adotar identificação
                    não pode ser       posterior e         única das operações e
                    aceita duas vezes. eventuais reenvios  processamento
                                       não podem gerar     idempotente, permitindo
                                       duplicidade.        reconhecer eventos já
                                                           processados durante
                                                           sincronizações e
                                                           reenvios.

  **R04**           Recargas e saldo   As operações        Isolar Cartões e
                    dos cartões exigem monetárias precisam Recarga como capacidade
                    consistência e não preservar           com regras
                    podem permitir     integridade mesmo   transacionais próprias,
                    aplicação          diante de falhas,   aplicando idempotência
                    duplicada de       repetição de        nas recargas e mantendo
                    crédito.           mensagens ou        o registro das
                                       indisponibilidade   operações necessárias à
                                       temporária.         reconstrução
                                                           financeira.

  **R05**           A telemetria da    A ingestão não pode Processar telemetria de
                    frota produz fluxo bloquear produtores forma orientada a
                    contínuo de        nem obrigar outros  eventos, com
                    posições e pode    subdomínios a       consumidores
                    apresentar picos.  escalar junto com a independentes e
                                       telemetria.         escaláveis. Serverless
                                                           não será a base da
                                                           ingestão principal,
                                                           pois a carga é
                                                           contínua, conforme
                                                           decisão da matriz
                                                           entregue.

  **R06**           O sistema de       Não é necessário    Utilizar CQRS,
                    informação ao      consultar           construindo modelos de
                    passageiro possui  diretamente os      leitura próprios a
                    grande volume de   modelos             partir da telemetria
                    consultas e tolera transacionais a     para consultas de
                    alguns segundos de cada requisição.    previsão de chegada,
                    atraso.                                mapa e informações ao
                                                           passageiro.

  **R07**           O fechamento       Não basta armazenar Utilizar Event Sourcing
                    financeiro mensal  apenas o estado     de forma localizada em
                    deve poder ser     financeiro atual;   Cartões/Recarga e
                    recalculado        fatos e versões das Conciliação,
                    utilizando as      regras relevantes   preservando os eventos
                    regras que estavam precisam permitir   financeiros
                    vigentes na data   reconstrução.       necessários, juntamente
                    de cada viagem.                        com versionamento
                                                           temporal das regras
                                                           tarifárias.

  **R08**           A conciliação e o  Uma alteração ou    Estruturar a
                    fechamento         correção não deve   conciliação com Pipes
                    financeiro         exigir              and Filters, separando
                    envolvem várias    reimplementar todo  recuperação das
                    etapas e precisam  o processo de       viagens, validação,
                    permitir           fechamento.         seleção das regras
                    reprocessamento.                       vigentes, cálculo e
                                                           consolidação em etapas
                                                           independentes e
                                                           reexecutáveis.

  **R09**           O Tribunal de      A arquitetura       Manter trilha de
                    Contas pode        precisa fornecer    auditoria e histórico
                    auditar os         evidências de como  reconstruível das
                    repasses           determinado         operações financeiras,
                    financeiros e o    resultado           registrando fatos,
                    Envelope E exige   financeiro foi      regras/versionamentos
                    que as operações   produzido.          aplicados e resultados
                    relevantes sejam                       do processamento de
                    reconstruíveis.                        conciliação. Event
                                                           Sourcing é utilizado
                                                           apenas nos subdomínios
                                                           em que essa
                                                           reconstrução justifica
                                                           sua complexidade.

  **R10**           O histórico        Uma trilha de       Separar dados pessoais
                    identificado de    auditoria           identificáveis dos
                    passageiros é dado permanente não pode eventos financeiros
                    pessoal e está     tornar impossível   necessários à
                    sujeito à LGPD e   eliminar dados      auditoria. O Event
                    ao direito de      pessoais quando     Sourcing não será
                    exclusão.          aplicável.          aplicado
                                                           indiscriminadamente ao
                                                           histórico pessoal; sua
                                                           utilização fica
                                                           restrita aos fatos
                                                           necessários à
                                                           reconstrução
                                                           financeira.

  **R11**           Existem            Alterações externas Utilizar Ports and
                    integrações com    não devem           Adapters nas fronteiras
                    banco, adquirente, contaminar          de integração e SOA/ESB
                    operadoras e       diretamente as      apenas de forma
                    outros sistemas    regras centrais do  localizada quando
                    que possuem        sistema.            necessário para
                    contratos e                            mediação dos sistemas
                    formatos próprios.                     heterogêneos, sem
                                                           transformar o
                                                           barramento no núcleo da
                                                           arquitetura.

  **R12**           Os subdomínios     Uma única unidade   Utilizar serviços
                    possuem            de implantação      independentes somente
                    necessidades       faria capacidades   para as capacidades que
                    diferentes de      de características  realmente necessitam de
                    carga,             muito diferentes    escala, isolamento ou
                    disponibilidade e  escalarem e         implantação própria,
                    evolução.          falharem juntas.    evitando uma
                                                           decomposição excessiva
                                                           em microsserviços.

  **R13**           A equipe possui    Uma arquitetura     Adotar uma arquitetura
                    apenas 15          excessivamente      híbrida e com
                    desenvolvedores e  distribuída         granularidade
                    1 pessoa           aumentaria o custo  controlada:
                    responsável por    operacional, de     microsserviços apenas
                    compliance.        testes e de         onde houver
                                       observabilidade     justificativa concreta;
                                       para uma equipe     Monolito Modular pode
                                       relativamente       ser usado em
                                       pequena.            capacidades coesas e de
                                                           menor volume, como
                                                           Atendimento.

  **R14**           A solução será     Serviços            Centralizar logs,
                    executada em nuvem distribuídos,       métricas, rastreamento
                    pública e precisa  eventos e           e registros de
                    permitir           integrações         auditoria, com
                    fiscalização e     precisam ser        identificação
                    operação           observáveis para    correlacionável das
                    controlada.        que falhas e        operações entre os
                                       operações possam    serviços e fluxos
                                       ser rastreadas.     assíncronos.

  **R15**           O fechamento       O processamento     Não adotar Arquitetura
                    mensal precisa     financeiro precisa  Celular, pois a
                    consolidar         realizar consultas  separação em células
                    informações de     e consolidações     dificultaria o
                    diferentes         globais.            processamento
                    operadores e                           transversal necessário
                    validações.                            à conciliação. Manter a
                                                           consolidação financeira
                                                           em um fluxo próprio de
                                                           Conciliação.
  --------------------------------------------------------------------------------

## Referências aos demais artefatos da Entrega 2

As decisões acima deverão ser associadas aos ADRs e aos diagramas C4
correspondentes após a consolidação desses artefatos pelo grupo. Nesta
etapa, os identificadores ainda não foram preenchidos para evitar
referências a ADRs ou componentes que possam receber outra numeração ou
nomenclatura na versão final.

A versão final do mapa pode acrescentar uma coluna **Referência**,
contendo, por exemplo, `ADR-01 / C4 Containers` ou
`ADR-03 / Componente de Conciliação`, conforme os artefatos efetivamente
produzidos pelo grupo.
