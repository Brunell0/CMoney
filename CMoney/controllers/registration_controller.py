from models.usuario import Usuario
from controllers.db_controller import DbController
from controllers.log_controller import LogController


class RegistrationController:
    def __init__(self, dbController: DbController, logController: LogController):
        self.__dbC = dbController
        self.__lgC = logController

    def registrar_usuario(self, username: str, senha: str, perfil: str) -> tuple[bool, str]:
        if self.__dbC.checa_usuario_existe(username):
            return False, "Este nome de usuário não está disponível"

        novo_usuario = Usuario(username, senha, perfil)
        self.__dbC.adiciona_usuario(username, novo_usuario)
        self.__lgC.registrar_log("CRIAR_USUÁRIO", f"Usuário: '{username}' criado", username)
        self.__dbC.salvar_dados()
        return True, f"Usuário: '{username}' criado com sucesso"

    def remover_usuario(self, usuario_alvo: str, nome_usuario: str) -> tuple[bool, str]:
        if not self.__dbC.checa_usuario_existe(usuario_alvo):
            return False, f"Usuário: '{usuario_alvo}' não foi encontrado"

        self.__dbC.remove_usuario(usuario_alvo)
        self.__lgC.registrar_log("DELETAR_USUÁRIO", f"Usuário: '{usuario_alvo}' deletado", nome_usuario)
        self.__dbC.salvar_dados()
        return True, f"Usuário: '{usuario_alvo}' removido com sucesso"
