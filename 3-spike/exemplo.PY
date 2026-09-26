from datetime import datetime

# ==========================================
# 1. SERVIÇOS DE DADOS E ARMAZENAMENTO
# ==========================================

class CadastroPessoalService:
    """Mantém os dados pessoais (PII) fora do armazenamento imutável."""
    def __init__(self):
        self._banco_dados = {}

    def registrar_passageiro(self, usuario_id: str, nome: str, cpf: str):
        self._banco_dados[usuario_id] = {"nome": nome, "cpf": cpf}

    def obter_dados(self, usuario_id: str) -> dict:
        return self._banco_dados.get(usuario_id, {"nome": "<ANONIMIZADO (LGPD)>", "cpf": "<ANONIMIZADO>"})

    def eliminar_dados_lgpd(self, usuario_id: str):
        """Apaga definitivamente os dados pessoais associados ao identificador."""
        if usuario_id in self._banco_dados:
            del self._banco_dados[usuario_id]
            return True
        return False

class EventStoreFinanceiro:
    """Armazenamento imutável (append-only) contendo apenas o histórico de transações."""
    def __init__(self):
        self.eventos = []

    def registrar_evento(self, evento: dict):
        self.eventos.append(evento)
        
    def obter_fita_do_tempo(self):
        return self.eventos

# ==========================================
# 2. PROJEÇÃO E CONCILIAÇÃO (IDEMPOTENTE)
# ==========================================

class ProjecaoConciliacao:
    """Projeção construída a partir da leitura dos eventos, com tratamento de duplicidade."""
    def __init__(self):
        self.eventos_processados = set()
        self.saldo_arrecadado = 0.0
        self.viagens_contabilizadas = 0

    def projetar_fita(self, eventos: list):
        for evt in eventos:
            # Garante idempotência: se o evento já foi processado, ignora
            if evt["evento_id"] not in self.eventos_processados:
                self.saldo_arrecadado += evt["valor_tarifa"]
                self.viagens_contabilizadas += 1
                self.eventos_processados.add(evt["evento_id"])

# ==========================================
# 3. LÓGICA DE NEGÓCIO E APLICAÇÃO
# ==========================================

cadastro = CadastroPessoalService()
event_store = EventStoreFinanceiro()

def simular_validação_catraca(usuario_id: str, valor: float):
    """Gera o evento de viagem sem gravar os dados pessoais, apenas a referência."""
    evento = {
        "evento_id": f"evt_bus_{len(event_store.obter_fita_do_tempo())+1:05d}",
        "timestamp": datetime.now().isoformat(),
        "tipo_evento": "TarifaDebitada",
        "usuario_id_ref": usuario_id, 
        "valor_tarifa": valor
    }
    event_store.registrar_evento(evento)
    print(f"-> Viagem registrada: {evento['evento_id']} | Tarifa: R$ {valor:.2f}")

def gerar_relatorio_auditoria(projecao: ProjecaoConciliacao):
    """Cruza o histórico imutável com o banco de cadastro para prestação de contas."""
    print("\n" + "="*65)
    print("RELATÓRIO DE AUDITORIA DO TRIBUNAL DE CONTAS")
    print("="*65)
    
    for evt in event_store.obter_fita_do_tempo():
        # Tenta buscar os dados pessoais, se ainda existirem
        dados_pessoais = cadastro.obter_dados(evt["usuario_id_ref"])
        
        print(f"[{evt['evento_id']}] R$ {evt['valor_tarifa']:.2f} | Ref: {evt['usuario_id_ref']}")
        print(f"    Passageiro: {dados_pessoais['nome']} (CPF: {dados_pessoais['cpf']})")
    
    print("-" * 65)
    print(f">> TOTAL CONCILIADO: R$ {projecao.saldo_arrecadado:.2f} ({projecao.viagens_contabilizadas} viagens)")
    print("=" * 65 + "\n")

# ==========================================
# 4. EXECUÇÃO DO CENÁRIO EXIGIDO PELO ADR
# ==========================================

if __name__ == "__main__":
    # 1. Registrar passageiros (fora do armazenamento imutável)
    cadastro.registrar_passageiro("usr_001", "Alice Silva", "111.111.111-11")
    cadastro.registrar_passageiro("usr_002", "Bob Souza", "222.222.222-22")

    print("CENÁRIO A: Processamento inicial das viagens")
    simular_validação_catraca("usr_001", 4.50)
    simular_validação_catraca("usr_002", 4.50)
    simular_validação_catraca("usr_001", 4.50)
    
    projecao = ProjecaoConciliacao()
    projecao.projetar_fita(event_store.obter_fita_do_tempo())
    gerar_relatorio_auditoria(projecao)
    
    # 2. Exclusão LGPD
    print("CENÁRIO B: Solicitação de Direito ao Esquecimento (LGPD)")
    print("-> Apagando dados pessoais do usuário usr_001...")
    cadastro.eliminar_dados_lgpd("usr_001")
    
    # 3. Reprocessamento com Idempotência
    print("\nCENÁRIO C: Reprocessamento e Auditoria pós-LGPD")
    print("-> Injetando os mesmos eventos na projeção para testar idempotência...")
    
    # Repassa a mesma fita de eventos para a projeção existente
    projecao.projetar_fita(event_store.obter_fita_do_tempo())
    
    # Adiciona uma nova viagem para outro usuário para provar que a projeção continua ativa
    simular_validação_catraca("usr_002", 4.50)
    projecao.projetar_fita(event_store.obter_fita_do_tempo())
    
    gerar_relatorio_auditoria(projecao)