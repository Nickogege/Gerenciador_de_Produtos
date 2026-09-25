import customtkinter as ctk
from tkinter import messagebox

from helpers import centralizar_em


class PopupExcluir(ctk.CTkToplevel):
    """Popup de confirmação para excluir um produto do estoque."""

    def __init__(self, app, prod, ao_confirmar):
        super().__init__(app)
        self.app = app
        self.estoque = app.estoque
        self.prod = prod
        self.ao_confirmar = ao_confirmar

        self.title("Confirmar Exclusão")
        self.resizable(False, False)
        centralizar_em(self, app, 420, 220)
        self.transient(app)
        self.after(100, self.grab_set)
        self.after(120, self.focus)

        self._montar()

    def _montar(self):
        ctk.CTkLabel(
            self,
            text="Deseja realmente excluir este produto?",
            font=("Arial", 14, "bold"),
        ).pack(pady=(20, 8), padx=20)

        ctk.CTkLabel(
            self,
            text=(
                f"Código: {self.prod.codigo}\n"
                f"Nome: {self.prod.nome}\n"
                f"Categoria: {self.prod.categoria}\n"
                f"Quantidade: {self.prod.quantidade}"
            ),
            justify="left",
        ).pack(pady=4, padx=20)

        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.pack(pady=18)

        ctk.CTkButton(
            frame_botoes,
            text="Cancelar",
            width=110,
            fg_color="#555555",
            hover_color="#333333",
            command=self.destroy,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_botoes,
            text="Excluir",
            width=110,
            fg_color="#C0392B",
            hover_color="#922B21",
            command=self.confirmar,
        ).pack(side="left", padx=10)

    def confirmar(self):
        codigo = self.prod.codigo
        if self.estoque.remover_produto(codigo):
            self.destroy()
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            self.ao_confirmar()
        else:
            messagebox.showerror(
                "Erro", "Não foi possível excluir o produto.", parent=self
            )