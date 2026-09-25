class Produto:
    def __init__(self, codigo: int, nome: str, preco: float, quantidade: int,
                 categoria: str = "Sem categoria", id: int = None):
        # 'id' é interno — gerado pelo SQLite, nunca exibido na interface.
        self.id = id
        self.codigo = int(codigo)
        self.nome = nome
        self.preco = float(preco)
        self.quantidade = int(quantidade)
        self.categoria = categoria

    def atualizar_preco(self, novo_preco: float) -> None:
        if novo_preco > 0:
            self.preco = float(novo_preco)

    def atualizar_quantidade(self, nova_quantidade: int) -> None:
        if nova_quantidade >= 0:
            self.quantidade = int(nova_quantidade)

    def to_dict(self) -> dict:
        return {
            "id": self.id,            # oculto, mas útil p/ debug
            "codigo": self.codigo,
            "nome": self.nome,
            "preco": self.preco,
            "quantidade": self.quantidade,
            "categoria": self.categoria,
        }

    def __str__(self) -> str:
        return (
            f"Código: {self.codigo} | "
            f"Nome: {self.nome} | "
            f"Categoria: {self.categoria} | "
            f"Preço: R$ {self.preco:.2f} | "
            f"Qtd: {self.quantidade}"
        )

    def __repr__(self) -> str:
        return (f"Produto(id={self.id}, codigo={self.codigo}, "
                f"{self.nome!r}, R${self.preco}, qtd={self.quantidade})")