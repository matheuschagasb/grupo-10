# ADR 0003: isolar integrações com sistemas externos por portas e adaptadores

**Status:** aceito

**Contexto:**  
O sistema de transporte coletivo precisa se integrar com sistemas externos, incluindo banco, adquirente, operadoras e outros terceiros. Esses sistemas possuem contratos, protocolos e formatos de dados próprios, que não são controlados pela equipe responsável pelo sistema.

Alterações nesses contratos externos não devem se propagar diretamente para as regras internas de validação, cartões e recarga, conciliação ou demais subdomínios. Além disso, falhas ou indisponibilidade de um terceiro não devem comprometer capacidades que possam continuar operando de forma independente.

O Envelope E exige fiscalização por órgão regulador, aumentando a importância de controlar e rastrear as interações realizadas nas fronteiras externas.

**Decisão:**  
Isolar as integrações com banco, adquirente, operadoras e demais terceiros utilizando arquitetura hexagonal, representando as necessidades do sistema por portas e implementando um adaptador específico para cada integração externa.

As regras de domínio dependerão das portas definidas internamente, e não dos contratos, bibliotecas, protocolos ou formatos fornecidos pelos terceiros. Cada adaptador será responsável por traduzir entre o modelo interno e o contrato do sistema externo correspondente.

As integrações serão organizadas da seguinte forma:

- **Banco e adquirente:** adaptadores próprios encapsularão seus contratos e formatos, impedindo que detalhes dessas integrações façam parte das regras internas de cartões, recarga ou conciliação.
- **Operadoras e demais sistemas externos:** cada integração será implementada por um adaptador correspondente à porta necessária pelo sistema, permitindo que mudanças externas permaneçam restritas à fronteira de integração.
- **Auditoria:** as interações relevantes com terceiros deverão produzir registros que permitam identificar a operação realizada e seu resultado, de modo a sustentar a fiscalização sem espalhar essa responsabilidade pelas regras de domínio.

Chamadas síncronas serão utilizadas quando a operação exigir uma resposta imediata do terceiro. Quando não houver necessidade de resposta imediata, a comunicação poderá ser desacoplada por eventos ou processamento assíncrono, conforme as fronteiras estabelecidas na ADR 0001.

Não será adotado um ESB como intermediário obrigatório para todas as integrações. Mediação centralizada será considerada apenas quando houver necessidade concreta de integrar sistemas heterogêneos com contratos e formatos impostos e quando os benefícios de tradução, roteamento ou aplicação centralizada de políticas justificarem seu custo.

Falhas dos sistemas externos deverão permanecer contidas na fronteira de seus respectivos adaptadores. Capacidades que não dependam da resposta imediata do terceiro não deverão ser interrompidas apenas pela indisponibilidade dessa integração.

**Alternativas consideradas:**

- **Integrar os sistemas externos diretamente às regras de domínio:** descartada porque faria as regras internas dependerem de contratos, formatos e tecnologias controlados por terceiros. Uma mudança externa poderia exigir alterações nas regras de negócio e ampliar o impacto das integrações sobre o restante do sistema.

- **Adotar um ESB como intermediário obrigatório para todas as integrações:** descartada porque centralizaria o tráfego das integrações em um componente adicional, acrescentando custo, latência e um possível ponto de indisponibilidade. A quantidade e as características das integrações apresentadas não justificam tornar o barramento o estilo dominante.

- **Criar integrações ponto a ponto sem uma fronteira arquitetural comum:** descartada porque cada subdomínio passaria a conhecer diretamente os contratos externos de que necessita, espalhando lógica de tradução, tratamento de falhas e dependências de terceiros pelo sistema.

**Consequências:**

- **Positivas:** as regras de domínio permanecem independentes das tecnologias e contratos dos terceiros; mudanças em banco, adquirente ou operadoras tendem a ficar concentradas nos respectivos adaptadores; integrações podem ser substituídas ou testadas sem depender diretamente dos sistemas externos; falhas externas podem ser isoladas na fronteira de integração; e o registro das interações externas favorece a rastreabilidade necessária à fiscalização.

- **Negativas:** cada sistema externo exige desenvolvimento e manutenção de seu próprio adaptador; a tradução entre modelos internos e contratos externos adiciona código e custo de desenvolvimento; mudanças incompatíveis nos contratos dos terceiros ainda exigem atualização dos adaptadores; mecanismos assíncronos, quando utilizados, aumentam a complexidade de tratamento de falhas e consistência; e não utilizar um barramento central significa que políticas comuns às integrações precisam ser padronizadas sem depender de um único intermediário.