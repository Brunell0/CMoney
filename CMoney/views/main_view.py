import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from views.relatorios_view import RelatoriosView
from views.logs_view import LogsView
from views.compras_view import ComprasView
from views.gerencia_view import GerenciaView

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
        self.aba_gerencia = GerenciaView(self.notebook, self.controller)
        self.aba_compras = ComprasView(self.notebook, self.controller)
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
        self.aba_gerencia.atualizar_cats()
        self.aba_compras.atualizar_compras()
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