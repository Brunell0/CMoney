import json
import os
import csv

# Import de todos os models necessários no sistema
from models.usuario import Usuario
from models.transacao import Receita, Despesa, Categoria
from models.database_models import ItemCompra, RegistroLog

# Import de todos os controllers para referenciação
from controllers.Db_controller import DbController
from controllers.Log_controller import LogController
from controllers.Login_controller import LoginController
from controllers.Category_controller import CategoryController
from controllers.Transaction_controller import TransactionController
from controllers.Registration_controller import RegistrationController

# Os erros neste arquivo são intencionais e desaparecerão conforme a reestruturação for avançando

class SystemController:
    def __init__(self, 
            dbController: DbController, 
            logController: LogController,
            loginController: LoginController,
            categoryController: CategoryController,
            transactionController: TransactionController,
            registrationController: RegistrationController
        ):

        self.__dbC = dbController
        self.__lgC = logController
        self.__lnC = loginController
        self.__cyC = categoryController
        self.__tnC = transactionController
        self.__rnC = registrationController

        self.usuario_atual: Usuario = None
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
                self.__dbC.__db.__transacoes[t.id] = t
            elif t_data["tipo"] == "Despesa":
                t = Despesa(t_data["id"], t_data["descricao"], t_data["valor"], t_data["categoria"], t_data["data"]) 
                self.__dbC.__db.__transacoes[t.id] = t

            if t.id >= self.__tnC.proximo_id_transacao: self.__tnC.proximo_id_transacao = t.id + 1
                
        for i_data in data.get("lista_compras", []):
            item = ItemCompra(**i_data)
            self.__dbC.__db.__listaCompras[item.id] = item
            if item.id >= self.proximo_id_compra: self.proximo_id_compra = item.id + 1 #adicionar controller para compras

        for l_data in data.get("logs", []):
            log = RegistroLog(l_data["id"], l_data["usuario"], l_data["acao"], l_data["detalhes"], l_data["datahora"])
            self.__dbC.__logs[log.id] = log
            if log.id >= self.__lgC.proximo_id_log: self.__lgC.proximo_id_log = log.id + 1
                
        for user, u_data in data.get("usuarios", {}).items():
            self.__dbC.__db.__usuarios[user] = Usuario(user, u_data["senha"], u_data["perfil"])

    def _criar_dados_padrao(self):
        self.__dbC.__db.__categorias = {
            c: Categoria(c) for c in ["Marketing", "Infraestrutura", "RH", "Operações"]
        }
        self.__dbC.__db.__usuarios = {
            "admin": Usuario("admin", "admin", "Gerente"),
            "user": Usuario("user", "user", "Funcionário")
        }

        self.__dbC.salvar_dados()


    # Tudo abaixo disso ainda precisa ser removido daqui

    def alterar_status_verba(self, nome: str, bloquear: bool):
        if nome in self.categorias:
            self.categorias[nome].bloqueada = bloquear
            acao_str = "Bloqueou" if bloquear else "Liberou"
            self.registrar_log("STATUS_VERBA", f"{acao_str} verba da categoria '{nome}'.")
            self.salvar_dados()

    # === LISTA DE COMPRAS CRUD ===
    def adicionar_item_compra(self, nome: str, qtd: int, estimado: float):
        item = ItemCompra(self.proximo_id_compra, nome, qtd, estimado)
        self.lista_compras[item.id] = item
        self.proximo_id_compra += 1
        self.registrar_log("CRIAR_COMPRA", f"Item '{nome}' (Qtd: {qtd}) adicionado.")
        self.salvar_dados()

    def editar_item_compra(self, id_item: int, nome: str, qtd: int, estimado: float):
        if id_item in self.lista_compras:
            item = self.lista_compras[id_item]
            item.nome = nome
            item.quantidade = qtd
            item.estimado = estimado
            self.registrar_log("EDITAR_COMPRA", f"Item ID {id_item} atualizado para '{nome}'.")
            self.salvar_dados()

    def deletar_item_compra(self, id_item: int):
        if id_item in self.lista_compras:
            nome = self.lista_compras[id_item].nome
            del self.lista_compras[id_item]
            self.registrar_log("DELETAR_COMPRA", f"Item '{nome}' removido.")
            self.salvar_dados()

    def alternar_comprado(self, id_item: int):
        if id_item in self.lista_compras:
            self.lista_compras[id_item].comprado = not self.lista_compras[id_item].comprado
            status = "Comprado" if self.lista_compras[id_item].comprado else "Pendente"
            self.registrar_log("STATUS_COMPRA", f"Item ID {id_item} alterado para {status}.")
            self.salvar_dados()

    # === EXCEL NATIVO ===
    def gerar_excel_csv(self, filepath: str):
        # Usamos utf-8-sig para que o Excel identifique os acentos perfeitamente no Brasil
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            
            # 1. Tabela de Compras
            writer.writerow(["=== RELATÓRIO DETALHADO DE COMPRAS ==="])
            writer.writerow(["ID", "ITEM", "QUANTIDADE", "VALOR UNITÁRIO", "TOTAL ESTIMADO", "STATUS"])
            total_compras = 0
            for item in self.lista_compras.values():
                t_estimado = item.quantidade * item.estimado
                total_compras += t_estimado
                status = "Comprado" if item.comprado else "Pendente"
                writer.writerow([item.id, item.nome, item.quantidade, f"R$ {item.estimado:.2f}", f"R$ {t_estimado:.2f}", status])
            writer.writerow(["", "", "", "TOTAL GERAL DAS COMPRAS:", f"R$ {total_compras:.2f}", ""])
            writer.writerow([])
            writer.writerow([])

            # 2. Tabela Secundária de Categorias e Gastos
            writer.writerow(["=== ANÁLISE DE GASTOS POR CATEGORIA ==="])
            writer.writerow(["CATEGORIA", "LIMITE DE VERBA", "TOTAL GASTO (DESPESAS)", "SALDO DA VERBA", "STATUS DA CATEGORIA"])
            
            # Calcula gastos por categoria
            gastos_cat = {c: 0.0 for c in self.categorias.keys()}
            for t in self.transacoes.values():
                if t.__class__.__name__ == "Despesa" and t.categoria in gastos_cat:
                    gastos_cat[t.categoria] += t.valor

            for nome_cat, cat_obj in self.categorias.items():
                gasto = gastos_cat[nome_cat]
                saldo_verba = cat_obj.limite_verba - gasto
                status_cat = "BLOQUEADA" if cat_obj.bloqueada else "LIBERADA"
                writer.writerow([nome_cat, f"R$ {cat_obj.limite_verba:.2f}", f"R$ {gasto:.2f}", f"R$ {saldo_verba:.2f}", status_cat])