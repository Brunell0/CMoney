import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from views.relatorios_view import RelatoriosView
from views.logs_view import LogsView

class MainView(tk.Frame):
    def __init__(self, parent, controller, on_logout):
        super().__init__(parent)
        self.controller = controller
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)
        
        # Configuração de Estilos Globais (UI/UX)
        self.configurar_estilos()
        self.montar_tela()

    def configurar_estilos(self):
        self.style = ttk.Style()
        # Força o uso do tema nativo que aceita melhor customizações de borda e cores
        self.style.theme_use("clam")
        
        # --- Paleta de Cores Estilo Dashboard Moderno ---
        COLOR_BG = "#f8f9fa"          # Fundo geral cinza bem claro
        COLOR_PRIMARY = "#1e3a8a"     # Azul escuro corporativo
        COLOR_ACCENT = "#3b82f6"      # Azul claro para destaques
        COLOR_TEXT = "#1f2937"        # Grafite escuro para textos
        
        # Configurações de elementos básicos
        self.style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT, font=("Segoe UI", 10))
        
        # Customização das Abas (Notebook)
        self.style.configure("TNotebook", background="#e5e7eb", padding=2)
        self.style.configure("TNotebook.Tab", background="#d1d5db", foreground=COLOR_TEXT, padding=[15, 6], font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", COLOR_PRIMARY)], foreground=[("selected", "white")])
        
        # Customização de Botões (Mais limpos e arredondados visualmente)
        self.style.configure("TButton", background=COLOR_ACCENT, foreground="white", borderwidth=0, padding=[10, 6], font=("Segoe UI", 10, "bold"))
        self.style.map("TButton", background=[("active", "#2563eb")]) # Efeito hover (passar o mouse)
        
        # Botão de Alerta / Exclusão
        self.style.configure("Danger.TButton", background="#ef4444", foreground="white")
        self.style.map("Danger.TButton", background=[("active", "#dc2626")])
        
        # Customização das Tabelas (Treeview)
        self.style.configure("Treeview", background="white", fieldbackground="white", rowheight=25, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", background="#f3f4f6", foreground=COLOR_TEXT, font=("Segoe UI", 10, "bold"), padding=5)
        self.style.map("Treeview", background=[("selected", "#3b82f6")], foreground=[("selected", "white")])
        
        # Customização de Frames de Formulário
        self.style.configure("TLabelframe", background="white", bordercolor="#e5e7eb", borderwidth=1)
        self.style.configure("TLabelframe.Label", background="white", font=("Segoe UI", 10, "bold"), foreground=COLOR_PRIMARY)

    def montar_tela(self):
        # Barra de Navegação Superior Superior (Fundo Premium)
        nav_bar = tk.Frame(self, bg="#0f172a", height=50)
        nav_bar.pack(fill="x", side="top")
        
        user_info = f"👤  {self.controller.usuario_atual.username.upper()}  •  {self.controller.usuario_atual.perfil}"
        tk.Label(nav_bar, text=user_info, bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 10, "bold")).pack(side="left", padx=20, pady=10)
        
        # Botão Sair Minimalista
        btn_sair = tk.Button(nav_bar, text="Sair do Sistema", bg="#ef4444", fg="white", font=("Segoe UI", 9, "bold"), 
                             command=self.on_logout, bd=0, cursor="hand2", activebackground="#dc2626", activeforeground="white", padx=15)
        btn_sair.pack(side="right", padx=15, pady=10)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.aba_planilhas = ttk.Frame(self.notebook)
        self.aba_gerencia = ttk.Frame(self.notebook)
        self.aba_compras = ttk.Frame(self.notebook)
        self.aba_logs = LogsView(self.notebook, self.controller)
        self.aba_config = RelatoriosView(self.notebook, self.controller)
        
        self.notebook.add(self.aba_planilhas, text="📊  Registros")
        self.notebook.add(self.aba_gerencia, text="🛡️  Gerência")
        self.notebook.add(self.aba_compras, text="🛒  Compras")
        self.notebook.add(self.aba_config, text="⚙️  Relatórios")
        self.notebook.add(self.aba_logs, text="📜  Logs de Auditoria")
        
        self.montar_aba_planilhas()
        self.montar_aba_gerencia()
        self.montar_aba_compras()
        self.montar_aba_logs()
        self.montar_aba_config()

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.atualizar_todas_abas())

    def atualizar_todas_abas(self):
        self.atualizar_tabela_planilha()
        self.atualizar_cats()
        self.atualizar_compras()
        self.aba_logs.atualizar_logs()

    # --- ABA REGISTROS ---
    def montar_aba_planilhas(self):
        # Card de Saldo Estilo Dashboard
        card_saldo = tk.Frame(self.aba_planilhas, bg="#ffffff", bd=1, relief="solid", highlightthickness=0)
        card_saldo.configure(highlightbackground="#e5e7eb")
        card_saldo.pack(fill="x", padx=15, pady=10)
        
        self.lbl_saldo = tk.Label(card_saldo, text="", font=("Segoe UI", 14, "bold"), bg="white", fg="#1e3a8a", anchor="w")
        self.lbl_saldo.pack(fill="x", padx=15, pady=12)
        
        main_f = tk.Frame(self.aba_planilhas); main_f.pack(fill="both", expand=True, padx=10, pady=5)
        
        form = ttk.LabelFrame(main_f, text=" Lançar Movimentação ", padding=15)
        form.pack(side="left", fill="y", padx=10, pady=5)
        
        ttk.Label(form, text="Tipo:").grid(row=0, column=0, sticky="w", pady=3)
        self.cb_tipo = ttk.Combobox(form, values=["Receita", "Despesa"], state="readonly", width=22)
        self.cb_tipo.set("Despesa"); self.cb_tipo.grid(row=0, column=1, pady=8)
        
        ttk.Label(form, text="Descrição:").grid(row=1, column=0, sticky="w", pady=3)
        self.ent_desc = ttk.Entry(form, width=24); self.ent_desc.grid(row=1, column=1, pady=8)
        
        ttk.Label(form, text="Valor (R$):").grid(row=2, column=0, sticky="w", pady=3)
        self.ent_val = ttk.Entry(form, width=24); self.ent_val.grid(row=2, column=1, pady=8)
        
        ttk.Label(form, text="Categoria:").grid(row=3, column=0, sticky="w", pady=3)
        self.cb_cat = ttk.Combobox(form, state="readonly", width=22)
        self.cb_cat.grid(row=3, column=1, pady=8)
        
        tabela_frame = ttk.LabelFrame(main_f, text=" Histórico Financeiro ", padding=10)
        tabela_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)
        
        self.tree_plan = ttk.Treeview(tabela_frame, columns=("id", "tipo", "descricao", "valor", "categoria", "data"), show="headings", height=10)
        for col in ("id", "tipo", "descricao", "valor", "categoria", "data"):
            self.tree_plan.heading(col, text=col.upper())
            self.tree_plan.column(col, width=95, anchor="center" if col in ("id", "tipo", "data") else "w")
        self.tree_plan.pack(fill="both", expand=True, padx=5, pady=5)

        def salvar():
            try:
                s, m = self.controller.criar_transacao(self.cb_tipo.get(), self.ent_desc.get(), float(self.ent_val.get()), self.cb_cat.get())
                if s: 
                    self.atualizar_tabela_planilha()
                    self.ent_desc.delete(0, tk.END); self.ent_val.delete(0, tk.END)
                else: messagebox.showerror("Erro", m)
            except ValueError: messagebox.showerror("Erro", "Valor Inválido!")

        def deletar():
            for sel in self.tree_plan.selection():
                self.controller.deletar_transacao(int(self.tree_plan.item(sel)['values'][0]))
            self.atualizar_tabela_planilha()

        def carregar_para_edicao_plan():
            sel = self.tree_plan.selection()
            if not sel: return
            val = self.tree_plan.item(sel[0])['values']
            id_t = int(val[0])
            
            self.cb_tipo.set(val[1])
            self.ent_desc.delete(0, tk.END); self.ent_desc.insert(0, val[2])
            self.ent_val.delete(0, tk.END); self.ent_val.insert(0, str(val[3]).replace("R$ ", ""))
            self.cb_cat.set(val[4])
            
            def confirmar_edicao_plan():
                try:
                    sucesso = self.controller.atualizar_transacao(id_t, self.cb_tipo.get(), self.ent_desc.get(), float(self.ent_val.get()), self.cb_cat.get())
                    if sucesso:
                        self.atualizar_tabela_planilha()
                        self.ent_desc.delete(0, tk.END); self.ent_val.delete(0, tk.END)
                        self.btn_salvar_plan.config(text="Adicionar Registro", style="TButton", command=salvar)
                    else:
                        messagebox.showerror("Erro", "Verifique se a verba está bloqueada ou se excedeu o teto limite!")
                except ValueError: messagebox.showerror("Erro", "Valor Inválido!")
            self.btn_salvar_plan.config(text="Salvar Alteração", command=confirmar_edicao_plan)

        self.btn_salvar_plan = ttk.Button(form, text="Adicionar Registro", command=salvar)
        self.btn_salvar_plan.grid(row=4, column=0, columnspan=2, pady=15, sticky="we")
        
        f_btn_plan = tk.Frame(tabela_frame, bg="white"); f_btn_plan.pack(fill="x", side="bottom", padx=5, pady=5)
        ttk.Button(f_btn_plan, text="🗑️ Deletar Selecionados", style="Danger.TButton", command=deletar).pack(side="left", padx=5)
        ttk.Button(f_btn_plan, text="✏️ Editar Selecionado", command=carregar_para_edicao_plan).pack(side="left", padx=5)

    def atualizar_tabela_planilha(self):
        self.cb_cat['values'] = list(self.controller.categorias.keys())
        if self.cb_cat['values'] and not self.cb_cat.get(): self.cb_cat.set(self.cb_cat['values'][0])
        for item in self.tree_plan.get_children(): self.tree_plan.delete(item)
        for t in self.controller.listar_transacoes():
            self.tree_plan.insert("", "end", values=(t.id, t.__class__.__name__, t.descricao, f"R$ {t.valor:.2f}", t.categoria, t.data))
        self.lbl_saldo.config(text=f"📊   SALDO CONSOLIDADO:  R$ {self.controller.calcular_saldo():.2f}")

    # --- ABA GERÊNCIA ---
    def montar_aba_gerencia(self):
        if self.controller.usuario_atual.perfil != "Gerente":
            ttk.Label(self.aba_gerencia, text="🔒 ACESSO RESTRITO A GERENTES", font=("Segoe UI", 12, "bold"), foreground="#ef4444").pack(expand=True)
            return

        f_top = ttk.LabelFrame(self.aba_gerencia, text=" Controle de Orçamentos e Verbas ", padding=15)
        f_top.pack(fill="x", padx=20, pady=15)
        
        ttk.Label(f_top, text="Categoria:").pack(side="left", padx=5)
        self.ent_cat_nome = ttk.Entry(f_top, width=20); self.ent_cat_nome.pack(side="left", padx=5)
        ttk.Label(f_top, text="Teto de Verba (R$):").pack(side="left", padx=5)
        self.ent_cat_limite = ttk.Entry(f_top, width=15); self.ent_cat_limite.pack(side="left", padx=5)
        
        tabela_f = ttk.LabelFrame(self.aba_gerencia, text=" Categorias Mapeadas ", padding=10)
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
                self.ent_cat_nome.delete(0, tk.END); self.ent_cat_limite.delete(0, tk.END)
            except ValueError: pass

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
            if not sel: return
            val = self.tree_cat.item(sel[0])['values']
            self.ent_cat_nome.delete(0, tk.END); self.ent_cat_nome.insert(0, val[0])
            self.ent_cat_limite.delete(0, tk.END); self.ent_cat_limite.insert(0, str(val[1]).replace("R$ ", ""))
            
            def confirmar_edicao():
                try:
                    self.controller.editar_categoria(val[0], self.ent_cat_nome.get(), float(self.ent_cat_limite.get()))
                    self.atualizar_cats()
                    self.ent_cat_nome.delete(0, tk.END); self.ent_cat_limite.delete(0, tk.END)
                    btn_add_cat.config(text="Adicionar Categoria", command=salvar_cat)
                except ValueError: pass
            btn_add_cat.config(text="Salvar Alteração", command=confirmar_edicao)

        btn_add_cat = ttk.Button(f_top, text="Adicionar Categoria", command=salvar_cat)
        btn_add_cat.pack(side="left", padx=15)

        f_btn = tk.Frame(tabela_f, bg="white"); f_btn.pack(fill="x", side="bottom", pady=5)
        ttk.Button(f_btn, text="🗑️ Excluir Categorias", style="Danger.TButton", command=excluir_multiplos).pack(side="left", padx=5)
        ttk.Button(f_btn, text="🔒 Bloquear Verba", command=lambda: set_status(True)).pack(side="left", padx=5)
        ttk.Button(f_btn, text="🔓 Liberar Verba", command=lambda: set_status(False)).pack(side="left", padx=5)
        ttk.Button(f_btn, text="✏️ Editar Registro", command=carregar_para_edicao).pack(side="left", padx=5)

    def atualizar_cats(self):
        if hasattr(self, 'tree_cat'):
            for i in self.tree_cat.get_children(): self.tree_cat.delete(i)
            for c in self.controller.categorias.values():
                self.tree_cat.insert("", "end", values=(c.nome, f"R$ {c.limite_verba:.2f}", "BLOQUEADO" if c.bloqueada else "LIBERADO"))

    # --- ABA COMPRAS ---
    def montar_aba_compras(self):
        f_add = ttk.LabelFrame(self.aba_compras, text=" Solicitar Suprimentos / Itens ", padding=15)
        f_add.pack(fill="x", padx=20, pady=15)
        
        self.e_item = ttk.Entry(f_add, width=18); self.e_q = ttk.Entry(f_add, width=6); self.e_est = ttk.Entry(f_add, width=12)
        ttk.Label(f_add, text="Item/Produto:").pack(side="left", padx=2)
        self.e_item.pack(side="left", padx=5)
        ttk.Label(f_add, text="Qtd:").pack(side="left", padx=2)
        self.e_q.pack(side="left", padx=5)
        ttk.Label(f_add, text="Custo Unitário:").pack(side="left", padx=2)
        self.e_est.pack(side="left", padx=5)
        
        tabela_c = ttk.LabelFrame(self.aba_compras, text=" Lista de Demandas Estipuladas ", padding=10)
        tabela_c.pack(fill="both", expand=True, padx=20, pady=5)

        self.tree_compra = ttk.Treeview(tabela_c, columns=("id", "nome", "qtd", "total", "status"), show="headings", selectmode="extended")
        for col, t in zip(("id", "nome", "qtd", "total", "status"), ("ID", "ITEM", "QUANTIDADE", "TOTAL ESTIMADO", "STATUS DE AQUISIÇÃO")): 
            self.tree_compra.heading(col, text=t)
            self.tree_compra.column(col, anchor="center" if col in ("id", "qtd", "status") else "w")
        self.tree_compra.pack(fill="both", expand=True, padx=5, pady=5)
        
        def add():
            try:
                self.controller.adicionar_item_compra(self.e_item.get(), int(self.e_q.get()), float(self.e_est.get()))
                self.atualizar_compras(); self.e_item.delete(0, tk.END); self.e_q.delete(0, tk.END); self.e_est.delete(0, tk.END)
            except ValueError: pass

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
            if not sel: return
            val = self.tree_compra.item(sel[0])['values']
            item_id = int(val[0])
            item = self.controller.lista_compras[item_id]
            
            self.e_item.delete(0, tk.END); self.e_item.insert(0, item.nome)
            self.e_q.delete(0, tk.END); self.e_q.insert(0, str(item.quantidade))
            self.e_est.delete(0, tk.END); self.e_est.insert(0, str(item.estimado))
            
            def salvar_edicao():
                try:
                    self.controller.editar_item_compra(item_id, self.e_item.get(), int(self.e_q.get()), float(self.e_est.get()))
                    self.atualizar_compras()
                    self.e_item.delete(0, tk.END); self.e_q.delete(0, tk.END); self.e_est.delete(0, tk.END)
                    btn_add_compra.config(text="Adicionar na Lista", command=add)
                except ValueError: pass
            btn_add_compra.config(text="Salvar Alteração", command=salvar_edicao)

        btn_add_compra = ttk.Button(f_add, text="Adicionar na Lista", command=add)
        btn_add_compra.pack(side="left", padx=15)

        f_btn = tk.Frame(tabela_c, bg="white"); f_btn.pack(fill="x", side="bottom", pady=5)
        ttk.Button(f_btn, text="🔄 Alternar Status (Pendente/Comprado)", command=toggle_multiplos).pack(side="left", padx=5)
        ttk.Button(f_btn, text="🗑️ Remover Pedidos", style="Danger.TButton", command=deletar_multiplos).pack(side="left", padx=5)
        ttk.Button(f_btn, text="✏️ Editar Item", command=editar_compra).pack(side="left", padx=5)

    def atualizar_compras(self):
        for i in self.tree_compra.get_children(): self.tree_compra.delete(i)
        for i in self.controller.lista_compras.values():
            self.tree_compra.insert("", "end", values=(i.id, i.nome, i.quantidade, f"R$ {i.quantidade*i.estimado:.2f}", "✅ Comprado" if i.comprado else "⏳ Pendente"))
    