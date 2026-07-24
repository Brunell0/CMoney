import tkinter as tk
from tkinter import ttk, messagebox

class AuthView(tk.Frame):
    def __init__(self, parent, controller, on_success):
        super().__init__(parent)
        self.controller = controller
        self.on_success = on_success
        self.pack(fill="both", expand=True)
        self.montar_tela()

    def montar_tela(self):
        frame = ttk.LabelFrame(self, text=" Sign In / Sign Up ", padding=30)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(frame, text="Usuário:").grid(row=0, column=0, pady=5, sticky="e")
        self.ent_user = ttk.Entry(frame)
        self.ent_user.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Senha:").grid(row=1, column=0, pady=5, sticky="e")
        self.ent_pass = ttk.Entry(frame, show="*")
        self.ent_pass.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Perfil (Apenas Cadastro):").grid(row=2, column=0, pady=5, sticky="e")
        self.cb_perfil = ttk.Combobox(frame, values=["Funcionário", "Gerente"], state="readonly")
        self.cb_perfil.set("Funcionário")
        self.cb_perfil.grid(row=2, column=1, pady=5)
        
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="Entrar", command=self.acao_login).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cadastrar", command=self.acao_registro).pack(side="left", padx=5)

    def acao_login(self):
        if self.controller.login(self.ent_user.get(), self.ent_pass.get()):
            self.on_success()
        else:
            messagebox.showerror("Erro", "Login Inválido! Tente admin/admin ou user/user.")

    def acao_registro(self):
        if not self.ent_user.get() or not self.ent_pass.get():
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
        if self.controller.registrar_usuario(self.ent_user.get(), self.ent_pass.get(), self.cb_perfil.get()):
            messagebox.showinfo("Sucesso", "Registrado! Faça login.")
        else:
            messagebox.showerror("Erro", "Usuário já existe.")