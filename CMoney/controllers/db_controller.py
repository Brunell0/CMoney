import json
from models.db import Db

class DbController:
    def __init__(self, db: Db, db_path: str = "banco_dados.json"):
        self.__db_path = db_path
        self.__db = db

    # função para escrever no arquivo banco_dados.json
    def salvar_dados(self):
        data = {
            "categorias": [c.to_dict() for c in self.__db.__categorias.values()],
            "transacoes": [t.to_dict() for t in self.__db.__transacoes.values()],
            "lista_compras": [i.to_dict() for i in self.__db.__listaCompras.values()],
            "logs": [l.to_dict() for l in self.__db.__logs.values()],
            "usuarios": {u.username: u.to_dict() for u in self.__db.__usuarios.values()}
        }
        with open(self.__db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)