import customtkinter as ctk
from tkinter import ttk

from helpers import formatar_preco, TODAS


class AbaListar:
    """Aba de listagem e filtro dos produtos em estoque."""

    def __init__(self, aba, app):
        self.app = app
        self.estoque = app.estoque
        self._montar(aba)
        self.acao_listar()

    def _montar(self, aba):
        frame_filtro = ctk.CTkFrame(aba, fg_color="transparent")
        frame_filtro.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(frame_filtro, text="Categoria:").pack(side="left", padx=(0, 8))
        self.cmb_filtro = ctk.CTkComboBox(
            frame_filtro,
            values=[TODAS] + self.estoque.categorias,
            state="readonly",
            width=220,
            command=self.acao_listar, 
        )
        self.cmb_filtro.set(TODAS)
        self.cmb_filtro.pack(side="left")

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=32,
            borderwidth=0,
            font=("Arial", 12),
        )
        estilo.configure(
            "Treeview.Heading",
            background="#3a3a3a",
            foreground="white",
            relief="flat",
            font=("Arial", 12, "bold"),
        )
        estilo.map("Treeview", background=[("selected", "#1f6aa5")])

        frame_tabela = ctk.CTkFrame(aba)
        frame_tabela.pack(fill="both", expand=True)

        colunas = ("codigo", "nome", "categoria", "preco", "quantidade")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings")

        
        self.tabela.heading("codigo", text="Código", anchor="center")
        self.tabela.heading("nome", text="Nome", anchor="center")
        self.tabela.heading("categoria", text="Categoria", anchor="center")
        self.tabela.heading("preco", text="Preço (R$)", anchor="center")
        self.tabela.heading("quantidade", text="Quantidade", anchor="center")

        self.tabela.column("codigo", width=90, anchor="center")
        self.tabela.column("nome", width=320, anchor="center")
        self.tabela.column("categoria", width=170, anchor="center")
        self.tabela.column("preco", width=130, anchor="center")
        self.tabela.column("quantidade", width=120, anchor="center")

        barra = ctk.CTkScrollbar(frame_tabela, command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)

        barra.pack(side="right", fill="y")
        self.tabela.pack(side="left", fill="both", expand=True)

        self.lbl_contagem = ctk.CTkLabel(aba, text="")
        self.lbl_contagem.pack(pady=(8, 0))

        btn_atualizar = ctk.CTkButton(
            aba, text="Atualizar Lista", command=self.acao_listar,
            fg_color="#A37BD6", hover_color="#8358BE",
        )
        btn_atualizar.pack(pady=10)

    def atualizar_categoria_values(self, categorias):
        """Chamado pelo App quando a lista de categorias muda em qualquer aba."""
        self.cmb_filtro.configure(values=[TODAS] + categorias)

    def acao_listar(self, _=None):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        filtro = self.cmb_filtro.get()
        exibidos = 0

        for p in self.estoque.produtos:
            if filtro != TODAS and p.categoria != filtro:
                continue
            self.tabela.insert(
                "", "end",
                values=(p.codigo, p.nome, p.categoria, formatar_preco(p.preco), p.quantidade),
            )
            exibidos += 1

        self.lbl_contagem.configure(text=f"Exibindo {exibidos} produto(s)")
