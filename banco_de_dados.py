import os
import pandas as pd
from produto import Produto          
from estoque import Estoque         


class BancoDeDados:
    COLUNAS = ["codigo", "nome", "preco", "quantidade", "categoria"]

    def __init__(self, nome_arquivo="produtos.csv", estoque: Estoque = None):
        self.arquivo = nome_arquivo
        self.estoque = estoque if estoque is not None else Estoque()

        if os.path.exists(self.arquivo):
            self.df = pd.read_csv(self.arquivo)
            self._carregar_no_estoque()          
        else:
            self.df = pd.DataFrame(columns=self.COLUNAS)
            self.df.to_csv(self.arquivo, index=False)


    def _carregar_no_estoque(self):
        """Reconstrói objetos Produto a partir do CSV e repovoa categorias."""
        self.estoque.produtos.clear()
        for _, row in self.df.iterrows():
            p = Produto(
                codigo=int(row["codigo"]),
                nome=str(row["nome"]),
                preco=float(row["preco"]),
                quantidade=int(row["quantidade"]),
                categoria=str(row.get("categoria", "sem categoria")),
            )
            self.estoque.produtos.append(p)

          
            if p.categoria and p.categoria not in self.estoque.categorias:
                self.estoque.categorias.append(p.categoria)

    def sincronizar_do_estoque(self):
        """Estoque (memória) → DataFrame → CSV."""
        self.df = pd.DataFrame(self.estoque.listar_produtos(), columns=self.COLUNAS)
        self.df.to_csv(self.arquivo, index=False)
        return self.df

    
    importar_lista = sincronizar_do_estoque

   
    def buscar_produto(self, codigo):
        resultado = self.df[self.df["codigo"] == int(codigo)]
        return resultado.iloc[0] if not resultado.empty else None

    def listar_produtos(self):
        return self.df

    def adicionar_produto(self, produto: Produto):
        if self.estoque.cadastrar_produto(produto):
            self.sincronizar_do_estoque()
            return True
        return False

    def remover_produto(self, codigo):
        if self.estoque.remover_produto(codigo):
            self.sincronizar_do_estoque()
            return True
        return False