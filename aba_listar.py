# aba_listar.py
import customtkinter as ctk
from tkinter import messagebox

from helpers import formatar_preco, TODAS
from busca import BuscaProdutos
from popup_excluir import PopupExcluir
from popup_alterar import PopupAlterar
from tema import paleta


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

    DEBOUNCE_MS = 200

    def __init__(self, aba, app):
        self.app = app
        self.estoque = app.estoque
        self.busca = BuscaProdutos(self.estoque)
        self.aba = aba
        self._job_busca = None
        self._montar(aba)
        self.acao_listar()

    # ---------- montagem ----------
    def _montar(self, aba):
        p = paleta()

        self.frame_busca = ctk.CTkFrame(aba, fg_color=p["fundo"])
        self.frame_busca.pack(fill="x", pady=(0, 8))

        self.lbl_busca_cod = ctk.CTkLabel(
            self.frame_busca, text="Buscar por código:", text_color=p["texto"],
            fg_color=p["fundo"],
        )
        self.lbl_busca_cod.pack(side="left", padx=(0, 8))
        vcmd_codigo = (aba.register(self._validar_codigo_busca), "%P")
        self.ent_busca_codigo = ctk.CTkEntry(
            self.frame_busca, width=120, validate="key", validatecommand=vcmd_codigo,
        )
        self.ent_busca_codigo.pack(side="left", padx=(0, 15))
        self._ligar_busca_tempo_real(self.ent_busca_codigo)

        self.lbl_busca_nome = ctk.CTkLabel(
            self.frame_busca, text="Nome:", text_color=p["texto"],
            fg_color=p["fundo"],
        )
        self.lbl_busca_nome.pack(side="left", padx=(0, 8))
        self.ent_busca_nome = ctk.CTkEntry(self.frame_busca, width=180)
        self.ent_busca_nome.pack(side="left", padx=(0, 15))
        self._ligar_busca_tempo_real(self.ent_busca_nome)

        self.btn_limpar = ctk.CTkButton(
            self.frame_busca, text="Limpar", width=80, command=self._limpar_busca,
        )
        self.btn_limpar.pack(side="left")

        self.frame_filtro = ctk.CTkFrame(aba, fg_color=p["fundo"])
        self.frame_filtro.pack(fill="x", pady=(0, 8))

        self.lbl_filtro = ctk.CTkLabel(
            self.frame_filtro, text="Categoria:", text_color=p["texto"],
            fg_color=p["fundo"],
        )
        self.lbl_filtro.pack(side="left", padx=(0, 8))
        self.cmb_filtro = ctk.CTkComboBox(
            self.frame_filtro,
            values=[TODAS] + self._categorias_para_filtro(),
            state="readonly",
            width=220,
            command=self.acao_buscar,
        )
        self.cmb_filtro.set(TODAS)
        self.cmb_filtro.pack(side="left")

        self.frame_header = ctk.CTkFrame(aba, corner_radius=0, fg_color=p["fundo_frame"])
        self.frame_header.pack(fill="x", pady=(0, 0))
        self.lbls_header = []
        for texto, largura, anchor in self.COLUNAS:
            lbl = ctk.CTkLabel(
                self.frame_header, text=texto, width=largura, anchor=anchor,
                font=("Arial", 12, "bold"),
                text_color=p["texto"], fg_color=p["fundo_frame"],
            )
            lbl.pack(side="left", padx=6, pady=8)
            self.lbls_header.append(lbl)

        self.frame_lista = ctk.CTkScrollableFrame(aba, fg_color=p["fundo"])
        self.frame_lista.pack(fill="both", expand=True)

        self.lbl_contagem = ctk.CTkLabel(
            aba, text="", text_color=p["texto"], fg_color=p["fundo"],
        )
        self.lbl_contagem.pack(pady=(8, 0))

        self.btn_atualizar = ctk.CTkButton(
            aba, text="Atualizar Lista", command=self.acao_listar,
        )
        self.btn_atualizar.pack(pady=10)

    # ---------- tema ----------
    def aplicar_tema(self, p):
        self.aba.configure(fg_color=p["fundo"])

        # frames de fundo (senão ficam brancos no tema claro e cinza no escuro)
        self.frame_busca.configure(fg_color=p["fundo"])
        self.frame_filtro.configure(fg_color=p["fundo"])
        self.frame_lista.configure(fg_color=p["fundo"])

        for lbl in (self.lbl_busca_cod, self.lbl_busca_nome,
                    self.lbl_filtro, self.lbl_contagem):
            lbl.configure(text_color=p["texto"], fg_color=p["fundo"])

        for ent in (self.ent_busca_codigo, self.ent_busca_nome):
            ent.configure(
                fg_color=p["entrada"],
                border_color=p["entrada_borda"],
                text_color=p["texto"],
            )

        self.cmb_filtro.configure(
            fg_color=p["entrada"],
            border_color=p["entrada_borda"],
            text_color=p["texto"],
            button_color=p["botao"],
            button_hover_color=p["botao_hover"],
            dropdown_fg_color=p["entrada"],
            dropdown_text_color=p["texto"],
            dropdown_hover_color=p["fundo_frame_hover"],
        )

        self.btn_limpar.configure(
            fg_color=p["botao_neutro"], hover_color=p["botao_neutro_hover"],
            text_color=p["texto"],
        )
        self.btn_atualizar.configure(
            fg_color=p["botao"], hover_color=p["botao_hover"],
            text_color=p["botao_texto"],
        )

        self.frame_header.configure(fg_color=p["fundo_frame"])
        for lbl in self.lbls_header:
            lbl.configure(text_color=p["texto"], fg_color=p["fundo_frame"])

    # ---------- busca tempo real ----------
    def _ligar_busca_tempo_real(self, entry):
        entry.bind("<KeyRelease>", self._agendar_busca)
        entry.bind("<<Paste>>", lambda e: self.after(10, self._agendar_busca))
        entry.bind("<<Cut>>",   lambda e: self.after(10, self._agendar_busca))
        entry.bind("<<Clear>>", lambda e: self.after(10, self._agendar_busca))
        entry.bind("<<PasteSelection>>", lambda e: self.after(10, self._agendar_busca))

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

    def _validar_codigo_busca(self, texto):
        if texto == "":
            return True
        return texto.isdigit()

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

    def acao_listar(self, _=None):
        self.ent_busca_codigo.delete(0, "end")
        self.ent_busca_nome.delete(0, "end")
        filtro = self.cmb_filtro.get()
        categoria = None if filtro == TODAS else filtro
        resultados = self.busca.buscar(categoria=categoria)
        self._renderizar(resultados)

    # ---------- renderização ----------
    def _renderizar(self, produtos):
        p = paleta()
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        for prod in produtos:
            self._criar_linha(prod, p)
        if not produtos:
            self.lbl_contagem.configure(text="Nenhum produto encontrado")
        else:
            self.lbl_contagem.configure(text=f"Exibindo {len(produtos)} produto(s)")

    def _criar_linha(self, prod, p):
        cor = p["fundo_frame"]

        linha = ctk.CTkFrame(
            self.frame_lista,
            fg_color=cor,
            corner_radius=0,
            border_width=0,
        )
        linha.pack(fill="x", pady=0, padx=0)

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
                text_color=p["texto"],
                fg_color=cor,
            )
            lbl.pack(side="left", padx=6, pady=8)
            widgets_hover.append(lbl)

        frame_acoes = ctk.CTkFrame(linha, fg_color=cor, corner_radius=0)
        frame_acoes.pack(side="left", padx=(0, 6), pady=4)
        widgets_hover.append(frame_acoes)

        btn_editar = ctk.CTkButton(
            frame_acoes, text="✏", width=40, height=28,
            fg_color=p["botao_editar"], hover_color=p["botao_editar_hover"],
            text_color=p["botao_texto"],
            corner_radius=6,
            command=lambda prod=prod: self._abrir_popup_alterar(prod),
        )
        btn_editar.pack(side="left", padx=(0, 4))

        btn_excluir = ctk.CTkButton(
            frame_acoes, text="🗑", width=40, height=28,
            fg_color=p["botao_perigo"], hover_color=p["botao_perigo_hover"],
            text_color=p["botao_texto"],
            corner_radius=6,
            command=lambda prod=prod: self._abrir_popup_excluir(prod),
        )
        btn_excluir.pack(side="left")

        widgets_hover.extend([btn_editar, btn_excluir])

        linha._cor_normal = cor
        linha._cor_hover = p["fundo_frame_hover"]
        linha._widgets_cor = [linha, frame_acoes] + [
            w for w in widgets_hover if isinstance(w, ctk.CTkLabel)
        ]

        self._ligar_hover_linha(linha, widgets_hover)

    def _ligar_hover_linha(self, linha, widgets):
        def on_enter(_):
            self._pintar_linha(linha, linha._cor_hover)

        def on_leave(_):
            x, y = linha.winfo_pointerxy()
            widget_sob_mouse = linha.winfo_containing(x, y)
            if widget_sob_mouse is not None:
                atual = widget_sob_mouse
                while atual is not None:
                    if atual is linha:
                        return
                    atual = atual.master
            self._pintar_linha(linha, linha._cor_normal)

        for w in widgets:
            w.bind("<Enter>", on_enter, add="+")
            w.bind("<Leave>", on_leave, add="+")

    @staticmethod
    def _pintar_linha(linha, cor):
        for w in linha._widgets_cor:
            try:
                w.configure(fg_color=cor)
            except Exception:
                pass

    # ---------- ações ----------
    def _abrir_popup_alterar(self, prod):
        PopupAlterar(self.app, prod, ao_salvar=self._apos_alterar)

    def _apos_alterar(self):
        self.app.refresh_listar()

    def _abrir_popup_excluir(self, prod):
        PopupExcluir(self.app, prod, ao_confirmar=self._apos_excluir)

    def _apos_excluir(self):
        self.app.refresh_listar()