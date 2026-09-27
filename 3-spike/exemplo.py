from datetime import datetime


class CadastroPessoalService:
    def __init__(self):
        self._dados = {}

    def registrar_passageiro(self, usuario_id, nome, cpf):
        self._dados[usuario_id] = {
            "nome": nome,
            "cpf": cpf
        }

    def obter_dados(self, usuario_id):
        return self._dados.get(usuario_id)

    def eliminar_dados_lgpd(self, usuario_id):
        if usuario_id in self._dados:
            del self._dados[usuario_id]
            return True

        return False


class EventStoreFinanceiro:
    def __init__(self):
        self._eventos = []

    def registrar_evento(self, evento):
        self._eventos.append(evento)

    def obter_eventos(self):
        return tuple(self._eventos)


class ProjecaoConciliacao:
    def __init__(self):
        self.eventos_processados = set()
        self.saldo_arrecadado = 0.0
        self.viagens_contabilizadas = 0

    def processar(self, eventos):
        for evento in eventos:
            evento_id = evento["evento_id"]

            if evento_id in self.eventos_processados:
                continue

            self.saldo_arrecadado += evento["valor_tarifa"]
            self.viagens_contabilizadas += 1
            self.eventos_processados.add(evento_id)


cadastro = CadastroPessoalService()
event_store = EventStoreFinanceiro()


def registrar_viagem(usuario_id, valor):
    numero = len(event_store.obter_eventos()) + 1

    evento = {
        "evento_id": f"evt_bus_{numero:05d}",
        "timestamp": datetime.now().isoformat(),
        "tipo_evento": "TarifaDebitada",
        "usuario_id_ref": usuario_id,
        "valor_tarifa": valor
    }

    event_store.registrar_evento(evento)

    print(
        f"-> Viagem registrada: {evento['evento_id']} "
        f"| Tarifa: R$ {valor:.2f}"
    )


def exibir_relatorio(projecao):
    print("\n" + "=" * 60)
    print("RELATÓRIO DE AUDITORIA")
    print("=" * 60)

    for evento in event_store.obter_eventos():
        usuario_id = evento["usuario_id_ref"]
        dados = cadastro.obter_dados(usuario_id)

        print(
            f"[{evento['evento_id']}] "
            f"R$ {evento['valor_tarifa']:.2f} "
            f"| Ref: {usuario_id}"
        )

        if dados:
            print(
                f"    Passageiro: {dados['nome']} "
                f"(CPF: {dados['cpf']})"
            )
        else:
            print("    Dados pessoais: removidos")

    print("-" * 60)

    print(
        f"TOTAL CONCILIADO: R$ {projecao.saldo_arrecadado:.2f} "
        f"({projecao.viagens_contabilizadas} viagens)"
    )

    print("=" * 60)


if __name__ == "__main__":
    cadastro.registrar_passageiro(
        "usr_001",
        "Alice Silva",
        "111.111.111-11"
    )

    cadastro.registrar_passageiro(
        "usr_002",
        "Bob Souza",
        "222.222.222-22"
    )

    print("CENÁRIO A: processamento inicial")

    registrar_viagem("usr_001", 4.50)
    registrar_viagem("usr_002", 4.50)
    registrar_viagem("usr_001", 4.50)

    projecao_inicial = ProjecaoConciliacao()

    projecao_inicial.processar(
        event_store.obter_eventos()
    )

    exibir_relatorio(projecao_inicial)

    print("\nCENÁRIO B: eliminação dos dados pessoais")

    cadastro.eliminar_dados_lgpd("usr_001")

    print("-> Dados pessoais de usr_001 removidos.")

    print("\nCENÁRIO C: reconstrução após eliminação")

    projecao_reconstruida = ProjecaoConciliacao()

    projecao_reconstruida.processar(
        event_store.obter_eventos()
    )

    exibir_relatorio(projecao_reconstruida)

    print("\nCENÁRIO D: teste de idempotência")
    print("-> Reprocessando os mesmos eventos...")

    projecao_reconstruida.processar(
        event_store.obter_eventos()
    )

    print(
        f"TOTAL APÓS REPROCESSAMENTO: "
        f"R$ {projecao_reconstruida.saldo_arrecadado:.2f} "
        f"({projecao_reconstruida.viagens_contabilizadas} viagens)"
    )