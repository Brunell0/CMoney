import json
import os

# Import de todos os models necessários no sistema
from models.usuario import Usuario
from models.transacao import Receita, Despesa, Categoria
from models.database_models import ItemCompra, RegistroLog

# Import de todos os controllers para referenciação
from Db_controller import DbController
from Log_controller import LogController
from Login_controller import LoginController
from Category_controller import CategoryController
from Shopping_controller import ShoppingController
from Transaction_controller import TransactionController
from Registration_controller import RegistrationController

class SystemController:
    def __init__(self, 
            dbController: DbController, 
            logController: LogController,
            loginController: LoginController,
            categoryController: CategoryController,
            shoppingController: ShoppingController,
            transactionController: TransactionController,
            registrationController: RegistrationController
        ):

        self.__dbC = dbController
        self.__lgC = logController
        self.__lnC = loginController
        self.__cyC = categoryController
        self.__sgC = shoppingController
        self.__tnC = transactionController
        self.__rnC = registrationController

        self.usuario_atual: str = None
        self.carregar_dados()

    def carregar_dados(self):
        if not os.path.exists(self.__dbC.__db_path):
            self._criar_dados_padrao()
            return

        try:
            with open(self.__dbC.__db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            self._criar_dados_padrao()
            return

        for c_data in data.get("categorias", []):
            self.__dbC.__db.__categorias[c_data["nome"]] = Categoria(**c_data)
            
        for t_data in data.get("transacoes", []):

            if t_data["tipo"] == "Receita":
                t = Receita(t_data["id"], t_data["descricao"], t_data["valor"], t_data["categoria"], t_data["data"])
                if self.__dbC.checa_transacao_existe(t.id): continue
                self.__dbC.adiciona_transacao(t.id, t)
            elif t_data["tipo"] == "Despesa":
                t = Despesa(t_data["id"], t_data["descricao"], t_data["valor"], t_data["categoria"], t_data["data"]) 
                if self.__dbC.checa_transacao_existe(t.id): continue
                self.__dbC.adiciona_transacao(t.id, t)

            if t.id >= self.__tnC.proximo_id_transacao: self.__tnC.proximo_id_transacao = t.id + 1
                
        for i_data in data.get("lista_compras", []):
            item = ItemCompra(**i_data)
            if self.__dbC.checa_compra_existe(item.id): continue
            self.__dbC.adiciona_compra(item.id, item)
            if item.id >= self.__sgC.proximo_id_compra: self.__sgC.proximo_id_compra = item.id + 1

        for l_data in data.get("logs", []):
            log = RegistroLog(l_data["id"], l_data["usuario"], l_data["acao"], l_data["detalhes"], l_data["datahora"])
            self.__dbC.adiciona_logs(log.id, log)
            if log.id >= self.__lgC.proximo_id_log: self.__lgC.proximo_id_log = log.id + 1
                
        for user, u_data in data.get("usuarios", {}).items():
            u = Usuario(user, u_data["senha"], u_data["perfil"])
            if self.__dbC.checa_usuario_existe(u.username): continue
            self.__dbC.adiciona_usuario(u.username, u)

    def _criar_dados_padrao(self):
        cat_padrao = ["Marketing", "Infraestrutura", "RH", "Operações"]
        usuarios_padrao = [Usuario("admin", "admin", "Gerente"), Usuario("user", "user", "Funcionário")]
        for c in cat_padrao:
            self.__dbC.adiciona_categoria(c, Categoria(c))
        for u in usuarios_padrao:
            self.__dbC.adiciona_usuario(u.username, u)

        self.__dbC.salvar_dados()

    # Funções de requisição de login e registro de usuarios ------------------

    def login_request(self, nome: str, senha: str):
        return self.__lnC.login(nome, senha)

    def registra_usuario(self, nome: str, senha: str, perfil: str): # Equivalente a adiciona_usuario, por isso apenas ela
        return self.__rnC.registrar_usuario(nome, senha, perfil)

    # Funções de adição e remoção --------------------------------------------

    def adiciona_categoria(self, nome: str, limite: float, nome_usuario: str):
        return self.__cyC.adicionar_categoria(nome, limite, nome_usuario)

    def remove_categoria(self, cat_nome: str, nome_usuario: str):
        return self.__cyC.deletar_categoria(cat_nome, nome_usuario)

    def adiciona_item(self, nome: str, qtd: int, estimado: float, nome_usuario: str):
        return self.__sgC.adicionar_item_compra(nome, qtd, estimado, nome_usuario)

    def remove_item(self ,id_item: int, nome_usuario: str):
        return self.__sgC.deletar_item_compra(id_item, nome_usuario)

    def adiciona_transacao(self, tipo: str, descricao: str, valor: float, cat_nome: str, nome_usuario):
        return self.__tnC.criar_transacao(tipo, descricao, valor, cat_nome, nome_usuario)

    def remove_transacao(self, id_t: int, nome_usuario: str):
        return self.__tnC.deletar_transacao(id_t, nome_usuario)

    def remove_usuario(self, usuarioASerRemovido: str, nome_usuario: str):
        return self.__rnC.remover_usuario(usuarioASerRemovido, nome_usuario)

    # Demais funções, responsáveis por edições e atualizações ----------------

    def alterar_status_verbas(self, nome: str, status: bool, nome_usuario):
        return self.__cyC.alterar_status_verba(nome, status, nome_usuario)

    def editar_categorias(self, nome_antigo: str, nome_novo: str, novo_limite: float, nome_usuario: str):
        return self.__cyC.editar_categoria(nome_antigo, nome_novo, novo_limite, nome_usuario)

    def editar_itens(self, id_item: int, nome: str, qtd: int, estimado: float, nome_usuario: str):
        return self.__sgC.editar_item_compra(id_item, nome, qtd, estimado, nome_usuario)

    def alternar_status_itens(self, id_item: int, nome_usuario: str):
        return self.__sgC.alternar_status(id_item, nome_usuario)

    def atualiza_transacao(self, id_t: int, tipo: str, descricao: str, valor: float, cat_nome: str, nome_usuario: str):
        return self.__tnC.atualizar_transacao(id_t, tipo, descricao, valor, cat_nome, nome_usuario)

    # Demais funções sem nada em comum ---------------------------------------

    # Retorna saldo 
    def saldo_atual(self):
        return self.__tnC.calcular_saldo()

    # Lista transações
    def lista_transacoes(self):
        return self.__dbC.listar_transacoes()

    # Gera arquivo .csv
    def gerar_csv(self, caminho: str):
        return self.__dbC.gerar_excel_csv(caminho)   