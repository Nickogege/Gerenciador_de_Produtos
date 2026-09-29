# popup_excluir.py
import customtkinter as ctk
from tkinter import messagebox

from helpers import centralizar_em
from tema import paleta


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
        centralizar_em(self, app, 420, 240)
        self.transient(app)
        self.after(100, self.grab_set)
        self.after(120, self.focus)

        self._montar()
        self._aplicar_tema()

    def _montar(self):
        self.lbl_titulo = ctk.CTkLabel(
            self,
            text="Deseja realmente excluir este produto?",
            font=("Arial", 14, "bold"),
        )
        self.lbl_titulo.pack(pady=(20, 8), padx=20)

        self.lbl_info = ctk.CTkLabel(
            self,
            text=(
                f"Código: {self.prod.codigo}\n"
                f"Nome: {self.prod.nome}\n"
                f"Categoria: {self.prod.categoria}\n"
                f"Quantidade: {self.prod.quantidade}"
            ),
            justify="left",
        )
        self.lbl_info.pack(pady=4, padx=20)

        self.frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botoes.pack(pady=18)

        self.btn_cancelar = ctk.CTkButton(
            self.frame_botoes, text="Cancelar", width=110,
            command=self.destroy,
        )
        self.btn_cancelar.pack(side="left", padx=10)

        self.btn_excluir = ctk.CTkButton(
            self.frame_botoes, text="Excluir", width=110,
            command=self.confirmar,
        )
        self.btn_excluir.pack(side="left", padx=10)

    def _aplicar_tema(self):
        p = paleta()
        self.configure(fg_color=p["fundo"])
        self.lbl_titulo.configure(text_color=p["texto"])
        self.lbl_info.configure(text_color=p["texto"])
        self.btn_cancelar.configure(
            fg_color=p["botao_neutro"], hover_color=p["botao_neutro_hover"],
            text_color=p["texto"],
        )
        self.btn_excluir.configure(
            fg_color=p["botao_perigo"], hover_color=p["botao_perigo_hover"],
            text_color=p["botao_texto"],
        )

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