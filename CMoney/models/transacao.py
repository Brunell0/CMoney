from datetime import datetime

class Categoria:
    def __init__(self, nome: str, limite_verba: float = 5000.0, bloqueada: bool = False):
        self.nome: str = nome
        self.limite_verba: float = limite_verba
        self.bloqueada: bool = bloqueada

    def to_dict(self) -> dict:
        return {"nome": self.nome, "limite_verba": self.limite_verba, "bloqueada": self.bloqueada}

class Transacao:
    def __init__(self, id_transacao: int, descricao: str, valor: float, categoria: str, data: str = None):
        self.id: int = id_transacao
        self.descricao: str = descricao
        self._valor: float = abs(valor) # Protected
        self.categoria: str = categoria
        self.data: str = data if data else datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def calcular_impacto(self) -> float:
        raise NotImplementedError("Subclasses devem implementar este método.")
    
    @property
    def valor(self):
        return self._valor

    def to_dict(self) -> dict:
        return {
            "id": self.id, "tipo": self.__class__.__name__, "descricao": self.descricao,
            "valor": self._valor, "categoria": self.categoria, "data": self.data
        }

class Receita(Transacao):
    def calcular_impacto(self) -> float:
        return self._valor

class Despesa(Transacao):
    def calcular_impacto(self) -> float:
        return -self._valor