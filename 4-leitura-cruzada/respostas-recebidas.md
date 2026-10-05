# Entrega 4b: Respostas às objeções recebidas

**Grupo autor:** Grupo 10 (Caso Ônibus, Envelope E: operação fiscalizada)
**Grupo revisor:** Grupo 07

Agradecemos ao Grupo 07 pela leitura cuidadosa. Conferimos cada objeção contra os ADRs, os três diagramas C4, o mapa de restrições e decisões, as respostas às perguntas obrigatórias e o spike. Das oito objeções, **aceitamos seis integralmente** (1, 2, 3, 5, 6 e 7), **a 4 em parte, com rebate fundamentado**, e **a 8 em parte**.

Na maioria dos casos, os ADRs estão coerentes entre si e o defeito está nos diagramas, que ficaram desalinhados dos ADRs. Isso não diminui a objeção: o diagrama é o que o leitor vê primeiro, e para o Envelope E a consistência entre os artefatos faz parte da prova. Ao revisar, encontramos também duas inconsistências que o revisor não citou (spike x ADR 0005, e a contagem de unidades do ADR 0001 x C4). Estão registradas nas respostas 3 e 8.

Mudanças que contradigam um ADR existente serão feitas por **novo ADR com status "substitui o ADR X"**, conforme a Entrega 5.

## Resumo

| # | Tema | Posição | Onde está o defeito | O que muda |
|---|------|---------|---------------------|------------|
| 1 | Trilha central de auditoria no C4 | Aceita | C4 contêineres contradiz o ADR 0006 | C4 contêineres |
| 2 | Pseudonimização tardia | Aceita | C4 componentes contradiz o ADR 0005 | C4 componentes; contrato do evento |
| 3 | Spike não cobre eliminação completa | Aceita | Spike e backups | Spike; novo ADR 0009 |
| 4 | Cartão offline e dupla aceitação | Aceita em parte, rebate em parte | ADR 0008 (integridade) | ADR 0008; resposta 1 |
| 5 | Topologia da telemetria | Aceita | C4 contêineres contradiz o ADR 0007 | C4 contêineres |
| 6 | Observabilidade x evidência de auditoria | Aceita | ADR 0004 | ADR 0004; novo ADR 0009 |
| 7 | Idempotência nas integrações financeiras | Aceita | ADR 0003 | ADR 0003 |
| 8 | Carga operacional | Aceita em parte | ADR 0001/0004 e C4 | Matriz de responsabilidades; SLO/RTO |

---

## Resposta à Objeção 1: qual é a fonte oficial de auditoria?

**Veredito: aceita. O diagrama contradiz o ADR 0006, e é o diagrama que está errado.**

O revisor tem razão e a contradição é mais direta do que ele descreveu. O ADR 0006 diz, entre as alternativas descartadas, "trilha central de todo evento de negócio: descartada por duplicar o Event Store e ferir o ADR 0005". Já o C4 de contêineres mostra o `Serviço de Trilha de Auditoria` recebendo "todo evento de negócio" do Barramento de Eventos, ou seja, desenha justamente a alternativa que o ADR descartou.

Os documentos de decisão já definem a fonte oficial **por tipo de informação**: fatos financeiros no Event Store (ADR 0005), alterações do Atendimento no log append-only próprio (ADR 0006), e correlação entre unidades por identificador comum (ADR 0004). O próprio ADR 0006 registra, como consequência, que reconstruir uma operação entre subdomínios "junta dois registros, o log e o Event Store". O modelo que o Grupo 07 propõe é, portanto, o dos ADRs; o que falta é dizer isso de forma explícita e consertar o desenho.

**O que vai mudar:**

1. **C4 de contêineres:** remover o `Serviço de Trilha de Auditoria` e o fluxo "todo evento de negócio". O Tribunal de Contas passa a receber o relatório de fechamento da Conciliação e a consultar as duas fontes oficiais (Event Store e log do Atendimento), com os conectores rotulados.
2. **ADR 0006:** acrescentar um parágrafo que declara a regra de precedência por tipo e o uso do **identificador de correlação** comum para ligar os dois registros. Não há mudança de decisão, então não é preciso novo ADR.
3. O mapa (linha E03) será ajustado para apontar para essa regra.

---

## Resposta à Objeção 2: a pseudonimização aparece tarde no fluxo

**Veredito: aceita. O diagrama confirma a leitura do revisor.**

