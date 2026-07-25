from models.db import Db
from models.usuario import Usuario

class LoginController: # precisa receber __dbC como os outros controllers
    def __init__(self, db: Db):
        self.__db = db
        self.__usuarioAtual: Usuario = None

    def login(self, username: str, senha: str) -> tuple[bool, str]: # incompleto 
        # deverá devolver o nome do usuário para o sistema
        user = self.__db.__usuarios.get(username) # encontra usuario pelo nome
        if user and user.password == senha: # checa senha
            self.__usuario_atual = user
            self.registrar_log("LOGIN", f"Usuário '{username}' iniciou sessão.")
            return True
        return False