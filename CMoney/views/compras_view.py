import tkinter as tk
from tkinter import ttk

class ComprasView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.montar_tela()

    def montar_tela(self):
        f_add = ttk.LabelFrame(self, text=" Solicitar Suprimentos / Itens ", padding=15)
        f_add.pack(fill="x", padx=20, pady=15)
        
        self.e_item = ttk.Entry(f_add, width=18)
        self.e_q = ttk.Entry(f_add, width=6)
        self.e_est = ttk.Entry(f_add, width=12)
        
        ttk.Label(f_add, text="Item/Produto:").pack(side="left", padx=2)
        self.e_item.pack(side="left", padx=5)
        ttk.Label(f_add, text="Qtd:").pack(side="left", padx=2)
        self.e_q.pack(side="left", padx=5)
        ttk.Label(f_add, text="Custo Unitário:").pack(side="left", padx=2)
        self.e_est.pack(side="left", padx=5)
        
        tabela_c = ttk.LabelFrame(self, text=" Lista de Demandas Estipuladas ", padding=10)
        tabela_c.pack(fill="both", expand=True, padx=20, pady=5)

        self.tree_compra = ttk.Treeview(tabela_c, columns=("id", "nome", "qtd", "total", "status"), show="headings", selectmode="extended")
        for col, t in zip(("id", "nome", "qtd", "total", "status"), ("ID", "ITEM", "QUANTIDADE", "TOTAL ESTIMADO", "STATUS DE AQUISIÇÃO")): 
            self.tree_compra.heading(col, text=t)
            self.tree_compra.column(col, anchor="center" if col in ("id", "qtd", "status") else "w")
        self.tree_compra.pack(fill="both", expand=True, padx=5, pady=5)
        
        def add():
            try:
                self.controller.adicionar_item_compra(self.e_item.get(), int(self.e_q.get()), float(self.e_est.get()))
                self.atualizar_compras()
                self.e_item.delete(0, tk.END)
                self.e_q.delete(0, tk.END)
                self.e_est.delete(0, tk.END)
            except ValueError:
                pass

        def deletar_multiplos():
            for sel in self.tree_compra.selection():
                self.controller.deletar_item_compra(int(self.tree_compra.item(sel)['values'][0]))
            self.atualizar_compras()

        def toggle_multiplos():
            for sel in self.tree_compra.selection():
                self.controller.alternar_comprado(int(self.tree_compra.item(sel)['values'][0]))
            self.atualizar_compras()

        def editar_compra():
            sel = self.tree_compra.selection()
            if not sel: 
                return
            val = self.tree_compra.item(sel[0])['values']
            item_id = int(val[0])
            item = self.controller.lista_compras[item_id]
            
            self.e_item.delete(0, tk.END)
            self.e_item.insert(0, item.nome)
            self.e_q.delete(0, tk.END)
            self.e_q.insert(0, str(item.quantidade))
            self.e_est.delete(0, tk.END)
            self.e_est.insert(0, str(item.estimado))
            
            def salvar_edicao():
                try:
                    self.controller.editar_item_compra(item_id, self.e_item.get(), int(self.e_q.get()), float(self.e_est.get()))
                    self.atualizar_compras()
                    self.e_item.delete(0, tk.END)
                    self.e_q.delete(0, tk.END)
                    self.e_est.delete(0, tk.END)
                    self.btn_add_compra.config(text="Adicionar na Lista", command=add)
                except ValueError:
                    pass

            self.btn_add_compra.config(text="Salvar Alteração", command=salvar_edicao)

        self.btn_add_compra = ttk.Button(f_add, text="Adicionar na Lista", command=add)
        self.btn_add_compra.pack(side="left", padx=15)

        f_btn = tk.Frame(tabela_c, bg="white")
        f_btn.pack(fill="x", side="bottom", pady=5)
        ttk.Button(f_btn, text="🔄 Alternar Status (Pendente/Comprado)", command=toggle_multiplos).pack(side="left", padx=5)
        ttk.Button(f_btn, text="🗑️ Remover Pedidos", style="Danger.TButton", command=deletar_multiplos).pack(side="left", padx=5)
        ttk.Button(f_btn, text="✏️ Editar Item", command=editar_compra).pack(side="left", padx=5)

    def atualizar_compras(self):
        for i in self.tree_compra.get_children():
            self.tree_compra.delete(i)
        for i in self.controller.lista_compras.values():
            self.tree_compra.insert("", "end", values=(i.id, i.nome, i.quantidade, f"R$ {i.quantidade*i.estimado:.2f}", "✅ Comprado" if i.comprado else "⏳ Pendente"))