No C4 de componentes, a ordem é: Recuperador de Eventos, Validador de Dados, Seletor de Regras Vigentes, Calculadora de Valores, **Pseudonimizador de Dados Pessoais**, Gravador de Eventos Financeiros. Portanto, se o evento chega com dado pessoal, ele atravessa quatro componentes antes de ser pseudonimizado. Isso contradiz o ADR 0005, que diz que os eventos guardam só referência opaca, e amplia o conjunto de componentes alcançados por um pedido de eliminação.

Há um fato a favor do desenho correto: pelo ADR 0002, quem é dono do Cadastro de Passageiros é Cartões e Recarga, que portanto já detém a ligação entre cartão e passageiro. Faz sentido que ele publique eventos só com a referência opaca desde a origem. O `Pseudonimizador` dentro da Conciliação deve ser a **segunda barreira**, e não a única.

**O que vai mudar:**

1. **C4 de componentes:** o `Pseudonimizador` passa a ser o **primeiro** componente do pipeline, antes do Validador de Dados, com conector rotulado. Seletor e Calculadora só enxergam a referência opaca.
2. **Contrato do evento financeiro:** declara que nenhum dado de identificação pessoal (nome, CPF, hash de CPF) faz parte dele, e o Pseudonimizador **rejeita** (e não só remove) evento que viole o contrato, registrando a ocorrência.
3. **ADR 0005:** frase de fronteira: o que está antes do pseudonimizador pode tocar dado pessoal; o que está depois não pode.

---

## Resposta à Objeção 3: o spike prova só parte da eliminação

**Veredito: aceita.**

O revisor tem razão. O ADR 0005 e o README do spike já registravam que o spike cobre apenas Event Store e cadastro em memória, sem as cópias nem os backups. A pergunta 5 e o ADR 0005 também já diziam que os backups "precisam de prazo de expiração definido", mas **nenhum documento define esse prazo nem o comportamento numa restauração**. Declarar o limite não é provar a decisão, e o ADR 0005 promete apagar cópias em Banco de Cartões, Modelo de Leitura e registro do Atendimento, o que o spike não demonstra.

Ao reler o código, encontramos ainda uma divergência que o revisor não apontou: o ADR 0005 prevê uma referência opaca, de **identificador aleatório**, mais um **vínculo** que o pedido de eliminação apaga. No spike, o evento guarda `usuario_id_ref` com o mesmo valor (`usr_001`) que é a chave do cadastro, e não existe vínculo separado. Após a eliminação, as viagens da mesma pessoa continuam ligadas entre si, o que a pergunta 5 já reconhecia como risco residual de reidentificação, mas o spike não mostra nem trata.

**O que vai mudar:**

1. **Spike (`exemplo.py`, hoje com 170 linhas, dentro do limite de 100 a 300):** (a) referência aleatória e **tabela de vínculo** entre referência e passageiro, que é o que a eliminação apaga; (b) fluxo de eliminação que percorre cada armazenamento simulado com dado pessoal (cadastro, banco de cartões, modelo de leitura, registro do Atendimento); (c) **verificação final** que falha se restar projeção identificável. O `saida-esperada.txt` e o README serão atualizados.
2. **Novo ADR 0009, retenção, backup e restauração:** define o prazo de expiração dos backups e o procedimento de restauração (a lista de eliminações já executadas é reaplicada antes de o sistema voltar ao ar).
3. **Crypto-shredding** permanece descartado, como no ADR 0005, que já registra o motivo e a condição para reabrir a decisão (se a auditoria exigir dado pessoal dentro do evento). Se o prazo de expiração dos backups se mostrar inviável no ADR 0009, a decisão será reavaliada.

**Onde mantemos a escolha.** O spike continua provando **uma decisão** (separar dado pessoal do fato financeiro), como exige a Entrega 3. A extensão cobre o fluxo de eliminação, mas não vai simular o sistema inteiro nem backups reais de um provedor de nuvem, e o README dirá isso.

---

## Resposta à Objeção 4: o cartão offline e a passagem aceita duas vezes

**Veredito: aceita em parte e rebate em parte.**

**Onde rebatemos.** A objeção afirma que a solução só *detecta* o uso duplicado depois. Isso não descreve o mecanismo completo. O ADR 0008 e a resposta 1 dizem que o cartão carrega o saldo operacional e um **número de sequência incrementado a cada uso**, "de modo que o segundo ônibus leia o estado já atualizado". Quem usa o cartão no ônibus A e depois no ônibus B é **recusado no B na hora**, com os dois offline. Isso é prevenção durante a operação sem rede, e o ADR a lista como consequência positiva.

