from datetime import datetime

class ItemCompra:
    def __init__(self, id: int, nome: str, quantidade: int, estimado: float, comprado: bool = False):
        self.id: int = id
        self.nome: str = nome
        self.quantidade: int = quantidade
        self.estimado: float = estimado
        self.comprado: bool = comprado

    def to_dict(self) -> dict:
        return {"id": self.id, "nome": self.nome, "quantidade": self.quantidade, "estimado": self.estimado, "comprado": self.comprado}

# CLASSE DE LOG 
class RegistroLog:
    def __init__(self, id_log: int, usuario: str, acao: str, detalhes: str, datahora: str = None):
        self.id = id_log
        self.usuario = usuario
        self.acao = acao
        self.detalhes = detalhes
        self.datahora = datahora if datahora else datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usuario": self.usuario,
            "acao": self.acao,
            "detalhes": self.detalhes,
            "datahora": self.datahora
        }