import customtkinter as ctk

from helpers import formatar_preco, TODAS
from popup_excluir import PopupExcluir


class AbaListar:
    """Aba de listagem e filtro dos produtos em estoque."""

    # (texto, largura, anchor)
    COLUNAS = [
        ("Código",       80,  "center"),
        ("Nome",         260, "w"),
        ("Categoria",    150, "center"),
        ("Preço (R$)",   110, "center"),
        ("Quantidade",   100, "center"),
        ("Ações",         60, "center"),
    ]

    def __init__(self, aba, app):
        self.app = app
        self.estoque = app.estoque
        self._montar(aba)
        self.acao_listar()

    # ---------- construção ----------
    def _montar(self, aba):
        # Filtro por categoria
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

        # Cabeçalho
        frame_header = ctk.CTkFrame(aba, fg_color="#3a3a3a", corner_radius=6)
        frame_header.pack(fill="x", pady=(0, 4))
        for texto, largura, anchor in self.COLUNAS:
            ctk.CTkLabel(
                frame_header,
                text=texto,
                width=largura,
                anchor=anchor,
                font=("Arial", 12, "bold"),
            ).pack(side="left", padx=4, pady=6)

        # Área de linhas (scrollable)
        self.frame_lista = ctk.CTkScrollableFrame(aba, fg_color="transparent")
        self.frame_lista.pack(fill="both", expand=True)

        self.lbl_contagem = ctk.CTkLabel(aba, text="")
        self.lbl_contagem.pack(pady=(8, 0))

        ctk.CTkButton(
            aba, text="Atualizar Lista", command=self.acao_listar,
            fg_color="#A37BD6", hover_color="#8358BE",
        ).pack(pady=10)

    # ---------- API usada pelo App ----------
    def atualizar_categoria_values(self, categorias):
        self.cmb_filtro.configure(values=[TODAS] + categorias)

    def acao_listar(self, _=None):
        # Limpa linhas antigas
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        filtro = self.cmb_filtro.get()
        exibidos = 0

        for p in self.estoque.produtos:
            if filtro != TODAS and p.categoria != filtro:
                continue
            self._criar_linha(p)
            exibidos += 1

        self.lbl_contagem.configure(text=f"Exibindo {exibidos} produto(s)")

    # ---------- linha ----------
    def _criar_linha(self, prod):
        linha = ctk.CTkFrame(self.frame_lista, fg_color="#2b2b2b", corner_radius=6)
        linha.pack(fill="x", pady=2, padx=2)

        valores = [
            (str(prod.codigo),               self.COLUNAS[0][1], self.COLUNAS[0][2]),
            (prod.nome,                      self.COLUNAS[1][1], self.COLUNAS[1][2]),
            (prod.categoria,                 self.COLUNAS[2][1], self.COLUNAS[2][2]),
            (formatar_preco(prod.preco),     self.COLUNAS[3][1], self.COLUNAS[3][2]),
            (str(prod.quantidade),           self.COLUNAS[4][1], self.COLUNAS[4][2]),
        ]
        for texto, largura, anchor in valores:
            ctk.CTkLabel(
                linha, text=texto, width=largura, anchor=anchor,
            ).pack(side="left", padx=4, pady=6)

        ctk.CTkButton(
            linha,
            text="🗑",
            width=self.COLUNAS[5][1] - 10,
            height=28,
            fg_color="#C0392B",
            hover_color="#922B21",
            command=lambda p=prod: self._abrir_popup_excluir(p),
        ).pack(side="left", padx=4, pady=6)

    # ---------- exclusão ----------
    def _abrir_popup_excluir(self, prod):
        PopupExcluir(self.app, prod, ao_confirmar=self._apos_excluir)

    def _apos_excluir(self):
        # Sincroniza CSV + recarrega a lista
        self.app.refresh_listar()