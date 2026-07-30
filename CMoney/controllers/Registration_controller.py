from models.usuario import Usuario
from typing import Dict
from Db_controller import DbController
from Log_controller import LogController

class RegistrationController:
    def __init__(self, dbController: DbController, logController: LogController):
        self.__dbC = dbController
        self.__lgC = logController
        
    def registrar_usuario(self, username: str, senha: str, perfil: str) -> tuple[bool, str]:
        if self.__dbC.checa_usuario_existe(username):
            return False, "Este nome de usuário não está disponível"
        else:
            newUser = Usuario(username, senha, perfil)
            self.__dbC.adiciona_usuario(username, newUser)
            self.__lgC.registrar_log("CRIAR_USUÁRIO", f"Usuário: '{username}' criado", username)
            self.__dbC.salvar_dados()
            return True, f"Usuário: '{username}' criado com sucesso"

    def remover_usuario(self, userToRemove: str, nome_usuario: str):
        if self.__dbC.checa_usuario_existe(userToRemove):
            self.__dbC.remove_usuario(userToRemove)
            self.__lgC.registrar_log("DELETAR_USUÁRIO", f"Usuário: '{userToRemove}' deletado", nome_usuario)
            self.__dbC.salvar_dados()