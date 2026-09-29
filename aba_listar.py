# aba_listar.py
import customtkinter as ctk
from tkinter import messagebox

from helpers import formatar_preco, TODAS
from busca import BuscaProdutos
from popup_excluir import PopupExcluir
from popup_alterar import PopupAlterar


class AbaListar:
    """Aba de listagem, busca em tempo real e filtro dos produtos em estoque."""

    COLUNAS = [
        ("Código",       80,  "center"),
        ("Nome",         260, "w"),
        ("Categoria",    150, "center"),
        ("Preço (R$)",   110, "center"),
        ("Quantidade",   100, "center"),
        ("Ações",        120, "center"),
    ]

    # cores da linha
    COR_LINHA = "#2b2b2b"
    COR_LINHA_HOVER = "#3a3a3a"

    DEBOUNCE_MS = 200

    def __init__(self, aba, app):
        self.app = app
        self.estoque = app.estoque
        self.busca = BuscaProdutos(self.estoque)

        self._job_busca = None

        self._montar(aba)
        self.acao_listar()

    # ---------- construção ----------
    def _montar(self, aba):
        frame_busca = ctk.CTkFrame(aba, fg_color="transparent")
        frame_busca.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(frame_busca, text="Buscar por código:").pack(side="left", padx=(0, 8))
        vcmd_codigo = (aba.register(self._validar_codigo_busca), "%P")
        self.ent_busca_codigo = ctk.CTkEntry(
            frame_busca, width=120, validate="key", validatecommand=vcmd_codigo,
        )
        self.ent_busca_codigo.pack(side="left", padx=(0, 15))
        self._ligar_busca_tempo_real(self.ent_busca_codigo)

        ctk.CTkLabel(frame_busca, text="Nome:").pack(side="left", padx=(0, 8))
        self.ent_busca_nome = ctk.CTkEntry(frame_busca, width=180)
        self.ent_busca_nome.pack(side="left", padx=(0, 15))
        self._ligar_busca_tempo_real(self.ent_busca_nome)

        ctk.CTkButton(
            frame_busca, text="Limpar", width=80, command=self._limpar_busca,
            fg_color="#555555", hover_color="#333333",
        ).pack(side="left")

        frame_filtro = ctk.CTkFrame(aba, fg_color="transparent")
        frame_filtro.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(frame_filtro, text="Categoria:").pack(side="left", padx=(0, 8))
        self.cmb_filtro = ctk.CTkComboBox(
            frame_filtro,
            values=[TODAS] + self._categorias_para_filtro(),
            state="readonly",
            width=220,
            command=self.acao_buscar,
        )
        self.cmb_filtro.set(TODAS)
        self.cmb_filtro.pack(side="left")

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

        self.frame_lista = ctk.CTkScrollableFrame(aba, fg_color="transparent")
        self.frame_lista.pack(fill="both", expand=True)

        self.lbl_contagem = ctk.CTkLabel(aba, text="")
        self.lbl_contagem.pack(pady=(8, 0))

        ctk.CTkButton(
            aba, text="Atualizar Lista", command=self.acao_listar,
            fg_color="#A37BD6", hover_color="#8358BE",
        ).pack(pady=10)

    # ---------- ligação de eventos ----------
    def _ligar_busca_tempo_real(self, entry):
        entry.bind("<KeyRelease>", self._agendar_busca)
        entry.bind("<<Paste>>", lambda e: self.after(10, self._agendar_busca))
        entry.bind("<<Cut>>",   lambda e: self.after(10, self._agendar_busca))
        entry.bind("<<Clear>>", lambda e: self.after(10, self._agendar_busca))
        entry.bind("<<PasteSelection>>", lambda e: self.after(10, self._agendar_busca))

    def _ligar_hover_linha(self, linha, widgets):
        """Aplica efeito de hover em todos os widgets da linha."""
        def on_enter(_):
            self._pintar_linha(linha, widgets, self.COR_LINHA_HOVER)

        def on_leave(_):
            # evita flicker: só desliga se o mouse realmente saiu da linha
            x, y = linha.winfo_pointerxy()
            widget_sob_mouse = linha.winfo_containing(x, y)
            # se ainda está sob algum widget da linha, ignora
            if widget_sob_mouse is not None:
                atual = widget_sob_mouse
                while atual is not None:
                    if atual is linha:
                        return
                    atual = atual.master
            self._pintar_linha(linha, widgets, self.COR_LINHA)

        for w in widgets:
            w.bind("<Enter>", on_enter, add="+")
            w.bind("<Leave>", on_leave, add="+")

    @staticmethod
    def _pintar_linha(linha, widgets, cor):
        try:
            linha.configure(fg_color=cor)
        except Exception:
            pass
        for w in widgets:
            if isinstance(w, ctk.CTkFrame):
                try:
                    w.configure(fg_color=cor)
                except Exception:
                    pass

    # ---------- categorias ----------
    def _categorias_para_filtro(self):
        cats = self.estoque.categorias
        outras = [c for c in cats if c.lower() != "sem categoria"]
        if outras:
            return outras
        return cats

    def atualizar_categoria_values(self, categorias):
        self.cmb_filtro.configure(values=[TODAS] + self._categorias_para_filtro())
        if self.cmb_filtro.get() not in ([TODAS] + self._categorias_para_filtro()):
            self.cmb_filtro.set(TODAS)

    # ---------- validação ----------
    def _validar_codigo_busca(self, texto):
        if texto == "":
            return True
        return texto.isdigit()

    # ---------- busca em tempo real ----------
    def _agendar_busca(self, _=None):
        if self._job_busca is not None:
            try:
                self.app.after_cancel(self._job_busca)
            except Exception:
                pass
        self._job_busca = self.app.after(self.DEBOUNCE_MS, self.acao_buscar)

    def _limpar_busca(self):
        self.ent_busca_codigo.delete(0, "end")
        self.ent_busca_nome.delete(0, "end")
        if self._job_busca is not None:
            try:
                self.app.after_cancel(self._job_busca)
            except Exception:
                pass
            self._job_busca = None
        self.acao_buscar()

    def acao_buscar(self, _=None):
        self._job_busca = None

        codigo_texto = self.ent_busca_codigo.get().strip()
        nome = self.ent_busca_nome.get().strip() or None

        filtro = self.cmb_filtro.get()
        categoria = None if filtro == TODAS else filtro

        resultados = self.busca.buscar(
            codigo_parcial=codigo_texto or None,
            nome=nome,
            categoria=categoria,
        )
        self._renderizar(resultados)

    # ---------- listagem ----------
    def acao_listar(self, _=None):
        self.ent_busca_codigo.delete(0, "end")
        self.ent_busca_nome.delete(0, "end")
        filtro = self.cmb_filtro.get()
        categoria = None if filtro == TODAS else filtro
        resultados = self.busca.buscar(categoria=categoria)
        self._renderizar(resultados)

    # ---------- renderização ----------
    def _renderizar(self, produtos):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        for p in produtos:
            self._criar_linha(p)

        if not produtos:
            self.lbl_contagem.configure(text="Nenhum produto encontrado")
        else:
            self.lbl_contagem.configure(text=f"Exibindo {len(produtos)} produto(s)")

    def _criar_linha(self, prod):
        linha = ctk.CTkFrame(
            self.frame_lista, fg_color=self.COR_LINHA, corner_radius=6,
        )
        linha.pack(fill="x", pady=2, padx=2)

        # coleta os widgets "internos" que precisam reagir ao hover
        widgets_hover = [linha]

        valores = [
            (str(prod.codigo),               self.COLUNAS[0][1], self.COLUNAS[0][2]),
            (prod.nome,                      self.COLUNAS[1][1], self.COLUNAS[1][2]),
            (prod.categoria,                 self.COLUNAS[2][1], self.COLUNAS[2][2]),
            (formatar_preco(prod.preco),     self.COLUNAS[3][1], self.COLUNAS[3][2]),
            (str(prod.quantidade),           self.COLUNAS[4][1], self.COLUNAS[4][2]),
        ]
        for texto, largura, anchor in valores:
            lbl = ctk.CTkLabel(
                linha, text=texto, width=largura, anchor=anchor,
            )
            lbl.pack(side="left", padx=4, pady=6)
            widgets_hover.append(lbl)

        frame_acoes = ctk.CTkFrame(linha, fg_color=self.COR_LINHA)
        frame_acoes.pack(side="left", padx=4, pady=6)
        widgets_hover.append(frame_acoes)

        btn_editar = ctk.CTkButton(
            frame_acoes, text="✏", width=40, height=28,
            fg_color="#3498DB", hover_color="#2980B9",
            command=lambda p=prod: self._abrir_popup_alterar(p),
        )
        btn_editar.pack(side="left", padx=(0, 4))

        btn_excluir = ctk.CTkButton(
            frame_acoes, text="🗑", width=40, height=28,
            fg_color="#C0392B", hover_color="#922B21",
            command=lambda p=prod: self._abrir_popup_excluir(p),
        )
        btn_excluir.pack(side="left")

        # os botões também disparam enter/leave pra manter a linha acesa
        # enquanto o mouse está em cima deles (sem pintá-los)
        widgets_hover.extend([btn_editar, btn_excluir])

        self._ligar_hover_linha(linha, widgets_hover)

    # ---------- alteração ----------
    def _abrir_popup_alterar(self, prod):
        PopupAlterar(self.app, prod, ao_salvar=self._apos_alterar)

    def _apos_alterar(self):
        self.app.refresh_listar()

    # ---------- exclusão ----------
    def _abrir_popup_excluir(self, prod):
        PopupExcluir(self.app, prod, ao_confirmar=self._apos_excluir)

    def _apos_excluir(self):
        self.app.refresh_listar()