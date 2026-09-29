from tkinter import messagebox


class AcaoExcluir:

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
            self.estoque.remover_produto(codigo)
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            self.ao_atualizar()

        return True