A detecção posterior cobre o resto: cartão adulterado ou clonado, e estado que não pôde ser gravado. Ela não é uma lacuna: a pergunta 1 do enunciado pede exatamente como o sistema "descobre depois" o uso em dois ônibus. O ADR 0008 também já descarta, entre as alternativas, "detectar duplicidade só por idempotência". E, com um ônibus até 4 horas sem rede, dois validadores não se consultam entre si; a única garantia possível sem comunicação é estado carregado pelo cartão, que é o que adotamos.

**Onde aceitamos.**

1. O ADR 0008 diz que o cartão é parte da base de confiança e que seu estado "precisa de assinatura contra adulteração", mas **não descreve o mecanismo**: onde fica a chave, quem verifica a assinatura, como se evita replay do estado antigo e o que acontece com um cartão clonado. Dizer que precisa de assinatura não é demonstrar que a garantia vale.
2. A resposta 1 mistura prevenção e detecção no mesmo bloco, o que levou à leitura "só detecta depois".
3. Há ainda um desalinhamento interno: a resposta 1 e o ADR 0008 atribuem a detecção de sequências repetidas a Cartões e Recarga, enquanto o C4 de contêineres coloca a "identificação única" no `Serviço de Validação`. Vamos definir um único responsável.

**O que vai mudar:**

1. **ADR 0008:** seções separadas de **prevenção** (contador monotônico com assinatura, verificação pelo validador, proteção contra replay e clonagem) e **detecção e recuperação** (conciliação, bloqueio, divergência), com a **exposição máxima assumida** no pior caso (cartão clonado em validadores offline) como consequência negativa explícita.
2. **Resposta 1** reescrita com essa separação, e **C4** e ADR alinhados quanto a quem detecta a duplicidade.
3. Os detalhes criptográficos serão apoiados em documentação primária da tecnologia de cartão escolhida; não adotaremos números de segurança sem fonte.

---

## Resposta à Objeção 5: ADR 0007 e C4 mostram topologias diferentes

**Veredito: aceita. O erro está no diagrama.**

O ADR 0007, a resposta 3 e a linha C07 do mapa dizem a mesma coisa: a telemetria tem **broker persistente próprio**, separado do barramento financeiro. No C4 de contêineres há um único `Barramento de Eventos`, ao qual o `Serviço de Telemetria` publica o "evento de posição" junto com os demais fluxos. Como o isolamento de capacidade é justamente a defesa contra o pico de telemetria afetar Validação, Recarga e Conciliação, o diagrama, como está, não mostra essa proteção.

**O que vai mudar:**

1. **C4 de contêineres:** passa a mostrar **dois brokers** (telemetria e barramento financeiro), indicando quem produz e quem consome em cada um e o tipo de cada conector.
2. O mapa será conferido contra o novo C4.
3. O ADR 0007 permanece como está; não há novo ADR.

---

## Resposta à Objeção 6: observabilidade não garante, sozinha, a reconstrução da auditoria

**Veredito: aceita.**

O ADR 0004 diz que logs, métricas, rastreamento e chamadas externas ficam em serviço central com identificador de correlação. Isso responde "como sabemos que está de pé", mas não define retenção, imutabilidade, controle de acesso, sincronização de horário nem recuperação, e o texto deixa em aberto se esses registros servem de evidência. O princípio correto já existe no projeto: o ADR 0006 descarta o "log de aplicação comum" justamente "por ser alterável e sem garantia de completude". O problema é que esse princípio não foi levado ao ADR 0004.

**O que vai mudar:**

1. **ADR 0004:** adendo declarando que logs e traces são **observabilidade operacional** e **não são fonte oficial de auditoria**. As fontes oficiais são o Event Store (ADR 0005) e o log do Atendimento (ADR 0006).
2. **Novo ADR 0009:** define, para essas duas fontes oficiais, retenção, imutabilidade, sincronização de horário, controle de acesso, backup e recuperação, com base na documentação oficial do provedor de nuvem adotado, citada no ADR.

---

## Resposta à Objeção 7: duplicidade e reprocessamento nas integrações financeiras

**Veredito: aceita.**

Parte do problema já está tratada: a recarga tem identificador único aplicado uma só vez mesmo com reenvio (resposta 2); o ADR 0003 prevê que a recarga fica pendente até o reenvio se o banco cair; o `Validador de Dados` da Conciliação confere "integridade e duplicidade dos eventos" no C4 de componentes; e o spike demonstra que reprocessar eventos não duplica o total (cenário D). O que o ADR 0003 não define, e o revisor identificou, é o caso em que **a mesma confirmação de liquidação do banco ou do adquirente chega duas vezes**, ou chega com conteúdo diferente.

