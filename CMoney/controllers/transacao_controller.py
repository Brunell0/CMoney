from models.transacao import Transacao
from models.db import Db

class transacaoController:
    def __init__(self, db: Db):
        self.__db = db
        self.proximo_id_transacao = 1

    def criar_transacao(self, tipo: str, descricao: str, valor: float, categoria_nome: str) -> tuple:
            cat = self.__db.categorias.get(categoria_nome)
            if not cat: 
                return False, "Categoria não existe."
                
            if tipo == "Despesa":
                if cat.bloqueada: 
                    return False, "ERRO: Verba bloqueada para esta categoria!"
                
                # --- VALIDAÇÃO DE TETO DE VERBA ---
                # Soma tudo o que já gastou nessa categoria específica
                total_gasto = sum(t.valor for t in self.transacoes.values() if t.__class__.__name__ == "Despesa" and t.categoria == categoria_nome)
                
                # Se o (já gasto + novo valor) estourar o limite, bloqueia!
                if total_gasto + valor > cat.limite_verba:
                    return False, f"ERRO: Esta despesa excede o teto da categoria!\nLimite: R$ {cat.limite_verba:.2f}\nJá gasto: R$ {total_gasto:.2f}\nDisponível: R$ {cat.limite_verba - total_gasto:.2f}"
            
            t = Receita(self.proximo_id_transacao, descricao, valor, categoria_nome) if tipo == "Receita" else Despesa(self.proximo_id_transacao, descricao, valor, categoria_nome)
            self.transacoes[t.id] = t
            self.proximo_id_transacao += 1
            self.registrar_log("CRIAR_TRANSACAO", f"{tipo}: R${valor:.2f} em {categoria_nome} ({descricao}).")
            self.salvar_dados()
            return True, "Sucesso"