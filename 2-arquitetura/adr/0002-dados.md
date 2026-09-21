# ADR 0002: distribuir a propriedade dos dados por subdomínio

**Status:** aceito

**Contexto:**  
O sistema manipula dados com características e requisitos de consistência distintos. Cartões e recargas mantêm informações de saldo e movimentações; a validação embarcada precisa tomar decisões mesmo quando o ônibus permanece sem conectividade; a telemetria recebe continuamente posições da frota; a informação ao passageiro realiza consultas derivadas desses dados; e a conciliação utiliza o histórico das operações para calcular e recalcular os repasses.

Uma base de dados compartilhada entre todas essas capacidades criaria acoplamento entre subdomínios e dificultaria sua evolução independente. Por outro lado, a separação dos dados introduz a necessidade de sincronização entre capacidades e impede que todas as informações estejam fortemente consistentes ao mesmo tempo.

O Envelope E acrescenta a necessidade de fiscalização e tratamento dos dados pessoais conforme a LGPD. O histórico necessário para auditoria financeira deve, portanto, ser separado dos dados pessoais identificáveis que não precisam permanecer indefinidamente.

**Decisão:**  
Distribuir a propriedade dos dados de acordo com as fronteiras dos subdomínios definidas na ADR 0001. Cada subdomínio será responsável pela escrita e manutenção de seus próprios dados, e outro subdomínio não poderá acessar diretamente suas tabelas.

A propriedade e a consistência serão definidas da seguinte forma:

- **Cartões e recarga:** será o proprietário dos dados de cartões, saldos e recargas. Alterações de saldo e operações financeiras dentro dessa fronteira exigem consistência forte. As alterações relevantes aos demais subdomínios serão publicadas por eventos.

- **Validação embarcada:** manterá localmente no validador apenas os dados necessários para realizar a validação durante períodos sem conectividade e os registros das validações ainda não sincronizadas. Quando a conexão for restabelecida, essas operações serão enviadas ao backend. A cópia embarcada é, portanto, uma visão necessária à operação offline, e não a fonte central de verdade dos dados de cartões.

- **Telemetria da frota:** será proprietária das posições e demais dados de telemetria recebidos dos veículos. Esses dados serão propagados de forma assíncrona para os consumidores que necessitam deles.

- **Informação ao passageiro:** manterá modelos de leitura próprios derivados da telemetria. Esses modelos poderão apresentar alguns segundos de defasagem e serão atualizados de forma assíncrona, adotando consistência eventual entre a telemetria e as informações exibidas ao passageiro.

- **Conciliação:** manterá os dados necessários ao fechamento financeiro, incluindo os resultados dos cálculos e as informações necessárias para permitir auditoria e recálculo conforme as regras aplicáveis à data de cada viagem. Os registros financeiros necessários à fiscalização serão preservados sem depender da permanência de dados pessoais identificáveis.

- **Atendimento:** será proprietário dos dados específicos do atendimento e utilizará as interfaces publicadas pelos demais subdomínios quando precisar consultar informações que não lhe pertencem.

Dados pertencentes a outro subdomínio serão obtidos por interfaces ou eventos publicados pelo proprietário, nunca por acesso direto às suas tabelas.

Será utilizada **consistência forte dentro das operações que possuem invariantes financeiras**, especialmente alterações de saldo e consolidação dos resultados financeiros. Entre subdomínios, quando não houver necessidade de resposta imediata, será utilizada **consistência eventual por eventos**.

Os eventos necessários para auditoria e reconstrução financeira não deverão exigir a retenção permanente de dados pessoais identificáveis. Dados pessoais e dados financeiros auditáveis serão mantidos separados de forma que os primeiros possam seguir seu ciclo de retenção e exclusão sem destruir o histórico financeiro necessário à fiscalização.

**Alternativas consideradas:**

- **Utilizar um único banco de dados compartilhado por todo o sistema:** descartada porque permitiria que diferentes subdomínios dependessem diretamente das mesmas tabelas e esquemas. Mudanças nos dados de uma capacidade poderiam afetar outras capacidades e reduzir a independência definida na ADR 0001.

- **Aplicar consistência forte global entre todos os subdomínios:** descartada porque exigiria coordenação distribuída inclusive em fluxos que não necessitam de consistência imediata. Além disso, a validação precisa continuar funcionando durante períodos sem conectividade e a informação ao passageiro tolera defasagem de alguns segundos.

- **Aplicar consistência eventual a todos os dados:** descartada porque operações relacionadas a saldo e resultados financeiros possuem invariantes que não podem depender apenas de convergência posterior.

- **Manter todos os eventos permanentemente com os dados pessoais identificáveis para facilitar a auditoria:** descartada porque a retenção permanente de informações pessoais entraria em tensão com as exigências de tratamento e exclusão de dados pessoais do Envelope E. A auditabilidade financeira deve ser preservada sem depender da permanência desses dados identificáveis.

**Consequências:**

- **Positivas:** os subdomínios mantêm propriedade explícita sobre seus dados e podem evoluir seus modelos internos sem depender diretamente dos esquemas de outras capacidades; operações financeiras críticas podem utilizar consistência forte sem impor esse custo a todo o sistema; a consistência eventual permite a sincronização das operações realizadas durante períodos sem conectividade; modelos de leitura próprios evitam que consultas de passageiros sobrecarreguem os dados transacionais; e a separação entre histórico financeiro e dados pessoais permite preservar a auditabilidade exigida pela fiscalização sem tornar a retenção de dados pessoais condição para o recálculo.

- **Negativas:** o mesmo fato pode existir em representações diferentes em mais de um subdomínio; consumidores podem visualizar temporariamente informações desatualizadas devido à consistência eventual; a sincronização das validações realizadas offline exige tratamento de duplicidade, ordenação e falhas de entrega; consultas que combinam informações pertencentes a vários subdomínios tornam-se mais complexas; e a separação entre informações pessoais e registros financeiros aumenta a complexidade do modelo de dados e dos processos de auditoria.