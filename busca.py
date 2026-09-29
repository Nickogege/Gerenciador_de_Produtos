class BuscaProdutos:
    """Encapsula a lógica de busca de produtos no estoque."""

    def __init__(self, estoque):
        self.estoque = estoque

    def buscar(self, codigo=None, nome=None, categoria=None, codigo_parcial=None):
        """
        Retorna lista de produtos que atendem aos filtros.

        - codigo: match exato (int ou None)
        - codigo_parcial: prefixo do código como string (ex.: "12" casa 12, 120, 1234)
        - nome: substring case-insensitive (str ou None)
        - categoria: match exato (str ou None)
        """
        resultados = []
        nome_lower = nome.lower() if nome else None
        codigo_str = str(codigo) if codigo is not None else None

        for p in self.estoque.produtos:
            if codigo_str is not None and str(p.codigo) != codigo_str:
                continue
            if codigo_parcial and not str(p.codigo).startswith(codigo_parcial):
                continue
            if nome_lower and nome_lower not in p.nome.lower():
                continue
            if categoria is not None and p.categoria != categoria:
                continue
            resultados.append(p)

        return resultados

    @staticmethod
    def parse_codigo(texto):
        """
        Converte texto em int. Retorna (codigo, erro).
        erro é uma string com mensagem, ou None se OK.
        """
        texto = (texto or "").strip()
        if not texto:
            return None, None
        try:
            return int(texto), None
        except ValueError:
            return None, "Digite um código numérico válido."