**O que vai mudar (ADR 0003):**

1. **Chave de idempotência** por operação financeira (identificador da recarga mais identificador da confirmação do banco ou adquirente).
2. **Registro persistente do estado da integração** por chave, classificando cada mensagem em **nova** (processa e gera efeito financeiro), **repetida** (registra o recebimento, sem novo efeito) ou **divergente** (mesma chave, conteúdo diferente; sem efeito e encaminhada a fila de exceção auditável).
3. O reprocessamento em lote usa a mesma regra, e a contagem de repetidas e divergentes entra no relatório de fechamento.

---

## Resposta à Objeção 8: carga operacional da arquitetura distribuída

**Veredito: aceita em parte.**

**Onde aceitamos.** O ADR 0001 reconhece que cinco unidades independentes "elevam o custo operacional", mas reconhecer o custo não demonstra que 15 desenvolvedores e uma pessoa de conformidade o sustentam. Faltam responsabilidades por unidade, SLO e RTO/RPO, e procedimentos de recuperação dos componentes críticos. O ADR 0004 prevê pipelines próprios e liberação gradual sem dimensionar o esforço da equipe para operá-los.

Também há uma inconsistência que a objeção ajuda a expor: o ADR 0001 lista cinco microsserviços (Cartões e Recarga, Telemetria, Informação ao Passageiro, Conciliação e Integração Externa), mas o C4 de contêineres mostra também um `Serviço de Validação`, além da API Gateway/BFF, que não constam dessa lista. A contagem do ADR e a do diagrama precisam coincidir.

**Onde mantemos.** Não vamos consolidar tudo num bloco só. O ADR 0001 já descarta "microsserviços em todos os subdomínios" pelo custo operacional e mantém o Atendimento, de baixo volume, em Monolito Modular; o ADR 0004 também descarta "todos os subdomínios como unidades independentes". Os subdomínios têm naturezas opostas (validação em tempo real, telemetria em fluxo contínuo, repasse em lote auditável), e o isolamento da telemetria é deliberado (ADR 0007). O que aceitamos é que **cada fronteira precisa pagar a conta operacional que cria**.

**O que vai mudar:**

1. **Matriz de responsabilidades** por unidade (time dono, atendimento de incidente, conformidade, versionamento de contrato).
2. **SLO e RTO/RPO** para os fluxos críticos (validação, recarga, fechamento do repasse, Event Store), registrados como **premissas do grupo**, justificadas pelos requisitos do caso, e não como dado de fonte externa.
3. **Procedimentos de recuperação** resumidos para Event Store, brokers e dados de auditoria.
4. **Reconciliar ADR 0001 e C4** quanto às unidades. Cada fronteira passará por um critério único: só se mantém se houver necessidade de **escala, isolamento ou implantação independente**. Se o `Serviço de Validação` ou outra unidade não passar, será incorporado a outra; se passar, entra na lista do ADR. Em qualquer dos dois casos, novo ADR "substitui o ADR 0001".

**Limite que admitimos:** ainda não fizemos a conta de esforço de operar os pipelines próprios. A matriz fará essa conta; se mostrar que o projeto não cabe na equipe, reduziremos unidades em vez de manter o desenho.

---

## Impacto consolidado para a Entrega 5

- **Novo ADR 0009:** retenção, backup e restauração, e garantias de evidência de auditoria (Objeções 3 e 6).
- **Possível novo ADR "substitui o ADR 0001"**, conforme a reconciliação de unidades (Objeção 8).
- **ADRs ajustados por adendo:** 0003 (idempotência), 0004 (observabilidade x evidência), 0005 (fronteira da pseudonimização), 0006 (regra de precedência e correlação), 0008 (prevenção x detecção).
- **Diagramas:** C4 de contêineres (remover trilha central; dois brokers; unidades alinhadas ao ADR 0001) e C4 de componentes (pseudonimização como primeira etapa).
- **Spike:** referência aleatória, tabela de vínculo, eliminação em todos os armazenamentos simulados e verificação final; README e `saida-esperada.txt` atualizados.
- **Novos anexos:** matriz de responsabilidades; SLO/RTO e procedimentos de recuperação.
- **Respostas obrigatórias:** perguntas 1 e 5 reescritas.
- Tudo registrado em `5-final/CHANGELOG.md`.
