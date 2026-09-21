# ADR 0005: limitar Event Sourcing ao histórico financeiro auditável

**Status:** aceito

**Contexto:**  
O sistema precisa permitir que operações financeiras relacionadas a cartões, recargas e conciliação sejam auditadas e reconstruídas. O fechamento financeiro também deve poder ser recalculado utilizando as regras vigentes na data de cada viagem, exigindo a preservação do histórico necessário para reproduzir os resultados.

O Envelope E acrescenta a fiscalização por órgão regulador e requisitos relacionados à LGPD. Isso cria uma tensão arquitetural: a preservação imutável de eventos favorece a auditabilidade e a reconstrução do histórico, enquanto dados pessoais identificáveis podem estar sujeitos a requisitos de eliminação e não devem permanecer indefinidamente em um armazenamento imutável apenas para viabilizar a auditoria financeira.

Aplicar Event Sourcing de forma indiscriminada aumentaria a complexidade de armazenamento, versionamento, reprocessamento e proteção dos dados. Por isso, seu uso deve ser limitado às capacidades em que a reconstrução histórica possui valor direto para o caso.

**Decisão:**  
Adotar Event Sourcing de forma localizada em Cartões/Recargas e Conciliação para os fatos financeiros que precisam ser preservados para auditoria, reconstrução de saldo e recálculo do fechamento.

Os eventos financeiros serão armazenados de forma append-only e representarão os fatos necessários para reconstruir o estado financeiro. Correções não apagarão nem alterarão eventos anteriores; quando necessário, serão representadas por novos eventos de reversão ou compensação.

Dados pessoais identificáveis não serão armazenados diretamente no fluxo permanente de eventos financeiros quando não forem necessários para a reconstrução do resultado. Quando uma operação precisar estar associada a uma pessoa, o evento utilizará um identificador de referência, enquanto os dados pessoais correspondentes permanecerão fora do armazenamento imutável e seguirão seu próprio ciclo de retenção e eliminação.

O Event Sourcing não será utilizado como mecanismo geral de persistência dos demais subdomínios. Capacidades que necessitam apenas do estado atual continuarão utilizando seus modelos de persistência adequados às decisões das ADRs anteriores.

As projeções e processos que consumirem os eventos deverão ser reconstruíveis e tratar reprocessamento sem repetir indevidamente os efeitos de uma operação já executada.

Antes de consolidar essa decisão na implementação, será produzido um código pequeno para verificar a viabilidade da separação entre o histórico financeiro imutável e os dados pessoais identificáveis.

O código deverá demonstrar pelo menos o seguinte cenário:

1. registrar eventos financeiros associados a um identificador, sem armazenar os dados pessoais diretamente nesses eventos;
2. reconstruir o estado financeiro a partir do histórico;
3. produzir uma projeção utilizada pela conciliação;
4. remover os dados pessoais associados ao identificador;
5. reconstruir novamente o histórico financeiro e demonstrar que a auditoria e o recálculo continuam possíveis sem recuperar os dados pessoais eliminados;
6. reprocessar os mesmos eventos sem duplicar o resultado financeiro.

A decisão será considerada viável se o código demonstrar que a eliminação dos dados pessoais não impede a reconstrução do estado financeiro nem altera o resultado da conciliação.

**Alternativas consideradas:**

- **Armazenar apenas o estado atual e manter uma tabela de auditoria:** descartada porque o histórico de alterações não oferece, por si só, a mesma capacidade de reconstruir o estado a partir dos fatos financeiros que produziram o resultado.

- **Adotar Event Sourcing em todos os subdomínios:** descartada porque capacidades que necessitam apenas do estado atual não justificam o custo adicional de armazenamento, versionamento de eventos, projeções e reprocessamento. Além disso, ampliar o armazenamento imutável aumentaria a dificuldade de tratamento dos dados pessoais.

- **Armazenar dados pessoais diretamente nos eventos financeiros:** descartada porque vincularia a reconstrução financeira à retenção desses dados e criaria tensão entre a imutabilidade do histórico e os requisitos de eliminação de dados pessoais.

- **Eliminar eventos financeiros quando houver solicitação de eliminação dos dados pessoais associados:** descartada porque remover fatos do histórico poderia comprometer sua integridade e impedir a reconstrução e o recálculo exigidos para auditoria.

**Consequências:**

- **Positivas:** o estado financeiro pode ser reconstruído a partir dos fatos registrados; o fechamento pode ser recalculado utilizando o histórico preservado; eventos anteriores não precisam ser alterados para representar correções; a fiscalização dispõe de um histórico auditável das operações financeiras; e a separação entre eventos financeiros e dados pessoais permite que a eliminação destes não destrua o histórico necessário à auditoria.

- **Negativas:** a equipe precisa lidar com versionamento e evolução dos eventos ao longo do tempo; projeções precisam ser construídas e mantidas para consultas; o armazenamento do histórico cresce continuamente; consumidores e projeções precisam tratar reprocessamento e duplicidade; a separação entre identificadores e dados pessoais aumenta a complexidade do modelo; e a equipe passa a operar dois ciclos distintos de dados, um relacionado ao histórico financeiro e outro ao tratamento dos dados pessoais.