from models.transacao import Categoria
from controllers.db_controller import DbController
from controllers.log_controller import LogController


class CategoryController:
    def __init__(self, dbController: DbController, logController: LogController):
        self.__dbC = dbController
        self.__lgC = logController

    def alterar_status_verba(self, nome: str, status: bool, nome_usuario: str) -> tuple[bool, str]:
        if not self.__dbC.checa_categoria_existe(nome):
            return False, f"Categoria de nome: '{nome}' não foi encontrada"

        self.__dbC.alterna_status_categoria(nome, status)
        acao_str = "Bloqueou" if status else "Liberou"
        self.__lgC.registrar_log("STATUS_VERBA", f"{acao_str} verba da categoria '{nome}'.", nome_usuario)
        self.__dbC.salvar_dados()
        return True, "Status alterado com sucesso"

    def adicionar_categoria(self, nome: str, limite: float, nome_usuario: str) -> tuple[bool, str]:
        if self.__dbC.checa_categoria_existe(nome):
            return False, f"Categoria de nome: '{nome}' já existe"

        cat = Categoria(nome, limite)
        self.__dbC.adiciona_categoria(nome, cat)
        self.__lgC.registrar_log("CRIAR_CATEGORIA", f"Categoria '{nome}' criada com limite R${limite:.2f}.",
            nome_usuario)
        self.__dbC.salvar_dados()
        return True, f"Categoria de nome: '{nome}' criada com sucesso"

    def editar_categoria(self, nome_antigo: str, novo_nome: str, novo_limite: float, nome_usuario: str) -> tuple[bool, str]:
        if not self.__dbC.checa_categoria_existe(nome_antigo):
            return False, f"Categoria de nome: '{nome_antigo}' não foi encontrada"

        if novo_nome != nome_antigo and self.__dbC.checa_categoria_existe(novo_nome):
            return False, f"Já existe uma categoria de nome: '{novo_nome}'"

        cat = self.__dbC.pop_categoria(nome_antigo)
        cat.nome = novo_nome
        cat.limite_verba = novo_limite
        self.__dbC.adiciona_categoria(novo_nome, cat)

        # Atualiza histórico de transações atreladas à categoria
        self.__dbC.atualiza_historico_categorias(nome_antigo, novo_nome)

        log_descricao = f"Categoria '{nome_antigo}' renomeada/alterada para '{novo_nome}' com teto R${novo_limite:.2f}."
        self.__lgC.registrar_log("EDITAR_CATEGORIA", log_descricao, nome_usuario)
        self.__dbC.salvar_dados()
        return True, f"Categoria de nome: '{novo_nome}' editada com sucesso"

    def deletar_categoria(self, cat_nome: str, nome_usuario: str) -> tuple[bool, str]:
        if not self.__dbC.checa_categoria_existe(cat_nome):
            return False, f"Não foi possível encontrar uma categoria de nome: '{cat_nome}'"

        self.__dbC.remove_categoria(cat_nome)
        self.__lgC.registrar_log("DELETAR_CATEGORIA", f"Categoria '{cat_nome}' removida.", nome_usuario)
        self.__dbC.salvar_dados()
        return True, f"Categoria de nome: '{cat_nome}' deletada com sucesso"
