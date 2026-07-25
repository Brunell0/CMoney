from typing import Dict
from models.usuario import Usuario
from models.transacao import Transacao, Categoria
from models.database_models import RegistroLog, ItemCompra

class Db:
    def __init__(self):
        self.__usuarios
        self.__logs = Dict[int, RegistroLog] = {}
        self.__usuarios = Dict[str, Usuario] = {}
        self.__categorias = Dict[str, Categoria] = {}
        self.__transacoes = Dict[int, Transacao] = {}
        self.__listaCompras = Dict[int, ItemCompra] = {}