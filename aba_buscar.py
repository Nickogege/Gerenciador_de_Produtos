import customtkinter as ctk
from tkinter import messagebox

from helpers import formatar_preco, ler_numero
from popup_alterar import PopupAlterar


class AbaBuscar:
    """Aba de consulta e alteração de produtos."""

    def __init__(self, aba, app):
        self.app = app
        self.estoque = app.estoque
        self.produto_encontrado = None
        self._montar(aba)

    def _montar(self, aba):
        ctk.CTkLabel(aba, text="Código:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.ent_busca_codigo = ctk.CTkEntry(aba, width=200)
        self.ent_busca_codigo.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(aba, text="Nome:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.ent_busca_nome = ctk.CTkEntry(aba, width=200)
        self.ent_busca_nome.grid(row=1, column=1, padx=10, pady=10)

        btn_buscar = ctk.CTkButton(
            aba, text="Buscar", width=100, command=self.acao_buscar,
            fg_color="#A37BD6", hover_color="#8358BE",
        )
        btn_buscar.grid(row=0, column=2, padx=10, pady=10)

        self.lbl_resultado_busca = ctk.CTkLabel(aba, text="", justify="left", anchor="w")
        self.lbl_resultado_busca.grid(row=3, column=0, columnspan=3, padx=10, pady=15, sticky="w")

        self.btn_alterar = ctk.CTkButton(
            aba, text="Alterar Produto", command=self.abrir_popup_alterar,
            fg_color="#A37BD6", hover_color="#8358BE",
        )
        self.btn_alterar.grid(row=2, column=0, columnspan=3, pady=5)
        self.btn_alterar.grid_remove()

    def acao_buscar(self):
        
        try:
            if self.ent_busca_codigo.get() != '':
                codigo = int(self.ent_busca_codigo.get()) 
            else:
                codigo = None
            nome = self.ent_busca_nome.get()
        except ValueError:
            messagebox.showerror("Erro", "Digite um código numérico válido.")
            return
  
       
        prod = self.estoque.buscar_produto(codigo, nome)
        if prod:
            self.produto_encontrado = prod
            self.lbl_resultado_busca.configure(
                text=(
                    "Produto encontrado:\n"
                    f"Nome: {prod.nome}\n"
                    f"Categoria: {prod.categoria}\n"
                    f"Preço: R$ {formatar_preco(prod.preco)}\n"
                    f"Quantidade: {prod.quantidade}"
                )
            )
            self.btn_alterar.grid()
        else:
            self.produto_encontrado = None
            self.lbl_resultado_busca.configure(text="Produto não encontrado")
            self.btn_alterar.grid_remove()

    def abrir_popup_alterar(self):
        if self.produto_encontrado is None:
            return
        PopupAlterar(self.app, self.produto_encontrado, ao_salvar=self._apos_salvar_alteracao)

    def _apos_salvar_alteracao(self):
        """Chamado pelo popup depois que a alteração é salva com sucesso."""
        self.acao_buscar()
        self.app.refresh_listar()
