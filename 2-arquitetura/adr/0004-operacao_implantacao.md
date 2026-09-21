# ADR 0004: implantar e escalar independentemente as capacidades críticas

**Status:** aceito

**Contexto:**  
O sistema possui capacidades com perfis operacionais distintos. A telemetria recebe continuamente posições da frota e deve suportar picos de até cinco vezes a carga normal sem perda de dados. Cartões e recargas possuem volume próprio de operações, enquanto a informação ao passageiro possui um perfil predominantemente de consulta.

A validação embarcada possui uma restrição diferente: a decisão de aceitar ou recusar uma passagem deve ocorrer em até 300 ms e continuar funcionando mesmo quando o ônibus permanecer por até quatro horas sem conexão 4G. Portanto, a disponibilidade do backend ou da rede não pode ser condição para a validação de uma passagem.

A solução será operada em nuvem pública e mantida por uma equipe de 15 desenvolvedores. Assim, é necessário permitir escala e implantação independentes onde houver necessidade concreta, sem transformar cada capacidade do sistema em uma unidade operacional independente.

O Envelope E também exige fiscalização por órgão regulador, tornando necessário que a operação permita acompanhar o processamento das transações relevantes e identificar falhas que possam comprometer a integridade ou a rastreabilidade das informações.

**Decisão:**  
Implantar de forma independente as capacidades que possuem necessidades próprias de escala, disponibilidade ou evolução, mantendo agrupadas aquelas que não justificam o custo operacional de uma unidade separada.

A operação e a implantação seguirão as seguintes regras:

- **Validação embarcada:** será implantada nos validadores dos ônibus e deverá realizar localmente a decisão de aceitar ou recusar a passagem. A indisponibilidade da nuvem ou da conexão 4G não poderá interromper essa decisão. Operações pendentes serão armazenadas localmente e sincronizadas quando a conectividade for restabelecida.

- **Cartões e recarga:** poderá ser implantado como unidade independente do restante do backend, permitindo evolução e escala próprias de acordo com seu volume de operações.

- **Telemetria da frota:** será implantada como unidade independente e poderá escalar separadamente para absorver o fluxo contínuo de posições e os picos de até cinco vezes a carga normal. A ingestão será desacoplada do processamento posterior por eventos, evitando que consumidores mais lentos interrompam o recebimento dos dados.

- **Informação ao passageiro:** poderá ser implantada e escalada independentemente da ingestão de telemetria, utilizando os modelos de leitura definidos na ADR 0002. Dessa forma, o aumento das consultas dos passageiros não deverá aumentar diretamente a carga sobre o processamento transacional da telemetria.

- **Conciliação:** será operada separadamente dos fluxos que exigem resposta imediata. O fechamento poderá ser executado e reexecutado sem bloquear validação, recarga, telemetria ou informação ao passageiro.

- **Atendimento:** permanecerá agrupado em uma única unidade de implantação modular enquanto sua carga e necessidade de disponibilidade não justificarem separação adicional.

As unidades independentes deverão permitir implantação e escala sem exigir a implantação simultânea de todo o sistema.

A operação deverá possuir observabilidade suficiente para acompanhar a saúde das unidades, o processamento das mensagens assíncronas e as integrações externas. Operações relevantes para fiscalização deverão produzir registros que permitam rastrear seu processamento e identificar falhas.

A arquitetura não dependerá de escalabilidade automática para corrigir qualquer tipo de gargalo. A escala independente será aplicada principalmente às capacidades cujo volume e perfil de carga justificam essa necessidade.

**Alternativas consideradas:**

- **Implantar todo o backend como uma única unidade:** descartada porque capacidades com perfis diferentes de carga e disponibilidade teriam de ser escaladas e implantadas em conjunto. Um pico de telemetria, por exemplo, poderia exigir recursos adicionais para componentes que não necessitam dessa escala.

- **Implantar cada subdomínio como um microsserviço independente:** descartada porque aumentaria a quantidade de unidades que precisam ser implantadas, monitoradas e mantidas. Para uma equipe de 15 desenvolvedores, esse custo não se justifica nos subdomínios que não possuem necessidade concreta de escala ou disponibilidade independente.

- **Executar a validação de passagem dependendo de uma chamada síncrona ao backend:** descartada porque a validação precisa responder em até 300 ms e continuar operando durante períodos de até quatro horas sem conectividade.

- **Processar telemetria de forma totalmente síncrona:** descartada porque consumidores lentos ou indisponíveis poderiam limitar a ingestão das posições e dificultar a absorção dos picos de cinco vezes a carga normal.

**Consequências:**

- **Positivas:** capacidades com maior volume podem ser escaladas sem exigir recursos adicionais para todo o sistema; falhas ou picos na telemetria ficam mais isolados das demais capacidades; a validação permanece disponível mesmo durante perda de conectividade; consultas dos passageiros podem escalar independentemente da ingestão de telemetria; a conciliação pode ser executada e reexecutada sem competir diretamente com os fluxos de resposta imediata; e a observabilidade das unidades e das mensagens favorece a identificação de falhas e a fiscalização.

- **Negativas:** múltiplas unidades de implantação aumentam a complexidade operacional em relação a uma única aplicação; a equipe precisa acompanhar aplicações, integrações e processamento assíncrono distribuídos; a sincronização após períodos sem conectividade introduz situações de recuperação que precisam ser tratadas; filas ou eventos acumulados podem aumentar a defasagem entre produção e consumo dos dados; e a implantação independente exige compatibilidade entre contratos durante a evolução das diferentes unidades.