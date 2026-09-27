# Respostas às Perguntas Obrigatórias

## 1. Como o validador aceita passagem sem rede e detecta duplicidade depois?

A validação da passagem ocorre localmente no equipamento embarcado. O validador mantém as regras e os dados mínimos necessários para decidir se uma passagem pode ser aceita, sem depender de uma chamada ao backend. Dessa forma, a operação consegue responder em até 300 ms mesmo durante períodos de até quatro horas sem conexão.

Internamente, a aplicação embarcada utiliza Arquitetura Hexagonal para separar a regra de validação dos mecanismos de leitura do cartão, armazenamento local e comunicação com a nuvem.

Cada validação gera uma operação com identificador único. Além disso, o validador mantém localmente o controle das utilizações já realizadas pelo cartão durante a operação, permitindo aplicar a regra de anti-duplicidade antes de liberar novamente uma passagem.

Enquanto o ônibus estiver sem conexão, as validações ficam armazenadas localmente. Quando a rede retorna, essas operações são enviadas de forma assíncrona ao backend por meio de eventos.

Como a entrega de uma mensagem pode ocorrer mais de uma vez em situações de falha ou perda de confirmação, os consumidores do backend também são idempotentes. Assim, um evento com identificador já processado não produz novamente seus efeitos.

**Sustentação:** ADR 0001, ADR 0002, ADR 0004 e Diagrama C4 de Contêineres.

---

## 2. Como manter a consistência do saldo do cartão entre a aplicação e o ônibus com atraso de sincronização?

A consistência não pode depender apenas do backend, pois o ônibus precisa continuar validando passagens mesmo quando permanece várias horas sem conexão. Se cada validador mantivesse apenas uma cópia independente do saldo central, dois ônibus offline poderiam aceitar gastos com base no mesmo saldo desatualizado.

Para evitar esse problema, o cartão é utilizado como portador do **saldo operacional necessário à validação offline**, juntamente com informações de controle da última operação. O validador lê o estado do cartão, verifica as regras da passagem e, quando aceita a utilização, registra a operação no próprio cartão e no armazenamento local do equipamento.

Dessa forma, ao utilizar o mesmo cartão em outro ônibus, o novo validador lê o estado já atualizado no próprio cartão, mesmo que nenhum dos dois veículos esteja conectado ao backend.

O subdomínio de Cartões e Recarga continua sendo responsável pelo histórico financeiro, pelas recargas e pela consolidação central. Quando houver conectividade, as operações realizadas nos ônibus são sincronizadas por eventos e processadas de forma idempotente.

As recargas também recebem identificadores únicos para impedir que uma mesma operação seja aplicada mais de uma vez durante reenvios ou falhas de comunicação.

Assim, existem dois níveis complementares:

- no ambiente embarcado, o cartão mantém o estado necessário para impedir gastos duplicados durante a operação offline;
- no backend, Cartões e Recarga mantém o histórico financeiro central, realiza a reconciliação e garante que cada operação sincronizada seja aplicada uma única vez.

**Sustentação:** ADR 0002, ADR 0004 e Diagrama C4 de Contêineres.

---

## 3. Como a telemetria escala no pico sem derrubar o resto do sistema?

A Telemetria da Frota é tratada como uma capacidade independente das demais partes do sistema. Isso permite que seus recursos sejam aumentados sem obrigar Validação, Cartões/Recarga, Conciliação ou Atendimento a escalar junto com ela.

A ingestão das posições utiliza Arquitetura Orientada a Eventos. As posições recebidas são colocadas em um mecanismo de mensageria persistente antes do processamento pelos consumidores.

Essa separação permite que a ingestão continue recebendo dados mesmo quando algum consumidor estiver temporariamente mais lento. Em caso de falha de processamento, as mensagens podem ser entregues novamente, e os consumidores devem tratar reprocessamento de forma idempotente.

O sistema precisa absorver aproximadamente 80 posições por segundo em condições normais e até cinco vezes esse volume nos períodos de pico. Como a Telemetria possui uma unidade de implantação própria, ela pode ser escalada de forma independente para atender esse aumento.

Para as consultas dos passageiros, a solução utiliza CQRS. A Telemetria alimenta modelos de leitura próprios utilizados pela Informação ao Passageiro, que tolera alguns segundos de defasagem.

Com isso, um pico de consultas no aplicativo não aumenta diretamente a carga sobre o fluxo responsável por receber as posições dos ônibus.

**Sustentação:** ADR 0001, ADR 0002, ADR 0004 e Diagrama C4 de Contêineres.

---

## 4. Como recalcular o repasse mensal se a regra de divisão mudar no meio do mês?

O processo de Repasse e Conciliação foi projetado para ser reconstruível e reexecutável.

Os fatos financeiros necessários ao fechamento são preservados com suas datas, enquanto as regras utilizadas no cálculo possuem período de vigência. Dessa forma, o sistema consegue determinar qual regra deve ser utilizada para cada viagem durante um recálculo.

O processamento da Conciliação utiliza Pipes and Filters e é dividido em etapas independentes:

1. recuperar os fatos financeiros do período;
2. validar os dados recebidos;
3. identificar a regra vigente na data de cada viagem;
4. calcular os valores correspondentes;
5. consolidar os resultados por operadora;
6. gerar o fechamento financeiro.

Se uma regra de divisão for alterada, o pipeline pode ser executado novamente. O componente responsável pela seleção das regras consulta a versão aplicável à data de cada viagem, permitindo reconstruir o resultado do mês sem alterar os fatos financeiros originais.

Event Sourcing é utilizado de forma localizada para preservar os fatos financeiros necessários à reconstrução e à auditoria, enquanto Pipes and Filters organiza o processo de recálculo.

**Sustentação:** ADR 0001, ADR 0002, ADR 0005 e Diagrama C4 de Componentes.

---

## 5. Como guardar tudo para o Tribunal de Contas e ainda apagar o que a LGPD manda apagar?

A arquitetura separa as informações necessárias à auditoria financeira dos dados pessoais identificáveis dos passageiros.

Os fatos financeiros necessários para reconstrução de saldos, conciliação e fiscalização são armazenados em um histórico append-only. Esse histórico contém informações como identificador do evento, valor, data, tipo da operação e uma referência ao cadastro relacionado, mas não precisa armazenar diretamente nome, CPF ou outros dados pessoais do passageiro.

Os dados pessoais ficam em um armazenamento separado, com ciclo de retenção e exclusão próprio.

Quando uma solicitação de eliminação de dados pessoais for aplicável, os dados identificáveis podem ser removidos dessa base sem alterar os fatos financeiros já registrados.

Após a eliminação, o histórico financeiro continua permitindo responder perguntas como:

- qual valor foi debitado;
- quando a operação ocorreu;
- qual regra foi utilizada;
- qual operadora participou;
- como o valor do fechamento foi calculado.

O que deixa de ser possível, quando o dado pessoal correspondente é eliminado, é recuperar a identidade do passageiro apenas a partir do histórico financeiro.

Por isso, Event Sourcing é utilizado somente nos subdomínios em que a reconstrução do histórico realmente é necessária, principalmente Cartões/Recarga e Conciliação. Ele não é utilizado como mecanismo geral para armazenar permanentemente todos os dados do sistema.

Essa separação permite manter a trilha necessária para fiscalização do Tribunal de Contas sem tornar a permanência dos dados pessoais uma condição para a auditoria financeira.

**Sustentação:** ADR 0002, ADR 0005 e Diagrama C4 de Componentes.