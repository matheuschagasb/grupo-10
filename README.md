# Projeto Arquitetura de Software - Caso Ônibus 
 
**Caso:** Sistema de Bilhetagem Eletrônica e Telemetria de Ônibus   
**Envelope:** E - Operação fiscalizada (Tribunal de Contas e LGPD)   

---

## Contexto

O órgão gestor do transporte da cidade vai substituir o sistema de bilhetagem eletrônica. O sistema atual, contratado há mais de dez anos, é um monolito fechado de um fornecedor, com banco central e validadores que só funcionam com rede. O novo sistema precisa cobrir a validação da passagem no ônibus, os cartões e recargas, a telemetria da frota, a informação ao passageiro e o repasse financeiro entre operadoras e prefeitura.

**Quem usa:** Passageiro; motorista; operadora de ônibus (várias empresas em consórcio); órgão gestor (regula, fiscaliza e reparte a receita); pontos de recarga (lojas, aplicativo, totens); banco e adquirente de cartão; auditoria externa.

## Premissas de dimensionamento

| Premissa | Valor adotado |
|---|---|
| Frota | 1.200 ônibus, cada um com um validador embarcado |
| Validações | 900 mil por dia útil; pico de 120 por segundo entre 6h30 e 8h30 |
| Cartões ativos | 2,5 milhões, sendo 25% com gratuidade ou desconto (estudante, idoso, pessoa com deficiência) |
| Recargas | 150 mil por dia, por aplicativo, loja e totem |
| Telemetria | posição GPS de cada ônibus a cada 15 segundos |
| Rede no ônibus | 4G intermitente; um ônibus pode ficar até 4 horas sem conexão em partes do trajeto |
| Repasse financeiro | fechamento mensal por operadora, auditado, com contestação em até 30 dias |
| Guarda de dados | histórico de viagens do passageiro identificado é dado pessoal sob a LGPD |

## Subdomínios e a natureza de cada um

| Subdomínio | O que faz | Natureza | Requisito que aperta |
|---|---|---|---|
| Validação embarcada | aceita ou recusa a passagem no ônibus | tempo real, alto volume, sem rede | resposta em até 300 ms mesmo sem conexão; nunca aceitar a mesma passagem duas vezes |
| Cartões e recarga | saldo, recarga, bloqueio, gratuidades | transacional, envolve dinheiro | saldo consistente; fraude de recarga zero; conciliação com o banco |
| Telemetria da frota | recebe posições e estado dos veículos | fluxo contínuo | absorver 80 posições por segundo em média e 5 vezes isso em pico sem perder dados |
| Informação ao passageiro | previsão de chegada, aplicativo, painéis | analítico, tolera atraso de segundos | pico de acessos no horário de rush; custo baixo fora do pico |
| Repasse e conciliação | calcula o que cada operadora recebe | lote mensal, auditável | recalcular o mês inteiro com regras vigentes na data de cada viagem |
| Integração externa | órgão gestor, operadoras, banco, adquirente | contratos formais, legado | formatos impostos por terceiros; janelas de indisponibilidade |
| Atendimento | segunda via, contestação, cadastro de gratuidade | transacional, baixo volume | trilha de auditoria de quem alterou o quê |

---

## Envelope E

**Situação e equipe:** Operação sob fiscalização de órgão regulador. 15 desenvolvedores, 1 responsável por conformidade.

**Dinheiro e infraestrutura:** Nuvem pública com exigência de trilha de auditoria completa.

**Exigência que domina:** Tudo o que acontece precisa ser reconstruível; LGPD com direito ao esquecimento.

**A pergunta que o envelope obriga a responder:** Como vocês guardam tudo para sempre e ainda assim apagam o que a lei manda apagar?

## Detalhes por caso - Ônibus E

A auditoria é do tribunal de contas sobre o repasse financeiro.

---

## Integrantes (Grupo 10):
- Eduardo Freitas - RA: 24008082
- Guilherme Santos - RA: 24015942
- Matheus Chagas - RA: 24015048
- Rafael Cespedes - RA: 24013307
- Thiago Mauri - RA: 24015357

---

## Como Navegar no Repositório
- `1-matriz/`: Contém a análise dos 12 estilos arquiteturais e sua aderência ao nosso caso e envelope.
- `2-arquitetura/`: Contém os diagramas C4 (Contexto, Contêineres e Componentes), o mapa de restrições vs. decisões, os 5 ADRs e as respostas às perguntas obrigatórias do domínio.
- `3-spike/`: Prova de conceito (código executável) focada na resolução do conflito entre trilha de auditoria e exclusão de dados (LGPD) usando Crypto-Shredding.
- `4-leitura-cruzada/`: Objeções enviadas a outro grupo e nossas respostas às críticas recebidas.
- `5-final/`: Changelog consolidando as mudanças arquiteturais após a leitura cruzada.
