from models.transacao import Categoria
from controllers.Log_controller import LogController
from controllers.Db_controller import DbController

class CategoryController:
    def __init__(self, dbController: DbController, logController: LogController):
        self.__dbC = dbController
        self.__lgC = logController

    def adicionar_categoria(self, nome: str, limite: float): # precisa receber o user
        if nome not in self.__dbC.__db.__categorias:
            self.__dbC.__db.__categorias[nome] = Categoria(nome, limite)
            self.__lgC.registrar_log("CRIAR_CATEGORIA", f"Categoria '{nome}' criada com limite R${limite:.2f}.")
            self.__dbC.salvar_dados()
    
    def editar_categoria(self, nome_antigo: str, novo_nome: str, novo_limite: float): # precisa receber o user
        if nome_antigo in self.categorias:
            cat = self.__dbC.__db.__categorias.pop(nome_antigo)
            cat.nome = novo_nome
            cat.limite_verba = novo_limite
            self.__dbC.__db.__categorias[novo_nome] = cat
            # Atualiza histórico de transações atreladas à categoria
            if nome_antigo != novo_nome:
                for t in self.__dbC.__db.__transacoes.values():
                    if t.categoria == nome_antigo:
                        t.categoria = novo_nome

            logDescription = f"Categoria '{nome_antigo}' renomeada/alterada para '{novo_nome}' com teto R${novo_limite:.2f}."

            self.__lgC.registrar_log("EDITAR_CATEGORIA", logDescription)
            self.__dbC.salvar_dados()

    def deletar_categoria(self, nome: str): # precisa receber o user
        if nome in self.__dbC.__db.__categorias:
            del self.__dbC.__db.__categorias[nome]

            self.__lgC.registrar_log("DELETAR_CATEGORIA", f"Categoria '{nome}' removida.")
            self.__dbC.salvar_dados()