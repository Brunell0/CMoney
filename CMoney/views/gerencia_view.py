import tkinter as tk
from tkinter import ttk

class GerenciaView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.montar_tela()

    def montar_tela(self):
        # 🔒 Trava de segurança para acesso exclusivo de Gerentes
        if self.controller.usuario_atual.perfil != "Gerente":
            ttk.Label(self, text="🔒 ACESSO RESTRITO A GERENTES", font=("Segoe UI", 12, "bold"), foreground="#ef4444").pack(expand=True)
            return

        f_top = ttk.LabelFrame(self, text=" Controle de Orçamentos e Verbas ", padding=15)
        f_top.pack(fill="x", padx=20, pady=15)
        
        ttk.Label(f_top, text="Categoria:").pack(side="left", padx=5)
        self.ent_cat_nome = ttk.Entry(f_top, width=20)
        self.ent_cat_nome.pack(side="left", padx=5)

        ttk.Label(f_top, text="Teto de Verba (R$):").pack(side="left", padx=5)
        self.ent_cat_limite = ttk.Entry(f_top, width=15)
        self.ent_cat_limite.pack(side="left", padx=5)
        
        tabela_f = ttk.LabelFrame(self, text=" Categorias Mapeadas ", padding=10)
        tabela_f.pack(fill="both", expand=True, padx=20, pady=5)

        self.tree_cat = ttk.Treeview(tabela_f, columns=("Nome", "Limite", "Status"), show="headings", height=6, selectmode="extended")
        for col in ("Nome", "Limite", "Status"): 
            self.tree_cat.heading(col, text=col.upper())
            self.tree_cat.column(col, anchor="center" if col == "Status" else "w")
        self.tree_cat.pack(fill="both", expand=True, padx=5, pady=5)
        
        def salvar_cat():
            try:
                self.controller.adicionar_categoria(self.ent_cat_nome.get(), float(self.ent_cat_limite.get()))
                self.atualizar_cats()
                self.ent_cat_nome.delete(0, tk.END)
                self.ent_cat_limite.delete(0, tk.END)
            except ValueError:
                pass

        def excluir_multiplos():
            for sel in self.tree_cat.selection():
                self.controller.deletar_categoria(self.tree_cat.item(sel)['values'][0])
            self.atualizar_cats()

        def set_status(bloquear):
            for sel in self.tree_cat.selection():
                self.controller.alterar_status_verba(self.tree_cat.item(sel)['values'][0], bloquear)
            self.atualizar_cats()

        def carregar_para_edicao():
            sel = self.tree_cat.selection()
            if not sel:
                return
            val = self.tree_cat.item(sel[0])['values']
            self.ent_cat_nome.delete(0, tk.END)
            self.ent_cat_nome.insert(0, val[0])
            self.ent_cat_limite.delete(0, tk.END)
            self.ent_cat_limite.insert(0, str(val[1]).replace("R$ ", ""))
            
            def confirmar_edicao():
                try:
                    self.controller.editar_categoria(val[0], self.ent_cat_nome.get(), float(self.ent_cat_limite.get()))
                    self.atualizar_cats()
                    self.ent_cat_nome.delete(0, tk.END)
                    self.ent_cat_limite.delete(0, tk.END)
                    self.btn_add_cat.config(text="Adicionar Categoria", command=salvar_cat)
                except ValueError:
                    pass

            self.btn_add_cat.config(text="Salvar Alteração", command=confirmar_edicao)

        self.btn_add_cat = ttk.Button(f_top, text="Adicionar Categoria", command=salvar_cat)
        self.btn_add_cat.pack(side="left", padx=15)

        f_btn = tk.Frame(tabela_f, bg="white")
        f_btn.pack(fill="x", side="bottom", pady=5)
        ttk.Button(f_btn, text="🗑️ Excluir Categorias", style="Danger.TButton", command=excluir_multiplos).pack(side="left", padx=5)
        ttk.Button(f_btn, text="🔒 Bloquear Verba", command=lambda: set_status(True)).pack(side="left", padx=5)
        ttk.Button(f_btn, text="🔓 Liberar Verba", command=lambda: set_status(False)).pack(side="left", padx=5)
        ttk.Button(f_btn, text="✏️ Editar Registro", command=carregar_para_edicao).pack(side="left", padx=5)

    def atualizar_cats(self):
        if hasattr(self, 'tree_cat'):
            for i in self.tree_cat.get_children():
                self.tree_cat.delete(i)
            for c in self.controller.categorias.values():
                self.tree_cat.insert("", "end", values=(c.nome, f"R$ {c.limite_verba:.2f}", "BLOQUEADO" if c.bloqueada else "LIBERADO"))