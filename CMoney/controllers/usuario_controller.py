from models.usuario import Usuario
from typing import Dict
from models.db import Db

class usuarioController:

    def __init__(self, db: Db):
        self.__db = db
        self.__usuarioAtual: Usuario = None

    def registrar_usuario(self, username: str, senha: str, perfil: str) -> bool:
            if username in self.__db.__usuarios:
                return False
            