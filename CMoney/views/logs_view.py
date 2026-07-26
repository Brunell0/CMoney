import tkinter as tk
from tkinter import ttk

class LogsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.montar_tela()

    def montar_tela(self):
        # 🔒 Verificação de permissão
        if self.controller.usuario_atual.perfil != "Gerente":
            ttk.Label(self, text="🔒 ACESSO RESTRITO A GERENTES", font=("Segoe UI", 12, "bold"), foreground="#ef4444").pack(expand=True)
            return

        # 📊 Tabela de auditoria
        tabela_l = ttk.LabelFrame(self, text=" Histórico Geral de Operações de Auditoria ", padding=10)
        tabela_l.pack(fill="both", expand=True, padx=20, pady=20)

        self.tree_log = ttk.Treeview(tabela_l, columns=("Data", "Usuario", "Acao", "Detalhes"), show="headings", height=12)
        self.tree_log.heading("Data", text="DATA / HORA"); self.tree_log.column("Data", width=140, anchor="center")
        self.tree_log.heading("Usuario", text="OPERADOR"); self.tree_log.column("Usuario", width=90, anchor="center")
        self.tree_log.heading("Acao", text="AÇÃO SISTÊMICA"); self.tree_log.column("Acao", width=150, anchor="center")
        self.tree_log.heading("Detalhes", text="MODIFICAÇÕES DETALHADAS"); self.tree_log.column("Detalhes", width=400)
        self.tree_log.pack(fill="both", expand=True, padx=5, pady=5)

    def atualizar_logs(self):
        if hasattr(self, 'tree_log'):
            for i in self.tree_log.get_children(): 
                self.tree_log.delete(i)
            for l in sorted(self.controller.logs.values(), key=lambda x: x.id, reverse=True):
                self.tree_log.insert("", "end", values=(l.datahora, l.usuario, l.acao, l.detalhes))