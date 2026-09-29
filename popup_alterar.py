import customtkinter as ctk
from tkinter import messagebox

from helpers import (
    formatar_preco, ler_numero, centralizar_em,
    capitalizar_nome, validar_decimal, validar_inteiro,
)


class PopupAlterar(ctk.CTkToplevel):
    """Popup para alterar nome, preço, quantidade e categoria de um produto."""

    def __init__(self, app, prod, ao_salvar):
        super().__init__(app)
        self.app = app
        self.estoque = app.estoque
        self.prod = prod
        self.ao_salvar = ao_salvar

        self.title("Alterar Produto")
        centralizar_em(self, app, 450, 380)
        self.transient(app)
        self.after(100, self.grab_set)
        self.after(120, self.focus)

        self._montar()

    def _montar(self):
        prod = self.prod

        ctk.CTkLabel(self, text="Código:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.ent_codigo = ctk.CTkEntry(self, width=200)
        self.ent_codigo.grid(row=0, column=1, padx=10, pady=8)
        self.ent_codigo.insert(0, str(prod.codigo))
        self.ent_codigo.configure(state="disabled")

        ctk.CTkLabel(self, text="Nome:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.ent_nome = ctk.CTkEntry(self, width=200)
        self.ent_nome.grid(row=1, column=1, padx=10, pady=8)
        self.ent_nome.insert(0, prod.nome)
        self.ent_nome.bind("<FocusOut>", self._capitalizar_nome)
        self.ent_nome.bind("<Return>", self._capitalizar_nome)

        ctk.CTkLabel(self, text="Preço (R$):").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        vcmd_preco = (self.register(self._validar_preco), "%P")
        self.ent_preco = ctk.CTkEntry(self, width=200, validate="key", validatecommand=vcmd_preco)
        self.ent_preco.grid(row=2, column=1, padx=10, pady=8)
        self.ent_preco.insert(0, formatar_preco(prod.preco))

        ctk.CTkLabel(self, text="Quantidade:").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        vcmd_qtd = (self.register(self._validar_quantidade), "%P")
        self.ent_qtd = ctk.CTkEntry(self, width=200, validate="key", validatecommand=vcmd_qtd)
        self.ent_qtd.grid(row=3, column=1, padx=10, pady=8)
        self.ent_qtd.insert(0, str(prod.quantidade))

        ctk.CTkLabel(self, text="Categoria:").grid(row=4, column=0, padx=10, pady=8, sticky="w")
        self.cmb_cat = ctk.CTkComboBox(
            self, values=self._categorias_disponiveis(), state="readonly", width=200
        )
        self.cmb_cat.set(prod.categoria)
        self.cmb_cat.grid(row=4, column=1, padx=10, pady=8)

        btn_nova = ctk.CTkButton(
            self, text="+ Nova", width=70, fg_color="#A37BD6", hover_color="#8358BE",
            command=self.acao_nova_categoria,
        )
        btn_nova.grid(row=4, column=2, padx=5, pady=8)

        btn_salvar = ctk.CTkButton(
            self, text="Salvar Alterações", fg_color="#A37BD6", hover_color="#8358BE",
            command=self.salvar_alteracoes,
        )
        btn_salvar.grid(row=5, column=0, columnspan=3, pady=20)

    # ---------- categorias ----------
    def _categorias_disponiveis(self):
        """Oculta 'sem categoria' quando existirem outras categorias."""
        cats = self.estoque.categorias
        outras = [c for c in cats if c.lower() != "sem categoria"]
        if outras:
            return outras
        return cats

    # ---------- validações ----------
    def _validar_preco(self, texto):
        return validar_decimal(texto)

    def _validar_quantidade(self, texto):
        return validar_inteiro(texto)

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
            self.cmb_cat.configure(values=self._categorias_disponiveis())
            self.cmb_cat.set(nome)

    def salvar_alteracoes(self):
        prod = self.prod
        nome = self.ent_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Digite um nome para o produto.", parent=self)
            return

        nome = capitalizar_nome(nome)

        try:
            preco = ler_numero(self.ent_preco.get(), float)
            quantidade = ler_numero(self.ent_qtd.get(), int)
        except ValueError:
            messagebox.showerror(
                "Erro", "Digite valores válidos para preço e quantidade.", parent=self
            )
            return

        if preco <= 0:
            messagebox.showerror("Erro", "O preço deve ser maior que zero.", parent=self)
            return
        if quantidade < 0:
            messagebox.showerror("Erro", "A quantidade não pode ser negativa.", parent=self)
            return

        prod.nome = nome
        prod.categoria = self.cmb_cat.get()

        if not self.estoque.alterar_produto(prod.codigo, preco, quantidade):
            messagebox.showerror("Erro", "Produto não encontrado no estoque.", parent=self)
            return

        self.destroy()
        messagebox.showinfo("Sucesso", "Produto alterado com sucesso!")
        self.ao_salvar()