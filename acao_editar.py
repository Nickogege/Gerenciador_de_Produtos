from tkinter import messagebox

from popup_alterar import PopupAlterar


class AcaoEditar:

    def __init__(self, app, ao_atualizar):
        self.app = app
        self.estoque = app.estoque
        self.ao_atualizar = ao_atualizar 
        self.ativo = False

    def ativar(self):
        self.ativo = True
        messagebox.showinfo(
        )

    def tratar_selecao(self, codigo):
        if not self.ativo:
            return False
        self.ativo = False

        prod = self.estoque.buscar_produto(codigo)
        if prod is None:
            return True

        if messagebox.askyesno({prod.nome}):
            PopupAlterar(self.app, prod, ao_salvar=self.ao_atualizar)

        return True
