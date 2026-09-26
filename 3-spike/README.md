# Spike: Destruição Criptográfica (Crypto-shredding) vs Trilha de Auditoria
**ADR Comprovado:** ADR/0005-crypto-shredding-lgpd.md

**O que este código prova:** 
Este spike demonstra a viabilidade de manter um banco de dados imutável (*Event Sourcing*) para auditorias financeiras rigorosas, enquanto cumpre integralmente o direito ao esquecimento exigido pela LGPD. 
Ele prova que, ao cifrar os dados sensíveis do passageiro (PII) no evento e guardar a chave em um repositório isolado, a exclusão exclusiva da chave anonimiza irreversivelmente a viagem sem alterar os valores e registros financeiros totais. 

**Como rodar:**
Certifique-se de ter o Python 3.12 instalado. Nenhuma biblioteca externa é necessária. Execute no terminal:
`python3 exemplo.py`

**O que aconteceria se a decisão estivesse errada:**
Se optássemos por uma exclusão física tradicional (CRUD/`DELETE`) para atender à LGPD, o evento da viagem sumiria da base. 
Ao recalcular o repasse mensal ou em uma auditoria do Tribunal de Contas, a soma de tarifas validadas não bateria com o dinheiro arrecadado, configurando indício de fraude e quebrando o requisito principal do Envelope E. 
Por outro lado, se não apagássemos os dados para preservar a auditoria financeira, o consórcio enfrentaria multas milionárias por descumprimento da legislação de privacidade.