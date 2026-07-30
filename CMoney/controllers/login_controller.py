from models.db import Db
from models.usuario import Usuario
from controllers.Db_controller import DbController
from controllers.Log_controller import LogController

class LoginController:
    def __init__(self, dbController: DbController, logController: LogController):
        self.__dbC = dbController
        self.__lgC = logController

    def login(self, username: str, senha: str) -> tuple[bool, str]:
        if not self.__dbC.checa_usuario_existe(username): return False, f"Usuário: {username} não encontrado"
        user = self.__dbC.encontra_usuario(username)
        if user and user.password == senha:
            self.__lgC.registrar_log("LOGIN", f"Usuário '{username}' iniciou sessão.")
            return True, username