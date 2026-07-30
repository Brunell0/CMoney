from typing import Dict
from models.usuario import Usuario
from models.transacao import Transacao, Categoria
from models.database_models import RegistroLog, ItemCompra


class Db:
    """
    Armazena em memória todas as coleções de dados da aplicação.

    Os atributos são privados (name-mangled) para impedir que outras
    classes os sobrescrevam por acidente; o acesso às coleções deve
    sempre passar pelo DbController, que é o único responsável por
    manipular o Db diretamente (via estas properties públicas).
    """

    def __init__(self):
        self.__usuarios: Dict[str, Usuario] = {}
        self.__categorias: Dict[str, Categoria] = {}
        self.__transacoes: Dict[int, Transacao] = {}
        self.__lista_compras: Dict[int, ItemCompra] = {}
        self.__logs: Dict[int, RegistroLog] = {}

    @property
    def usuarios(self) -> Dict[str, Usuario]:
        return self.__usuarios

    @property
    def categorias(self) -> Dict[str, Categoria]:
        return self.__categorias

    @property
    def transacoes(self) -> Dict[int, Transacao]:
        return self.__transacoes

    @property
    def lista_compras(self) -> Dict[int, ItemCompra]:
        return self.__lista_compras

    @property
    def logs(self) -> Dict[int, RegistroLog]:
        return self.__logs
