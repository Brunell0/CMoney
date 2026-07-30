from controllers.db_controller import DbController
from controllers.log_controller import LogController


class LoginController:
    def __init__(self, dbController: DbController, logController: LogController):
        self.__dbC = dbController
        self.__lgC = logController

    def login(self, username: str, senha: str) -> tuple[bool, str]:
        if not self.__dbC.checa_usuario_existe(username):
            return False, f"Usuário: {username} não encontrado"

        user = self.__dbC.encontra_usuario(username)
        if user.password != senha:
            return False, "Senha incorreta"

        self.__lgC.registrar_log("LOGIN", f"Usuário '{username}' iniciou sessão.", username)
        return True, f"Bem-vindo(a), {username}!"
