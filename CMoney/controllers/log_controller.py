from models.database_models import RegistroLog

class logController:
    def __int__(self):
        self.proximo_id_log = 1

    def registrar_log(self, acao: str, detalhes: str, user: str):
            log = RegistroLog(self.proximo_id_log, user, acao, detalhes)
            self.__logs[log.id] = log # enviará pro db 
            self.proximo_id_log += 1