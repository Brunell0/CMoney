import json
import os

# Models necessários para carregar/gerar dados padrão
from models.db import Db
from models.usuario import Usuario
from models.transacao import Receita, Despesa, Categoria
from models.database_models import ItemCompra, RegistroLog

# Controllers internos orquestrados pela fachada
from controllers.db_controller import DbController
from controllers.log_controller import LogController
from controllers.login_controller import LoginController
from controllers.category_controller import CategoryController
from controllers.shopping_controller import ShoppingController
from controllers.transaction_controller import TransactionController
from controllers.registration_controller import RegistrationController


class SystemController:
    """
    Fachada (Facade) única entre as Views e os demais controllers.

    Monta toda a árvore de dependências internamente, guarda o usuário
    logado (usuario_atual) e repassa automaticamente o nome de quem está
    logado para os sub-controllers — assim as Views não precisam saber
    nada sobre sessão/autoria, apenas chamar os métodos de negócio.
    """

    def __init__(self, db_path: str = "banco_dados.json"):
        db = Db()
        self.__dbC = DbController(db, db_path)
        self.__lgC = LogController(self.__dbC)
        self.__lnC = LoginController(self.__dbC, self.__lgC)
        self.__cyC = CategoryController(self.__dbC, self.__lgC)
        self.__sgC = ShoppingController(self.__dbC, self.__lgC)
        self.__tnC = TransactionController(self.__dbC, self.__lgC)
        self.__rnC = RegistrationController(self.__dbC, self.__lgC)

        self.usuario_atual: Usuario = None
        self.carregar_dados()

    def __nome_usuario_atual(self) -> str:
        return self.usuario_atual.username if self.usuario_atual else "desconhecido"

    # Properties de leitura direta (usadas pelas Views) ----------------------

    @property
    def categorias(self) -> dict:
        return self.__dbC.listar_categorias()

    @property
    def lista_compras(self) -> dict:
        return self.__dbC.listar_compras()

    @property
    def logs(self) -> dict:
        return self.__dbC.listar_logs()

    # Carregamento de dados a partir do JSON ----------------------------------

    def carregar_dados(self):
        if not os.path.exists(self.__dbC.db_path):
            self._criar_dados_padrao()
            return

        try:
            with open(self.__dbC.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            self._criar_dados_padrao()
            return

        for c_data in data.get("categorias", []):
            if not self.__dbC.checa_categoria_existe(c_data["nome"]):
                self.__dbC.adiciona_categoria(c_data["nome"], Categoria(**c_data))

        for t_data in data.get("transacoes", []):
            if self.__dbC.checa_transacao_existe(t_data["id"]):
                continue

            if t_data["tipo"] == "Receita":
                t = Receita(t_data["id"], t_data["descricao"], t_data["valor"], t_data["categoria"], t_data["data"])
            elif t_data["tipo"] == "Despesa":
                t = Despesa(t_data["id"], t_data["descricao"], t_data["valor"], t_data["categoria"], t_data["data"])
            else:
                continue

            self.__dbC.adiciona_transacao(t.id, t)
            if t.id >= self.__tnC.proximo_id_transacao:
                self.__tnC.proximo_id_transacao = t.id + 1

        for i_data in data.get("lista_compras", []):
            if self.__dbC.checa_compra_existe(i_data["id"]):
                continue
            item = ItemCompra(**i_data)
            self.__dbC.adiciona_compra(item.id, item)
            if item.id >= self.__sgC.proximo_id_compra:
                self.__sgC.proximo_id_compra = item.id + 1

        for l_data in data.get("logs", []):
            log = RegistroLog(l_data["id"], l_data["usuario"], l_data["acao"], l_data["detalhes"], l_data["datahora"])
            self.__dbC.adiciona_logs(log.id, log)
            if log.id >= self.__lgC.proximo_id_log:
                self.__lgC.proximo_id_log = log.id + 1

        for user, u_data in data.get("usuarios", {}).items():
            if self.__dbC.checa_usuario_existe(user):
                continue
            self.__dbC.adiciona_usuario(user, Usuario(user, u_data["senha"], u_data["perfil"]))

    def _criar_dados_padrao(self):
        cat_padrao = ["Marketing", "Infraestrutura", "RH", "Operações"]
        usuarios_padrao = [Usuario("admin", "admin", "Gerente"), Usuario("user", "user", "Funcionário")]

        for c in cat_padrao:
            self.__dbC.adiciona_categoria(c, Categoria(c))
        for u in usuarios_padrao:
            self.__dbC.adiciona_usuario(u.username, u)

        self.__dbC.salvar_dados()

    # Autenticação e registro de usuários -------------------------------------

    def login(self, nome: str, senha: str) -> tuple[bool, str]:
        ok, msg = self.__lnC.login(nome, senha)
        if ok:
            self.usuario_atual = self.__dbC.encontra_usuario(nome)
        return ok, msg

    def registrar_usuario(self, nome: str, senha: str, perfil: str) -> tuple[bool, str]:
        return self.__rnC.registrar_usuario(nome, senha, perfil)

    def remover_usuario(self, usuario_alvo: str) -> tuple[bool, str]:
        return self.__rnC.remover_usuario(usuario_alvo, self.__nome_usuario_atual())

    # Categorias ---------------------------------------------------------------

    def adicionar_categoria(self, nome: str, limite: float) -> tuple[bool, str]:
        return self.__cyC.adicionar_categoria(nome, limite, self.__nome_usuario_atual())

    def deletar_categoria(self, cat_nome: str) -> tuple[bool, str]:
        return self.__cyC.deletar_categoria(cat_nome, self.__nome_usuario_atual())

    def editar_categoria(self, nome_antigo: str, nome_novo: str, novo_limite: float) -> tuple[bool, str]:
        return self.__cyC.editar_categoria(nome_antigo, nome_novo, novo_limite, self.__nome_usuario_atual())

    def alterar_status_verba(self, nome: str, status: bool) -> tuple[bool, str]:
        return self.__cyC.alterar_status_verba(nome, status, self.__nome_usuario_atual())

    # Lista de compras -----------------------------------------------------------

    def adicionar_item_compra(self, nome: str, qtd: int, estimado: float) -> tuple[bool, str]:
        return self.__sgC.adicionar_item_compra(nome, qtd, estimado, self.__nome_usuario_atual())

    def deletar_item_compra(self, id_item: int) -> tuple[bool, str]:
        return self.__sgC.deletar_item_compra(id_item, self.__nome_usuario_atual())

    def editar_item_compra(self, id_item: int, nome: str, qtd: int, estimado: float) -> tuple[bool, str]:
        return self.__sgC.editar_item_compra(id_item, nome, qtd, estimado, self.__nome_usuario_atual())

    def alternar_comprado(self, id_item: int) -> tuple[bool, str]:
        return self.__sgC.alternar_status(id_item, self.__nome_usuario_atual())

    # Transações -----------------------------------------------------------------

    def criar_transacao(self, tipo: str, descricao: str, valor: float, cat_nome: str) -> tuple[bool, str]:
        return self.__tnC.criar_transacao(tipo, descricao, valor, cat_nome, self.__nome_usuario_atual())

    def deletar_transacao(self, id_t: int) -> tuple[bool, str]:
        return self.__tnC.deletar_transacao(id_t, self.__nome_usuario_atual())

    def atualizar_transacao(self, id_t: int, tipo: str, descricao: str, valor: float, cat_nome: str) -> bool:
        return self.__tnC.atualizar_transacao(id_t, tipo, descricao, valor, cat_nome, self.__nome_usuario_atual())

    def calcular_saldo(self) -> float:
        return self.__tnC.calcular_saldo()

    def listar_transacoes(self) -> list:
        return self.__dbC.listar_transacoes()

    # Relatórios -------------------------------------------------------------------

    def gerar_excel_csv(self, caminho: str):
        return self.__dbC.gerar_excel_csv(caminho)
