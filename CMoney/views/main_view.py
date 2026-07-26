import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from views.relatorios_view import RelatoriosView
from views.logs_view import LogsView
from views.compras_view import ComprasView
from views.gerencia_view import GerenciaView
from views.registros_view import RegistrosView

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
        
        self.aba_planilhas = RegistrosView(self.notebook, self.controller)
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
        self.aba_planilhas.atualizar_tabela_planilha()
        self.aba_gerencia.atualizar_cats()
        self.aba_compras.atualizar_compras()
        self.aba_logs.atualizar_logs()