import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class RelatoriosView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.montar_tela()

    def montar_tela(self):
        # 🏢 Card de Exportação
        card = tk.Frame(self, bg="white", bd=1, relief="solid")
        card.configure(highlightthickness=0)
        card.pack(pady=40, padx=50, fill="x")
        
        lbl = tk.Label(card, text="Central de Exportação de Relatórios", font=("Segoe UI", 14, "bold"), bg="white", fg="#1e3a8a")
        lbl.pack(pady=20)
        
        lbl_info = tk.Label(card, text="A exportação gera um arquivo .csv (planilha do Excel),\ncontendo tabelas secundárias de compras consolidadas por categoria.", font=("Segoe UI", 10), bg="white", fg="#4b5563")
        lbl_info.pack(pady=5)

        ttk.Button(card, text="💾  Exportar Relatório Excel (.csv)", command=self.gerar_excel, padding=[20,10]).pack(pady=25)
        
        # 👥 Créditos no Rodapé
        grupo_f = tk.Frame(self, bg="#f8f9fa")
        grupo_f.pack(side="bottom", anchor="w", padx=25, pady=25)
        tk.Label(grupo_f, text="EQUIPE DE PROGRAMAÇÃO ORIENTADA A OBJETOS:", font=("Segoe UI", 9, "bold"), fg="#6b7280", bg="#f8f9fa").pack(anchor="w")
        
        membros = ["• Bruno Antonello", "• Felipe Lima", "• João Marcelo Turolla", "• Vitória Akemi Nakai"]
        for m in membros:
            tk.Label(grupo_f, text=m, font=("Segoe UI", 9), fg="#6b7280", bg="#f8f9fa").pack(anchor="w", padx=10)

    def gerar_excel(self):
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Excel CSV (Com separador)", "*.csv")],
            title="Salvar Relatório Excel"
        )
        if arquivo:
            self.controller.gerar_excel_csv(arquivo)
            messagebox.showinfo("Sucesso", "Relatório de dados criado e pronto para análise corporativa!")