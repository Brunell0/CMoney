from models.database_models import RegistroLog
from controllers.db_controller import DbController


class LogController:
    def __init__(self, dbController: DbController):
        self.__dbC = dbController
        self.proximo_id_log = 1

    def registrar_log(self, acao: str, detalhes: str, username: str):
        log = RegistroLog(self.proximo_id_log, username, acao, detalhes)
        self.__dbC.adiciona_logs(log.id, log)
        self.proximo_id_log += 1
