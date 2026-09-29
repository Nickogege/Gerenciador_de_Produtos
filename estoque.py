# estoque.py
from produto import Produto


class Estoque:
    def __init__(self, bd=None):
        self.produtos = []
        self.categorias = ["sem categoria"]
        self.bd = bd  # camada de persistência (opcional)

    # ---------- leitura ----------
    def listar_produtos(self):
        """Retorna lista de dicts (formato ideal para o Pandas)."""
        return [p.to_dict() for p in self.produtos]

    def listar_objetos(self):
        return list(self.produtos)

    def buscar_produto(self, codigo=None, nome=None):
        for prod in self.produtos:
            if codigo is not None and prod.codigo == int(codigo):
                return prod
            if nome is not None and prod.nome.lower() == str(nome).lower():
                return prod
        return None

    # ---------- categorias ----------
    def criar_categoria(self, nome):
        nome = nome.strip()
        if not nome:
            return False
        if nome.lower() in [c.lower() for c in self.categorias]:
            return False

        if self.bd and not self.bd.inserir_categoria(nome):
            return False

        self.categorias.append(nome)
        return True

    # ---------- CRUD ----------
    def cadastrar_produto(self, produto: Produto):
        if self.buscar_produto(codigo=produto.codigo) is not None:
            return False

        if self.bd and not self.bd.inserir_produto(produto):
            return False

        self.produtos.append(produto)
        return True

    def alterar_produto(self, codigo, novo_preco=None, nova_quantidade=None):
        prod = self.buscar_produto(codigo=codigo)
        if prod is None:
            return False

        if novo_preco is not None:
            prod.atualizar_preco(novo_preco)
        if nova_quantidade is not None:
            prod.atualizar_quantidade(nova_quantidade)

        if self.bd:
            self.bd.atualizar_produto(prod)
        return True

    def remover_produto(self, codigo):
        prod = self.buscar_produto(codigo=codigo)
        if prod is None:
            return False

        if self.bd and not self.bd.remover_produto(codigo):
            return False

        self.produtos.remove(prod)
        return True

    def calcular_quantidade_total(self):
        return sum(p.quantidade for p in self.produtos)