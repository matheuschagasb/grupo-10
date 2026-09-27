# ADR 0003: isolar integrações externas por portas e adaptadores

**Status:** aceito

## Contexto

O sistema precisa se integrar com banco, adquirente, operadoras e outros sistemas externos que possuem contratos, protocolos e formatos próprios.

Esses detalhes não devem se espalhar pelas regras internas do sistema. Além disso, falhas ou mudanças de um terceiro devem ter impacto limitado sobre as demais capacidades.

O Envelope E também exige rastreabilidade das interações externas para fins de fiscalização.

## Decisão

Utilizar Arquitetura Hexagonal nas fronteiras de integração, representando as necessidades do sistema por portas internas e implementando adaptadores específicos para cada sistema externo.

| Integração | Decisão |
|---|---|
| **Banco / Adquirente** | Utilizar adaptadores próprios para traduzir contratos, mensagens e formatos externos para o modelo interno. |
| **Operadoras** | Isolar protocolos e formatos específicos em adaptadores dedicados. |
| **Sistemas legados** | Utilizar adaptadores para impedir que estruturas e regras do legado se propaguem para o domínio. |
| **Auditoria** | Registrar as interações relevantes, seus identificadores, resultados e falhas para permitir rastreabilidade. |

As regras de negócio dependerão das portas definidas pelo próprio sistema, e não diretamente de bibliotecas, protocolos ou formatos pertencentes aos terceiros.

Chamadas síncronas serão utilizadas quando houver necessidade de resposta imediata. Quando essa resposta não for necessária, a integração poderá utilizar eventos ou processamento assíncrono conforme definido na ADR 0001.

Um ESB não será adotado como intermediário obrigatório. A utilização de mecanismos de mediação centralizada somente será considerada caso surja uma necessidade concreta de tradução, roteamento ou aplicação compartilhada de políticas entre várias integrações.

Falhas externas devem permanecer contidas nos respectivos adaptadores sempre que possível.

## Alternativas consideradas

- **Integração direta com as regras de domínio:** descartada porque aumentaria o acoplamento com contratos e tecnologias controlados por terceiros.
- **ESB obrigatório para todas as integrações:** descartado porque adicionaria complexidade, latência e dependência de um componente central sem necessidade suficiente no cenário atual.
- **Integrações ponto a ponto sem uma fronteira comum:** descartadas porque espalhariam lógica de tradução e tratamento de falhas por vários subdomínios.

## Consequências

**Positivas:** mudanças externas ficam concentradas nos adaptadores; as regras de domínio permanecem independentes dos terceiros; integrações podem ser substituídas e testadas isoladamente; e as interações externas tornam-se mais rastreáveis.

**Negativas:** cada integração exige manutenção de seu próprio adaptador; transformações entre modelos aumentam a quantidade de código; e alterações incompatíveis nos contratos externos ainda exigem atualização dos adaptadores.