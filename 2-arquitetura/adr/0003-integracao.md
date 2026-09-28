# ADR 0003: isolar terceiros e legado em adaptadores por porta

**Status:** aceito

**Contexto:** Banco, adquirente, operadoras e o sistema legado impõem formatos e janelas de indisponibilidade. O legado do fornecedor atual só expõe um banco de leitura e arquivos de texto diários. A fraude de recarga deve ser zero e cada recarga deve ser conciliada com o banco.

**Decisão:** Cada sistema externo tem um adaptador que traduz seu contrato para uma porta do domínio, as regras dependem só das portas, e a recarga só é creditada depois que o adaptador do banco confirma a liquidação. O legado é lido apenas por adaptador, em modo somente leitura, inclusive na importação do histórico em lote.

**Alternativas consideradas:**
- Integração direta no domínio: descartada por acoplar as regras a contratos de terceiros.
- ESB obrigatório: descartado por acrescentar latência e um ponto central de falha sem necessidade comprovada.
- Ponto a ponto sem fronteira comum: descartado porque espalha tradução e tratamento de falha pelos subdomínios.
- Creditar a recarga antes da liquidação: descartado porque abre espaço para fraude.

**Consequências:**
- Positivas: mudanças externas ficam nos adaptadores; falhas de terceiros ficam contidas; recarga só entra com liquidação confirmada.
- Negativas: um adaptador por integração para manter; o passageiro espera a confirmação do banco para ver o crédito; se o banco cair, a recarga fica pendente até o reenvio.

**Fontes:** ABREU (2026): §7.2 (portas e adaptadores), §10.6 e §10.7 (ESB), §19.3 (camada anticorrupção). Premissas de dimensionamento e requisitos do caso Ônibus (enunciado "Um problema, cinco realidades").
