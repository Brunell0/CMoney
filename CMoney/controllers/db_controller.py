import csv
import json
from typing import List
from models.db import Db
from models.usuario import Usuario
from models.database_models import ItemCompra
from models.database_models import RegistroLog
from models.transacao import Categoria, Transacao, Receita, Despesa

class DbController:
    def __init__(self, db: Db, db_path: str = "banco_dados.json"):
        self.__db_path = db_path
        self.__db = db

    # função para escrever no arquivo banco_dados.json -----------------------
    def salvar_dados(self):
        data = {
            "categorias": [c.to_dict() for c in self.__db.__categorias.values()],
            "transacoes": [t.to_dict() for t in self.__db.__transacoes.values()],
            "lista_compras": [i.to_dict() for i in self.__db.__listaCompras.values()],
            "logs": [l.to_dict() for l in self.__db.__logs.values()],
            "usuarios": {u.username: u.to_dict() for u in self.__db.__usuarios.values()}
        }
        with open(self.__db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # Atualiza a categoria de transações já existentes caso a categoria seja renomeada
    #Sempre usar apenas após checa_categoria_existe()
    def atualiza_historico_categorias(self, nome_antigo: str, nome_novo: str): 
        if nome_antigo != nome_novo:
            for t in self.__db.__transacoes.values():
                if t.categoria == nome_antigo:
                    t.categoria = nome_novo

    def alterna_status_compra(self, id_item: int): #Sempre usar apenas após checa_compra_existe()
        self.__db.__listaCompras[id_item].comprado = not self.__db.__listaCompras[id_item].comprado

    def alterna_status_categoria(self, cat_nome: str, status: bool): #Sempre usar apenas após checa_categoria_existe()
        self.__db.__categorias[cat_nome].bloqueada = status

    # Funções que retornam um objeto baseado na chave a eles associada -------

    def encontra_categoria(self, cat_nome: str) -> Categoria: #Sempre usar apenas após checa_categoria_existe()
        return self.__db.__categorias.get(cat_nome)

    def encontra_compra(self, id_compra: int) -> ItemCompra: #Sempre usar apenas após checa_compra_existe()
        return self.__db.__listaCompras.get(id_compra)

    def encontra_compra_status(self, id_compra: int) -> str: #Sempre usar apenas após checa_compra_existe()
        if self.__db.__listaCompras[id_compra].comprado: return "Comprado"
        return "Pendente"

    def encontra_transacao(self, id_t: int) -> Transacao: #Sempre usar apenas após checa_transacao_existe()
        return self.__db.__transacoes.get(id_t)

    def encontra_usuario(self, username: str) -> Usuario: #Sempre usar apenas após checa_usuario_existe()
        return self.__db.__usuarios.get(username) 

    # Funções que checam existência ------------------------------------------

    def checa_categoria_existe(self, cat_nome: str) -> bool:
        if cat_nome in self.__db.__categorias: return True
        return False

    def checa_compra_existe(self, id_compra: int) -> bool:
        if id_compra in self.__db.__listaCompras: return True
        return False

    def checa_transacao_existe(self, id_t: int) -> bool:
        if id_t in self.__db.__transacoes: return True
        return False

    def checa_usuario_existe(self, username: str) -> bool:
        if username in self.__db.__usuarios: return True
        return False

    # Funções de adição ou remoção -------------------------------------------

    def adiciona_categoria(self, cat_nome: str, cat: Categoria): #Sempre usar apenas após checa_categoria_existe()
        self.__db.__categorias[cat_nome] = cat

    def remove_categoria(self, cat_nome: str): #Sempre usar apenas após checa_categoria_existe()
        del self.__db.__categorias[cat_nome]

    def pop_categoria(self, cat_nome: str) -> Categoria: #Sempre usar apenas após checa_categoria_existe()
        cat = self.__db.__categorias.pop(cat_nome)
        return cat

    def adiciona_compra(self, id_compra: int, item_compra: ItemCompra): #Sempre usar apenas após checa_compra_existe()
        self.__db.__listaCompras[id_compra] = item_compra
    
    def remove_compra(self, id_compra: int): #Sempre usar apenas após checa_compra_existe()
        del self.__db.__listaCompras[id_compra]

    def adiciona_transacao(self, id: int, transacao: Receita | Despesa): #Sempre usar apenas após checa_transacao_existe()
        self.__db.__transacoes[id] = transacao

    def remove_transacao(self, id: int): #Sempre usar apenas após checa_transacao_existe()
        del self.__db.__transacoes[id]

    def adiciona_usuario(self, username: str, user: Usuario): #Sempre usar apenas após checa_usuario_existe()
        self.__db.__usuarios[username] = user

    def remove_usuario(self, username: str): #Sempre usar apenas após checa_usuario_existe()
        del self.__db.__usuarios[username]

    def adiciona_logs(self, id_log: int, log: RegistroLog):
        self.__db.__logs[id_log] = log

    # Função que lista transações --------------------------------------------

    def listar_transacoes(self) -> List[Transacao]:
        return list(self.__db.__transacoes.values())

    # Gerar arquivo .csv -----------------------------------------------------

    def gerar_excel_csv(self, filepath: str):
            # Usamos utf-8-sig para que o Excel identifique os acentos perfeitamente no Brasil
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                
                # 1. Tabela de Compras
                writer.writerow(["=== RELATÓRIO DETALHADO DE COMPRAS ==="])
                writer.writerow(["ID", "ITEM", "QUANTIDADE", "VALOR UNITÁRIO", "TOTAL ESTIMADO", "STATUS"])
                total_compras = 0

                for item in self.__db.__listaCompras.values():
                    t_estimado = item.quantidade * item.estimado
                    total_compras += t_estimado
                    status = "Comprado" if item.comprado else "Pendente"

                    writer.writerow([item.id,
                        item.nome, 
                        item.quantidade, 
                        f"R$ {item.estimado:.2f}",
                        f"R$ {t_estimado:.2f}",
                        status])
                    
                writer.writerow(["", "", "", "TOTAL GERAL DAS COMPRAS:", f"R$ {total_compras:.2f}", ""])
                writer.writerow([])
                writer.writerow([])
    
                # 2. Tabela Secundária de Categorias e Gastos
                writer.writerow(["=== ANÁLISE DE GASTOS POR CATEGORIA ==="])
                writer.writerow(["CATEGORIA", 
                    "LIMITE DE VERBA",
                    "TOTAL GASTO (DESPESAS)",
                    "SALDO DA VERBA",
                    "STATUS DA CATEGORIA"])
                
                # Calcula gastos por categoria
                gastos_cat = {c: 0.0 for c in self.__db.__categorias.keys()}
                for t in self.__db.__transacoes.values():
                    if t.__class__.__name__ == "Despesa" and t.categoria in gastos_cat:
                        gastos_cat[t.categoria] += t.valor
    
                for nome_cat, cat_obj in self.__db.__categorias.items():
                    gasto = gastos_cat[nome_cat]
                    saldo_verba = cat_obj.limite_verba - gasto
                    status_cat = "BLOQUEADA" if cat_obj.bloqueada else "LIBERADA"
                    writer.writerow([nome_cat, 
                        f"R$ {cat_obj.limite_verba:.2f}",
                        f"R$ {gasto:.2f}",
                        f"R$ {saldo_verba:.2f}", status_cat])