import json
import os
import csv
from typing import List, Dict
from models.usuario import Usuario
from models.transacao import Transacao, Receita, Despesa, Categoria
from models.database_models import ItemCompra, RegistroLog

# Os erros neste arquivo são intencionais e desaparecerão conforme a reestruturação for sendo concluída

class SistemaController:
    def __init__(self):
        self.usuario_atual: Usuario = None
        self.proximo_id_compra = 1
        self.carregar_dados()

    def carregar_dados(self):
        if not os.path.exists(self.db_path):
            self._criar_dados_padrao()
            return

        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            self._criar_dados_padrao()
            return

        for c_data in data.get("categorias", []):
            self.categorias[c_data["nome"]] = Categoria(**c_data)
            
        for t_data in data.get("transacoes", []):
            t = Receita(t_data["id"], t_data["descricao"], t_data["valor"], t_data["categoria"], t_data["data"]) if t_data["tipo"] == "Receita" else Despesa(t_data["id"], t_data["descricao"], t_data["valor"], t_data["categoria"], t_data["data"])
            self.transacoes[t.id] = t
            if t.id >= self.proximo_id_transacao: self.proximo_id_transacao = t.id + 1
                
        for i_data in data.get("lista_compras", []):
            item = ItemCompra(**i_data)
            self.lista_compras[item.id] = item
            if item.id >= self.proximo_id_compra: self.proximo_id_compra = item.id + 1

        for l_data in data.get("logs", []):
            log = RegistroLog(l_data["id"], l_data["usuario"], l_data["acao"], l_data["detalhes"], l_data["datahora"])
            self.logs[log.id] = log
            if log.id >= self.proximo_id_log: self.proximo_id_log = log.id + 1
                
        for user, u_data in data.get("usuarios", {}).items():
            self.usuarios[user] = Usuario(user, u_data["senha"], u_data["perfil"])

    def _criar_dados_padrao(self):
        self.categorias = {c: Categoria(c) for c in ["Marketing", "Infraestrutura", "RH", "Operações"]}
        self.usuarios = {"admin": Usuario("admin", "admin", "Gerente"), "user": Usuario("user", "user", "Funcionário")}
        self.salvar_dados()

    def login(self, username: str, senha: str) -> bool:
        user = self.usuarios.get(username)
        if user and user.password == senha:
            self.usuario_atual = user
            self.registrar_log("LOGIN", f"Usuário '{username}' iniciou sessão.")
            return True
        return False

    # === TRANSAÇÕES ===
    # === TRANSAÇÕES (NOVO CRIAR COM VALIDAÇÃO DE TETO) ===
    

    # === TRANSAÇÕES (NOVO ATUALIZAR COM VALIDAÇÃO DE TETO) ===
    def atualizar_transacao(self, id_t: int, tipo: str, descricao: str, valor: float, categoria_nome: str) -> bool:
        if id_t not in self.transacoes: return False
        cat = self.categorias.get(categoria_nome)
        
        if tipo == "Despesa" and cat:
            if cat.bloqueada: return False
            
            # Soma o gasto dos OUTROS registros (ignorando o que está sendo editado agora)
            total_gasto = sum(t.valor for t in self.transacoes.values() if t.__class__.__name__ == "Despesa" and t.categoria == categoria_nome and t.id != id_t)
            
            if total_gasto + valor > cat.limite_verba:
                return False # Vai disparar o bloco except/erro na View
                
        t = Receita(id_t, descricao, valor, categoria_nome) if tipo == "Receita" else Despesa(id_t, descricao, valor, categoria_nome)
        self.transacoes[id_t] = t
        self.registrar_log("EDITAR_TRANSACAO", f"ID {id_t} alterado para {tipo} de R${valor:.2f} em {categoria_nome}.")
        self.salvar_dados()
        return True
        
    def listar_transacoes(self) -> List[Transacao]:
        return list(self.transacoes.values())

    def atualizar_transacao(self, id_t: int, tipo: str, descricao: str, valor: float, categoria_nome: str) -> bool:
        if id_t not in self.transacoes: return False
        t = Receita(id_t, descricao, valor, categoria_nome) if tipo == "Receita" else Despesa(id_t, descricao, valor, categoria_nome)
        self.transacoes[id_t] = t
        self.registrar_log("EDITAR_TRANSACAO", f"ID {id_t} alterado para {tipo} de R${valor:.2f} em {categoria_nome}.")
        self.salvar_dados()
        return True

    def deletar_transacao(self, id_t: int) -> bool:
        if id_t in self.transacoes:
            t = self.transacoes[id_t]
            self.registrar_log("DELETAR_TRANSACAO", f"Transação ID {id_t} ({t.descricao}) removida.")
            del self.transacoes[id_t]
            self.salvar_dados()
            return True
        return False

    def calcular_saldo(self) -> float:
        return sum(t.calcular_impacto() for t in self.transacoes.values())

    # === CATEGORIAS (GERÊNCIA) CRUD ===
    def adicionar_categoria(self, nome: str, limite: float):
        if nome not in self.categorias:
            self.categorias[nome] = Categoria(nome, limite)
            self.registrar_log("CRIAR_CATEGORIA", f"Categoria '{nome}' criada com limite R${limite:.2f}.")
            self.salvar_dados()

    def editar_categoria(self, nome_antigo: str, novo_nome: str, novo_limite: float):
        if nome_antigo in self.categorias:
            cat = self.categorias.pop(nome_antigo)
            cat.nome = novo_nome
            cat.limite_verba = novo_limite
            self.categorias[novo_nome] = cat
            # Atualiza histórico de transações atreladas à categoria
            if nome_antigo != novo_nome:
                for t in self.transacoes.values():
                    if t.categoria == nome_antigo:
                        t.categoria = novo_nome
            self.registrar_log("EDITAR_CATEGORIA", f"Categoria '{nome_antigo}' renomeada/alterada para '{novo_nome}' com teto R${novo_limite:.2f}.")
            self.salvar_dados()

    def deletar_categoria(self, nome: str):
        if nome in self.categorias:
            del self.categorias[nome]
            self.registrar_log("DELETAR_CATEGORIA", f"Categoria '{nome}' removida.")
            self.salvar_dados()

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