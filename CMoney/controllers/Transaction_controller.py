from typing import List
from models.transacao import Transacao, Receita, Despesa
from controllers.Log_controller import LogController
from controllers.Db_controller import DbController

class TransactionController:
    def __init__(self, dbController: DbController, logController: LogController):
        self.__lgC = logController
        self.__dbC = dbController
        self.proximo_id_transacao = 1

    def criar_transacao(self, tipo: str, descricao: str, valor: float, categoria_nome: str) -> tuple:
        cat = self.__dbC.__db.__categorias.get(categoria_nome)
        if not cat:
            return False, "Categoria não existe."
            
        if tipo == "Despesa":
            if cat.bloqueada:
                return False, "ERRO: Verba bloqueada para esta categoria!"
            
            # Soma tudo o que já gastou nessa categoria específica
            total_gasto = sum(t.valor for t in self.__dbC.__db.__transacoes.values() 
                if t.__class__.__name__ == "Despesa" and t.categoria == categoria_nome)
            
            # Checa se o novo valor estoura o limite de verba
            if total_gasto + valor > cat.limite_verba:
                errorMessage = (
                    f"ERRO: Esta despesa excede o teto da categoria!\nLimite: R$ {cat.limite_verba:.2f}"
                    f"\nJá gasto: R$ {total_gasto:.2f}\nDisponível: R$ {cat.limite_verba - total_gasto:.2f}"
                )

                return False, errorMessage
        
        t = Receita(self.proximo_id_transacao, descricao, valor, categoria_nome
            ) if tipo == "Receita" else Despesa(self.proximo_id_transacao, descricao, valor, categoria_nome)


        self.__dbC.__db.__transacoes[t.id] = t
        self.proximo_id_transacao += 1
        
        # Repassa a para as funções dos outros controllers
        self.__lgC.registrar_log("CRIAR_TRANSACAO", f"{tipo}: R${valor:.2f} em {categoria_nome} ({descricao}).")
        self.__dbC.salvar_dados()

        return True, "Transação criada com sucesso"

    def atualizar_transacao(self, id_t: int, tipo: str, descricao: str, valor: float, categoria_nome: str) -> bool:
        if id_t not in self.transacoes: return False
        cat = self.__dbC.__db.__categorias.get(categoria_nome)
        
        if tipo == "Despesa" and cat:
            if cat.bloqueada: return False
            
            # Soma o gasto dos outros registros (ignorando o que está sendo editado agora)
            total_gasto = sum(t.valor for t in self.transacoes.values() if t.__class__.__name__ == "Despesa" 
                and t.categoria == categoria_nome and t.id != id_t)
            
            if total_gasto + valor > cat.limite_verba:
                return False # Vai disparar o bloco except/erro na View

        if tipo == "Receita":
            t = Receita(id_t, descricao, valor, categoria_nome)
            self.__db.__transacoes[id_t] = t
        elif tipo == "Despesa":
            t = Despesa(id_t, descricao, valor, categoria_nome)
            self.__db.__transacoes[id_t] = t

        self.__lg.registrar_log("EDITAR_TRANSACAO", f"ID {id_t} alterado para {tipo} de R${valor:.2f} em {categoria_nome}.")
        self.__dbC.salvar_dados()

        return True
        
    def listar_transacoes(self) -> List[Transacao]:
        return list(self.transacoes.values())

    def atualizar_transacao(self, id_t: int, tipo: str, descricao: str, valor: float, categoria_nome: str) -> bool:
        if id_t not in self.transacoes: return False
        t = Receita(id_t, descricao, valor, categoria_nome) if tipo == "Receita" else Despesa(id_t, descricao, valor, categoria_nome)
        self.transacoes[id_t] = t
        self.registrar_log("EDITAR_TRANSACAO", f"ID {id_t} alterado para {tipo} de R${valor:.2f} em {categoria_nome}.")
        self.salvar_dados()
        return True

    def deletar_transacao(self, id_t: int) -> bool:
        if id_t in self.transacoes:
            t = self.transacoes[id_t]
            self.registrar_log("DELETAR_TRANSACAO", f"Transação ID {id_t} ({t.descricao}) removida.")
            del self.transacoes[id_t]
            self.salvar_dados()
            return True
        return False

    def calcular_saldo(self) -> float:
        return sum(t.calcular_impacto() for t in self.transacoes.values())