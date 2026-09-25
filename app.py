import customtkinter as ctk
from tkinter import messagebox

import produto as modulo_produto
import estoque as modulo_estoque
from produto import Produto
from estoque import Estoque
from banco_de_dados import BancoDeDados          

from aba_cadastrar import AbaCadastrar
from aba_buscar import AbaBuscar
from aba_listar import AbaListar

if "categoria" not in Produto.__init__.__code__.co_varnames:
    raise SystemExit("produto.py desatualizado (sem 'categoria').")
if not hasattr(Estoque(), "categorias"):
    raise SystemExit("estoque.py desatualizado (sem 'categorias').")


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AppEstoque(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciamento de Estoque")
        self.geometry("950x750")

        self.estoque = Estoque()

        
        self.bd = BancoDeDados("produtos.db", estoque=self.estoque)
        
        self.abas = ctk.CTkTabview(
            self,
            segmented_button_selected_color="#A37BD6",
            segmented_button_selected_hover_color="#8358BE",
        )
        self.abas.pack(fill="both", expand=True, padx=10, pady=10)

        tab_cadastrar = self.abas.add("Cadastrar")
        tab_buscar = self.abas.add("Consultar")
        tab_listar = self.abas.add("Listar no Estoque")

        self.aba_cadastrar = AbaCadastrar(tab_cadastrar, self)
        self.aba_buscar = AbaBuscar(tab_buscar, self)
        self.aba_listar = AbaListar(tab_listar, self)

    def criar_categoria(self):
        dialogo = ctk.CTkInputDialog(text="Nome da nova categoria:", title="Nova categoria")
        nome = dialogo.get_input()
        if not nome:
            return None
        if self.estoque.criar_categoria(nome):
            self.atualizar_categorias()
            self.bd.sincronizar_do_estoque()
            return nome.strip()
        messagebox.showerror("Erro", "Categoria vazia ou já existe.")
        return None

    def atualizar_categorias(self):
        self.aba_cadastrar.atualizar_categoria_values(self.estoque.categorias)
        self.aba_listar.atualizar_categoria_values(self.estoque.categorias)

    def refresh_listar(self):
        """Ponto único de sincronização: chamado após cadastrar/alterar."""
        self.bd.sincronizar_do_estoque()
        self.aba_listar.acao_listar()


if __name__ == "__main__":
    app = AppEstoque()
    app.mainloop()