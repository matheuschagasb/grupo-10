# Entrega 4a — Leitura Cruzada

**Grupo revisor:** Grupo 10  
**Grupo revisado:** Grupo 08  
**Caso:** Ônibus — bilhetagem e mobilidade urbana  
**Envelope revisado:** A — Startup

## Objeção 1 — A solução não garante que a mesma passagem nunca seja aceita duas vezes

### Decisão ou trecho atacado
**Arquivo:** `Entrega_2___Documento_de_Arquitetura___Caso__nibus___Envelope_A__Startup___Grupo_08_2026_09_27T11_59_31.md`  
**Seção:** `5. Mapa de restrições e decisões — R6`  
**Complemento:** `spike.py`, cenários 5 e 6.

O documento afirma que o requisito “nunca aceitar a mesma passagem duas vezes” é atendido com uma chave de idempotência formada por cartão, timestamp e veículo, seguida de deduplicação na sincronização.

### Argumento
O próprio spike mostra que, quando o mesmo cartão é usado em dois ônibus enquanto os dois estão offline, ambos os validadores aceitam a passagem. A duplicidade só é identificada depois, quando os dois ônibus sincronizam com o servidor central.

Além disso, a chave de idempotência inclui o identificador do veículo. Portanto, duas validações do mesmo cartão em ônibus diferentes geram chaves diferentes e não podem ser impedidas localmente por esse mecanismo.

Assim, a solução apresentada detecta posteriormente um possível uso duplicado, mas não sustenta a garantia escrita no documento de que a mesma passagem nunca será aceita duas vezes.

### O que faríamos no lugar
Distinguiríamos duas garantias: impedir duplicidade no mesmo validador e detectar conflitos entre ônibus depois da sincronização. Para reduzir o risco entre ônibus offline, usaríamos também um estado monotônico associado ao cartão, como um número de sequência atualizado a cada uso, para que o próximo validador consiga observar que houve uma utilização anterior.

---

## Objeção 2 — O saldo local pode ficar inconsistente entre dois ônibus offline

### Decisão ou trecho atacado
**Arquivo:** `spike.py`  
**Seção:** classe `EmbeddedValidator`, criação da tabela `cards` e método `validate()`.

O spike cria uma base SQLite independente para cada validador e copia para ela o saldo dos cartões. O débito é feito apenas nessa cópia local.

### Argumento
Dois validadores offline podem possuir cópias iguais e desatualizadas do saldo do mesmo cartão. Se um cartão tiver saldo suficiente para apenas uma passagem, ele ainda pode ser aceito em dois ônibus diferentes antes que qualquer sincronização aconteça.

O mecanismo de detecção cross-bus do spike também compara o mesmo cartão no mesmo minuto. Se o passageiro utilizar o cartão em ônibus diferentes em minutos diferentes, o conflito de saldo pode existir sem ser classificado como duplicidade pelo mecanismo apresentado.

Isso deixa sem solução completa a exigência de manter o saldo consistente entre uso offline e sincronização posterior.

### O que faríamos no lugar
Evitaríamos tratar a cópia existente em cada validador como estado suficiente para representar o saldo durante longos períodos offline. Manteríamos no cartão um saldo operacional ou um contador de sequência protegido contra adulteração e reconciliaríamos esse estado com o backend quando a conexão voltasse.

---

## Objeção 3 — A telemetria foi separada na entrada, mas volta a disputar o banco transacional

### Decisão ou trecho atacado
**Arquivo:** `Entrega_2___Documento_de_Arquitetura___Caso__nibus___Envelope_A__Startup___Grupo_08_2026_09_27T11_59_31.md`  
**Seção:** `3. Diagrama C4 — Nível 2: Contêineres`.

A ingestão de telemetria utiliza Lambda e Kinesis, mas depois grava as posições diretamente no mesmo PostgreSQL RDS definido como fonte da verdade transacional da Aplicação Central.

### Argumento
O uso de Kinesis e Lambda desacopla a entrada, porém o armazenamento final continua compartilhado com cartões, recargas, atendimento e repasse. Em um pico de telemetria, muitas gravações continuam concorrendo pelos mesmos recursos do banco utilizados pelas operações transacionais.

Para o Envelope A isso também cria um custo importante: a startup pode acabar dimensionando o banco transacional de acordo com o fluxo mais pesado do sistema, mesmo que os outros módulos não precisem dessa capacidade.

