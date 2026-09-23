import customtkinter as ctk
from tkinter import messagebox

from produto import Produto
from helpers import ler_numero


class AbaCadastrar:
    """Aba de cadastro de novos produtos."""

    def __init__(self, aba, app):
        self.app = app
        self.estoque = app.estoque
        self._montar(aba)

    def _montar(self, aba):
        ctk.CTkLabel(aba, text="Código:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.ent_codigo = ctk.CTkEntry(aba, width=220)
        self.ent_codigo.grid(row=0, column=1, padx=10, pady=8)

        ctk.CTkLabel(aba, text="Nome do Produto:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.ent_nome = ctk.CTkEntry(aba, width=220)
        self.ent_nome.grid(row=1, column=1, padx=10, pady=8)

        ctk.CTkLabel(aba, text="Preço (R$):").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.ent_preco = ctk.CTkEntry(aba, width=220)
        self.ent_preco.grid(row=2, column=1, padx=10, pady=8)

        ctk.CTkLabel(aba, text="Quantidade:").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.ent_qtd = ctk.CTkEntry(aba, width=220)
        self.ent_qtd.grid(row=3, column=1, padx=10, pady=8)

        ctk.CTkLabel(aba, text="Categoria:").grid(row=4, column=0, padx=10, pady=8, sticky="w")
        self.cmb_categoria = ctk.CTkComboBox(
            aba, values=self.estoque.categorias, state="readonly", width=220
        )
        self.cmb_categoria.set(self.estoque.categorias[0])
        self.cmb_categoria.grid(row=4, column=1, padx=10, pady=8)

        btn_nova_cat = ctk.CTkButton(
            aba, text="+ Nova", width=70, command=self.acao_nova_categoria,
            fg_color="#A37BD6", hover_color="#8358BE",
        )
        btn_nova_cat.grid(row=4, column=2, padx=5, pady=8)

        btn_cadastrar = ctk.CTkButton(
            aba, text="Cadastrar Produto", command=self.acao_cadastrar,
            fg_color="#A37BD6", hover_color="#8358BE",
        )
        btn_cadastrar.grid(row=5, column=0, columnspan=2, pady=20)

    def atualizar_categoria_values(self, categorias):
        """Chamado pelo App quando a lista de categorias muda em qualquer aba."""
        self.cmb_categoria.configure(values=categorias)

    def acao_nova_categoria(self):
        nome = self.app.criar_categoria()
        if nome:
            self.cmb_categoria.set(nome)

    def acao_cadastrar(self):
        nome = self.ent_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Digite um nome para o produto.")
            return

        try:
            codigo = ler_numero(self.ent_codigo.get(), int)
            preco = ler_numero(self.ent_preco.get(), float)
            quantidade = ler_numero(self.ent_qtd.get(), int)
        except ValueError:
            messagebox.showerror(
                "Erro", "Por favor, digite números válidos para código, preço e quantidade."
            )
            return

        if codigo <= 0:
            messagebox.showerror("Erro", "O código deve ser maior que zero.")
            return
        if preco <= 0:
            messagebox.showerror("Erro", "O preço deve ser maior que zero.")
            return
        if quantidade < 0:
            messagebox.showerror("Erro", "A quantidade não pode ser negativa.")
            return

        novo_prod = Produto(codigo, nome, preco, quantidade, self.cmb_categoria.get())

        if self.estoque.cadastrar_produto(novo_prod):
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            for campo in (self.ent_codigo, self.ent_nome, self.ent_preco, self.ent_qtd):
                campo.delete(0, "end")
            self.cmb_categoria.set(self.estoque.categorias[0])
            self.app.refresh_listar()
        else:
            messagebox.showerror("Erro", "Já existe um produto com esse código.")
