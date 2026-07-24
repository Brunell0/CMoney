import tkinter as tk
from tkinter import ttk
from controllers.sistema_controller import SistemaController
from views.auth_view import AuthView
from views.main_view import MainView

class AppGastoEmpresa:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Gastos Financeiros CMoney")
        self.root.geometry("850x600")
        
        # Inicia o Controller global
        self.controller = SistemaController()
        
        # Configurações de estilo global
        style = ttk.Style()
        style.theme_use("clam")
        
        self.current_view = None
        self.mostrar_login()

    def clear_view(self):
        if self.current_view:
            self.current_view.destroy()

    def mostrar_login(self):
        self.clear_view()
        self.controller.usuario_atual = None
        # Injeta o controller e o callback de sucesso na View de Autenticação
        self.current_view = AuthView(self.root, self.controller, self.mostrar_home)

    def mostrar_home(self):
        self.clear_view()
        # Injeta o controller e o callback de logout na View Principal
        self.current_view = MainView(self.root, self.controller, self.mostrar_login)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGastoEmpresa(root)
    root.mainloop()