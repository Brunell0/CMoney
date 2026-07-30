from models.database_models import ItemCompra
from controllers.Db_controller import DbController
from controllers.Log_controller import LogController

class ShoppingController:
    def __init__(self, dbController: DbController, logController: LogController):
        self.__dbC = dbController
        self.__lgC = logController

        self.proximo_id_compra = 1

    def adicionar_item_compra(self, nome: str, qtd: int, estimado: float,
            nome_usuario: str) -> tuple[bool, str]:

        item = ItemCompra(self.proximo_id_compra, nome, qtd, estimado)
        self.__dbC.adiciona_compra(item.id, item)
        self.proximo_id_compra += 1
        self.__lgC.registrar_log("CRIAR_COMPRA", f"Item '{nome}' (Qtd: {qtd}) adicionado.", nome_usuario)
        self.__dbC.salvar_dados()
        return True, "Item adicionado com sucesso"

    def editar_item_compra(self, id_item: int, nome: str, qtd: int, estimado: float,
        nome_usuario: str) -> tuple[bool, str]:

            if not self.__dbC.checa_compra_existe(id_item): 
                return False, f"Item de id: '{id_item}' não foi encontrado"
            item = self.__dbC.encontra_compra(id_item)
            item.nome = nome
            item.quantidade = qtd
            item.estimado = estimado
            self.__lgC.registrar_log("EDITAR_COMPRA", f"Item ID {id_item} atualizado para '{nome}'.", nome_usuario)
            self.__dbC.salvar_dados()
            return True, f"Item editado com sucesso"

    def deletar_item_compra(self, id_item: int, nome_usuario: str) -> tuple[bool, str]:
        if self.__dbC.checa_compra_existe(id_item):
            nome = self.__dbC.encontra_compra(id_item).nome
            self.__dbC.remove_compra(id_item)
            self.__lgC.registrar_log("DELETAR_COMPRA", f"Item '{nome}' removido.", nome_usuario)
            self.__dbC.salvar_dados()
            return True, "Item removido com sucesso"
        return False, f"Item de id: '{id_item}' não foi encontrado"

    def alternar_status(self, id_item: int, nome_usuario: str) -> tuple[bool, str]:
        if self.__dbC.checa_compra_existe(id_item):
            self.__dbC.alterna_status_compra(id_item)
            status = self.__dbC.encontra_compra_status(id_item)
            self.__lgC.registrar_log("STATUS_COMPRA", f"Item ID {id_item} alterado para {status}.", nome_usuario)
            self.__dbC.salvar_dados()
            return True, "Status alterado com sucesso"
        return False, f"Item de id: '{id_item}' não foi encontrado"