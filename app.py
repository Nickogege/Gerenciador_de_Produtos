# app.py
import customtkinter as ctk
from tkinter import messagebox

import produto as modulo_produto
import estoque as modulo_estoque
from produto import Produto
from estoque import Estoque

from banco import BancoDados

from aba_cadastrar import AbaCadastrar
from aba_listar import AbaListar

from helpers import validar_texto_sem_numeros, capitalizar_nome
import config
from tema import paleta

if "categoria" not in Produto.__init__.__code__.co_varnames:
    raise SystemExit("produto.py desatualizado (sem 'categoria').")


ctk.set_default_color_theme("blue")


class AppEstoque(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciamento de Estoque")
        self.geometry("950x780")

        self.cfg = config.carregar()
        ctk.set_appearance_mode(self.cfg["tema"])

        # 1) Banco
        self.bd = BancoDados("estoque.db")
        self.estoque = Estoque(bd=self.bd)
        self.bd.carregar_para_estoque(self.estoque)

        # 2) Barra superior
        self._montar_barra_topo()

        # 3) Abas
        self.abas = ctk.CTkTabview(self)
        self.abas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tab_cadastrar = self.abas.add("Cadastrar")
        tab_listar = self.abas.add("Listar no Estoque")

        self.aba_cadastrar = AbaCadastrar(tab_cadastrar, self)
        self.aba_listar = AbaListar(tab_listar, self)

        # 4) Aplica paleta inicial
        self._aplicar_tema()

        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    # ---------- barra de topo ----------
    def _montar_barra_topo(self):
        self.barra = ctk.CTkFrame(self, fg_color="transparent")
        self.barra.pack(fill="x", padx=10, pady=(10, 0))

        self.opt_tema = ctk.CTkOptionMenu(
            self.barra,
            values=["Escuro", "Claro"],
            width=110,
            command=self._mudar_tema,
        )
        self.opt_tema.set("Escuro" if self.cfg["tema"] == "dark" else "Claro")
        self.opt_tema.pack(side="right")

        self.lbl_tema = ctk.CTkLabel(self.barra, text="Tema:")
        self.lbl_tema.pack(side="right", padx=(0, 8))

    # ---------- tema ----------
    def _mudar_tema(self, escolha):
        tema = "dark" if escolha == "Escuro" else "light"
        if tema == self.cfg["tema"]:
            return
        self.cfg["tema"] = tema
        config.salvar(self.cfg)
        ctk.set_appearance_mode(tema)
        self._aplicar_tema()
        self.aba_listar.acao_listar()

    def _aplicar_tema(self):
        p = paleta()
        self.configure(fg_color=p["fundo"])

        # barra de topo
        self.opt_tema.configure(
            fg_color=p["botao"],
            button_color=p["botao_hover"],
            button_hover_color=p["botao_hover"],
            text_color=p["botao_texto"],
        )
        self.lbl_tema.configure(text_color=p["texto"])

        # abas
        self.abas.configure(
            fg_color=p["fundo"],
            segmented_button_selected_color=p["aba_sel"],
            segmented_button_selected_hover_color=p["aba_sel_hover"],
            segmented_button_unselected_color=p["aba_unsel"],
            segmented_button_unselected_hover_color=p["aba_unsel_hover"],
            text_color=p["texto"],
        )
        for nome in ("Cadastrar", "Listar no Estoque"):
            try:
                self.abas.tab(nome).configure(fg_color=p["fundo"])
            except Exception:
                pass

        # repassa o tema para as abas
        self.aba_cadastrar.aplicar_tema(p)
        self.aba_listar.aplicar_tema(p)

    # ---------- categorias ----------
    def criar_categoria(self):
        dialogo = ctk.CTkInputDialog(
            text="Nome da nova categoria:", title="Nova categoria"
        )
        nome = dialogo.get_input()
        if nome is None:
            return None
        nome = nome.strip()
        if not nome:
            messagebox.showerror("Erro", "Categoria vazia.")
            return None
        if not validar_texto_sem_numeros(nome):
            messagebox.showerror("Erro", "A categoria não pode conter números.")
            return None
        nome = capitalizar_nome(nome)
        if self.estoque.criar_categoria(nome):
            self.atualizar_categorias()
            return nome
        messagebox.showerror("Erro", "Categoria já existe.")
        return None

    def atualizar_categorias(self):
        self.aba_cadastrar.atualizar_categoria_values(self.estoque.categorias)
        self.aba_listar.atualizar_categoria_values(self.estoque.categorias)

    def refresh_listar(self):
        self.aba_listar.acao_listar()

    def _ao_fechar(self):
        try:
            self.bd.fechar()
        finally:
            self.destroy()


if __name__ == "__main__":
    app = AppEstoque()
    app.mainloop()