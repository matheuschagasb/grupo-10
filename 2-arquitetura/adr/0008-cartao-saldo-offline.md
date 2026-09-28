# ADR 0008: gravar no cartão o saldo operacional e a sequência de uso

**Status:** aceito

**Contexto:** O ônibus fica até 4 h sem rede, e dois ônibus offline podem receber o mesmo cartão. Uma cópia do saldo central em cada validador ficaria desatualizada, e a mesma passagem nunca pode ser aceita duas vezes. Uma recarga feita no aplicativo precisa chegar a um cartão que só é lido por validadores que podem estar offline.

**Decisão:** Gravar no cartão o saldo operacional e um número de sequência incrementado a cada uso, de modo que o segundo ônibus leia o estado já atualizado; ao sincronizar, Cartões e Recarga detecta sequências repetidas vindas de validadores diferentes e emite evento de divergência. A recarga do aplicativo fica como crédito pendente no backend e é gravada no cartão no primeiro uso em um validador que já sincronizou a lista de pendências.

**Alternativas consideradas:**
- Cópia do saldo central em cada validador: descartada porque ônibus offline gastariam o mesmo saldo desatualizado.
- Exigir conexão para validar: descartado porque viola os 300 ms e as 4 h offline.
- Detectar duplicidade só por idempotência: descartada porque ela trata reenvio da mesma mensagem, não o uso do mesmo cartão em dois ônibus.

**Consequências:**
- Positivas: a validação continua offline; o segundo ônibus vê o gasto do primeiro pelo próprio cartão; o uso duplo por adulteração é detectado e tratado.
- Negativas: o cartão passa a ser parte da base de confiança e seu estado precisa de assinatura contra adulteração; a recarga do aplicativo pode demorar até o primeiro uso em validador sincronizado; a segunda via exige reconciliar o saldo com o backend.

**Fontes:** ABREU (2026): §7.2 (portas e adaptadores), §11.2 (idempotência). Premissas de dimensionamento e requisitos do caso Ônibus (enunciado "Um problema, cinco realidades").