### O que faríamos no lugar
Separaríamos o histórico de telemetria do banco transacional principal. O fluxo bruto poderia ser armazenado em um armazenamento próprio para telemetria ou em objetos, mantendo no Redis apenas a projeção necessária para consultas de posição e previsão do passageiro.

---

## Objeção 4 — O custo de extrair um módulo para microsserviço foi simplificado demais

### Decisão ou trecho atacado
**Arquivo:** `Entrega_2___Documento_de_Arquitetura___Caso__nibus___Envelope_A__Startup___Grupo_08_2026_09_27T11_59_31.md`  
**Seção:** `1. Resumo executivo → O que NÃO estamos fazendo agora — e como não vai doer depois`.

O documento afirma que, por existirem módulos com contratos explícitos, extrair um deles para microsserviço exigiria “apenas criar um adaptador HTTP onde hoje há chamada local”.

### Argumento
A troca da chamada local por HTTP é apenas uma parte da extração. Hoje os módulos fazem parte do mesmo processo, usam o mesmo banco físico e são implantados juntos. Uma separação futura também exigiria tratar propriedade e migração dos dados, transações que atravessam módulos, falhas de rede, retries, timeouts, observabilidade, compatibilidade de contratos e implantação independente.

Como a principal pergunta do Envelope A é justamente o que será adiado agora e como evitar que isso doa depois, essa afirmação subestima o custo real da mudança.

### O que faríamos no lugar
Manteríamos o monolito modular, pois ele combina com a equipe de seis pessoas, mas registraríamos quais módulos são candidatos reais à extração e quais dependências precisam ser eliminadas antes disso. Também deixaríamos explícito que contratos internos reduzem o custo da migração, mas não tornam a extração apenas uma troca de protocolo.

---

## Objeção 5 — A infraestrutura proposta pode ser grande demais para um piloto de quatro meses sem equipe de operação

### Decisão ou trecho atacado
**Arquivo:** `Entrega_2___Documento_de_Arquitetura___Caso__nibus___Envelope_A__Startup___Grupo_08_2026_09_27T11_59_31.md`  
**Seções:** `1. Resumo executivo`, `3. Diagrama C4 — Nível 2: Contêineres` e `5. Mapa de restrições e decisões — R1, R2 e R3`.

O projeto usa Aplicação Central, SQS, Kinesis, Lambda, RDS, Redis e S3, além dos validadores embarcados, mesmo com uma equipe de seis desenvolvedores, sem equipe de operação e com um piloto em uma única linha em quatro meses.

### Argumento
Serviços gerenciados reduzem o trabalho de manter servidores, mas não eliminam operação. Cada componente ainda exige configuração, permissões, monitoramento, alarmes, controle de custos, tratamento de falhas e conhecimento suficiente para diagnosticar problemas entre serviços.

A arquitetura afirma que essa composição reduz o custo operacional, mas não mostra por que todos esses componentes precisam existir já no primeiro piloto. Para um envelope com caixa de seis meses, o custo de complexidade também deveria ser tratado como uma restrição arquitetural.

### O que faríamos no lugar
Começaríamos com a menor infraestrutura que ainda satisfizesse os requisitos do piloto e definiríamos gatilhos objetivos para adicionar componentes. Por exemplo, Redis ou uma infraestrutura específica de streaming entrariam quando métricas de carga justificassem essa separação, e não apenas por antecipação do cenário completo.

---

## Objeção 6 — O spike não possui saída determinística e o teste de 300 ms não representa o ambiente real

### Decisão ou trecho atacado
**Arquivo:** `spike.py`  
**Seção:** `CENÁRIO 7 — Benchmark de latência`.

O spike usa `time.monotonic()` para medir cada validação e imprime latência máxima e média, concluindo que as validações ficaram abaixo de 300 ms.

### Argumento
Como o tempo é medido durante a execução, os valores variam conforme máquina, sistema operacional e carga do computador. Por isso, duas execuções do programa não produzem necessariamente a mesma saída, apesar de a Entrega 3 exigir resultado determinístico registrado em `saida-esperada.txt`.

Além disso, o teste usa SQLite em memória em um computador comum. Isso prova que a lógica implementada é rápida naquele ambiente, mas não demonstra que o validador embarcado real, com armazenamento persistente e hardware próprio, continuará abaixo de 300 ms.

### O que faríamos no lugar
Deixaríamos a saída principal do spike totalmente determinística, verificando apenas resultados funcionais esperados. O teste de desempenho ficaria separado como experimento complementar e, para sustentar o requisito dos 300 ms, seria necessário executar a medição em um ambiente mais próximo do hardware embarcado real.
