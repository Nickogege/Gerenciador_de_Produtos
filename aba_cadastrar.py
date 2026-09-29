# aba_cadastrar.py
import customtkinter as ctk
from tkinter import messagebox

from produto import Produto
from helpers import (
    ler_numero, capitalizar_nome,
    validar_inteiro, validar_decimal,
)


class AbaCadastrar:
    """Aba de cadastro de novos produtos."""

    def __init__(self, aba, app):
        self.app = app
        self.estoque = app.estoque
        self.aba = aba
        self._widgets_texto = []  # labels para repintar
        self._montar(aba)

    def _montar(self, aba):
        self.lbl_codigo = ctk.CTkLabel(aba, text="Código de Barras:")
        self.lbl_codigo.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        vcmd_codigo = (aba.register(self._validar_codigo), "%P")
        self.ent_codigo = ctk.CTkEntry(aba, width=220, validate="key", validatecommand=vcmd_codigo)
        self.ent_codigo.grid(row=0, column=1, padx=10, pady=8)

        self.lbl_nome = ctk.CTkLabel(aba, text="Nome do Produto:")
        self.lbl_nome.grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.ent_nome = ctk.CTkEntry(aba, width=220)
        self.ent_nome.grid(row=1, column=1, padx=10, pady=8)
        self.ent_nome.bind("<FocusOut>", self._capitalizar_nome)
        self.ent_nome.bind("<Return>", self._capitalizar_nome)

        self.lbl_preco = ctk.CTkLabel(aba, text="Preço (R$):")
        self.lbl_preco.grid(row=2, column=0, padx=10, pady=8, sticky="w")
        vcmd_preco = (aba.register(self._validar_preco), "%P")
        self.ent_preco = ctk.CTkEntry(aba, width=220, validate="key", validatecommand=vcmd_preco)
        self.ent_preco.grid(row=2, column=1, padx=10, pady=8)

        self.lbl_qtd = ctk.CTkLabel(aba, text="Quantidade:")
        self.lbl_qtd.grid(row=3, column=0, padx=10, pady=8, sticky="w")
        vcmd_qtd = (aba.register(self._validar_quantidade), "%P")
        self.ent_qtd = ctk.CTkEntry(aba, width=220, validate="key", validatecommand=vcmd_qtd)
        self.ent_qtd.grid(row=3, column=1, padx=10, pady=8)

        self.lbl_cat = ctk.CTkLabel(aba, text="Categoria:")
        self.lbl_cat.grid(row=4, column=0, padx=10, pady=8, sticky="w")
        self.cmb_categoria = ctk.CTkComboBox(
            aba, values=self._categorias_disponiveis(), state="readonly", width=220
        )
        self.cmb_categoria.set(self._categorias_disponiveis()[0])
        self.cmb_categoria.grid(row=4, column=1, padx=10, pady=8)

        self.btn_nova_cat = ctk.CTkButton(
            aba, text="+ Nova", width=70, command=self.acao_nova_categoria,
        )
        self.btn_nova_cat.grid(row=4, column=2, padx=5, pady=8)

        self.btn_cadastrar = ctk.CTkButton(
            aba, text="Cadastrar Produto", command=self.acao_cadastrar,
        )
        self.btn_cadastrar.grid(row=5, column=0, columnspan=2, pady=20)

        self._widgets_texto = [
            self.lbl_codigo, self.lbl_nome, self.lbl_preco,
            self.lbl_qtd, self.lbl_cat,
        ]
        self._entries = [self.ent_codigo, self.ent_nome, self.ent_preco, self.ent_qtd]

    # ---------- tema ----------
    def aplicar_tema(self, p):
        self.aba.configure(fg_color=p["fundo"])
        for lbl in self._widgets_texto:
            lbl.configure(text_color=p["texto"])
        for ent in self._entries:
            ent.configure(
                fg_color=p["entrada"],
                border_color=p["entrada_borda"],
                text_color=p["texto"],
            )
        self.cmb_categoria.configure(
            fg_color=p["entrada"],
            border_color=p["entrada_borda"],
            text_color=p["texto"],
            button_color=p["botao"],
            button_hover_color=p["botao_hover"],
            dropdown_fg_color=p["entrada"],
            dropdown_text_color=p["texto"],
            dropdown_hover_color=p["fundo_frame_hover"],
        )
        self.btn_nova_cat.configure(
            fg_color=p["botao"], hover_color=p["botao_hover"],
            text_color=p["botao_texto"],
        )
        self.btn_cadastrar.configure(
            fg_color=p["botao"], hover_color=p["botao_hover"],
            text_color=p["botao_texto"],
        )

    # ---------- categorias ----------
    def _categorias_disponiveis(self):
        cats = self.estoque.categorias
        outras = [c for c in cats if c.lower() != "sem categoria"]
        if outras:
            return outras
        return cats

    def atualizar_categoria_values(self, categorias):
        valores = self._categorias_disponiveis()
        self.cmb_categoria.configure(values=valores)
        if self.cmb_categoria.get() not in valores:
            self.cmb_categoria.set(valores[0])

    # ---------- validações ----------
    def _validar_codigo(self, texto):
        return validar_inteiro(texto)

    def _validar_quantidade(self, texto):
        return validar_inteiro(texto)

    def _validar_preco(self, texto):
        return validar_decimal(texto)

    # ---------- nome ----------
    def _capitalizar_nome(self, _event=None):
        atual = self.ent_nome.get()
        if not atual.strip():
            return
        novo = capitalizar_nome(atual)
        if novo != atual:
            self.ent_nome.delete(0, "end")
            self.ent_nome.insert(0, novo)

    # ---------- ações ----------
    def acao_nova_categoria(self):
        nome = self.app.criar_categoria()
        if nome:
            self.cmb_categoria.set(nome)

    def acao_cadastrar(self):
        nome = self.ent_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Digite um nome para o produto.")
            return
        nome = capitalizar_nome(nome)

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
            self.cmb_categoria.set(self._categorias_disponiveis()[0])
            self.app.refresh_listar()
        else:
            messagebox.showerror("Erro", "Já existe um produto com esse código.")