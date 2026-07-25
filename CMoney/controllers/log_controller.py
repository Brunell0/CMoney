from models.database_models import RegistroLog
from controllers.Db_controller import DbController

class LogController:
    def __int__(self, dbController: DbController):
        self.__dbC = dbController
        self.proximo_id_log = 1

    def registrar_log(self, acao: str, detalhes: str, user: str):
        log = RegistroLog(self.proximo_id_log, user, acao, detalhes)
        self.__dbC.__db.__logs[log.id] = log 
        self.proximo_id_log += 1