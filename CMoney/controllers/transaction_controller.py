from models.transacao import Receita, Despesa
from controllers.db_controller import DbController
from controllers.log_controller import LogController


class TransactionController:
    def __init__(self, dbController: DbController, logController: LogController):
        self.__lgC = logController
        self.__dbC = dbController
        self.proximo_id_transacao = 1

    def criar_transacao(self, tipo: str, descricao: str, valor: float,
            categoria_nome: str, nome_usuario: str) -> tuple[bool, str]:
        cat = self.__dbC.encontra_categoria(categoria_nome)
        if not cat:
            return False, "Categoria não existe."

        if tipo == "Despesa":
            if cat.bloqueada:
                return False, "ERRO: Verba bloqueada para esta categoria!"

            # Soma tudo o que já foi gasto nessa categoria específica
            total_gasto = self.calcula_total_gasto(categoria_nome)

            # Checa se o novo valor estoura o limite de verba
            if total_gasto + valor > cat.limite_verba:
                errorMessage = (
                    f"ERRO: Esta despesa excede o teto da categoria!\nLimite: R$ {cat.limite_verba:.2f}"
                    f"\nJá gasto: R$ {total_gasto:.2f}\nDisponível: R$ {cat.limite_verba - total_gasto:.2f}"
                )
                return False, errorMessage

        t = Receita(self.proximo_id_transacao, descricao, valor, categoria_nome
            ) if tipo == "Receita" else Despesa(self.proximo_id_transacao, descricao, valor, categoria_nome)

        self.__dbC.adiciona_transacao(t.id, t)
        self.proximo_id_transacao += 1

        self.__lgC.registrar_log("CRIAR_TRANSACAO",
            f"{tipo}: R${valor:.2f} em {categoria_nome} ({descricao}).",
            nome_usuario)

        self.__dbC.salvar_dados()
        return True, "Transação criada com sucesso"

    def atualizar_transacao(self, id_t: int, tipo: str, descricao: str, valor: float,
            categoria_nome: str, nome_usuario: str) -> bool:
        # A transação precisa existir para poder ser atualizada.
        if not self.__dbC.checa_transacao_existe(id_t):
            return False

        cat = self.__dbC.encontra_categoria(categoria_nome)
        if not cat:
            return False

        if tipo == "Despesa":
            if cat.bloqueada:
                return False

            # Soma o gasto das demais despesas da categoria, ignorando a
            # própria transação que está sendo editada (para não contar 2x).
            total_gasto = self.calcula_total_gasto(categoria_nome, ignorar_id=id_t)

            if total_gasto + valor > cat.limite_verba:
                return False  # Vai disparar o bloco de erro na View

        if tipo == "Receita":
            t = Receita(id_t, descricao, valor, categoria_nome)
        else:
            t = Despesa(id_t, descricao, valor, categoria_nome)

        self.__dbC.adiciona_transacao(id_t, t)

        self.__lgC.registrar_log("EDITAR_TRANSACAO",
            f"ID {id_t} alterado para {tipo} de R${valor:.2f} em {categoria_nome}.",
            nome_usuario)

        self.__dbC.salvar_dados()
        return True

    def deletar_transacao(self, id_t: int, nome_usuario: str) -> tuple[bool, str]:
        if not self.__dbC.checa_transacao_existe(id_t):
            return False, f"Nenhuma transação com id: '{id_t}' foi encontrada"

        t = self.__dbC.encontra_transacao(id_t)
        self.__lgC.registrar_log("DELETAR_TRANSACAO", f"Transação ID {id_t} ({t.descricao}) removida.", nome_usuario)
        self.__dbC.remove_transacao(id_t)
        self.__dbC.salvar_dados()
        return True, f"Transação de id: '{id_t}' removida com sucesso"

    def calcular_saldo(self) -> float:
        return sum(t.calcular_impacto() for t in self.__dbC.listar_transacoes())

    def calcula_total_gasto(self, cat_nome: str, ignorar_id: int = None) -> float:
        return sum(t.valor for t in self.__dbC.listar_transacoes()
            if t.__class__.__name__ == "Despesa" and t.categoria == cat_nome and t.id != ignorar_id)
