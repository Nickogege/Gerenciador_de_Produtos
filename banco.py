# banco.py
import sqlite3
from produto import Produto

CAMINHO_BD = "estoque.db"


class BancoDados:
    """Camada de persistência SQLite para o Estoque."""

    def __init__(self, caminho=CAMINHO_BD):
        self.caminho = caminho
        self.conn = sqlite3.connect(self.caminho)
        self.conn.row_factory = sqlite3.Row
        self._criar_tabelas()

    # ---------- DDL ----------
    def _criar_tabelas(self):
        cur = self.conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo     INTEGER NOT NULL UNIQUE,
                nome       TEXT    NOT NULL,
                preco      REAL    NOT NULL,
                quantidade INTEGER NOT NULL,
                categoria  TEXT    NOT NULL DEFAULT 'sem categoria'
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        """)

        cur.execute(
            "INSERT OR IGNORE INTO categorias (nome) VALUES (?)",
            ("sem categoria",),
        )
        self.conn.commit()

    # ---------- Categorias ----------
    def listar_categorias(self):
        cur = self.conn.execute("SELECT nome FROM categorias ORDER BY nome")
        return [row["nome"] for row in cur.fetchall()]

    def inserir_categoria(self, nome):
        try:
            self.conn.execute(
                "INSERT INTO categorias (nome) VALUES (?)", (nome.strip(),)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False

    # ---------- Produtos ----------
    def listar_produtos(self):
        cur = self.conn.execute(
            "SELECT id, codigo, nome, preco, quantidade, categoria "
            "FROM produtos ORDER BY codigo"
        )
        return [self._row_para_produto(r) for r in cur.fetchall()]

    def buscar_por_codigo(self, codigo):
        cur = self.conn.execute(
            "SELECT id, codigo, nome, preco, quantidade, categoria "
            "FROM produtos WHERE codigo = ?",
            (int(codigo),),
        )
        row = cur.fetchone()
        return self._row_para_produto(row) if row else None

    def inserir_produto(self, prod: Produto):
        try:
            cur = self.conn.execute(
                "INSERT INTO produtos (codigo, nome, preco, quantidade, categoria) "
                "VALUES (?, ?, ?, ?, ?)",
                (prod.codigo, prod.nome, prod.preco,
                 prod.quantidade, prod.categoria),
            )
            self.conn.commit()
            prod.id = cur.lastrowid
            return True
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False

    def atualizar_produto(self, prod: Produto):
        cur = self.conn.execute(
            "UPDATE produtos SET nome = ?, preco = ?, quantidade = ?, categoria = ? "
            "WHERE codigo = ?",
            (prod.nome, prod.preco, prod.quantidade, prod.categoria, prod.codigo),
        )
        self.conn.commit()
        return cur.rowcount > 0

    def remover_produto(self, codigo):
        cur = self.conn.execute(
            "DELETE FROM produtos WHERE codigo = ?", (int(codigo),)
        )
        self.conn.commit()
        return cur.rowcount > 0

    # ---------- Sincronização ----------
    def carregar_para_estoque(self, estoque):
        """Popula o Estoque em memória a partir do BD."""
        estoque.produtos.clear()
        estoque.produtos.extend(self.listar_produtos())

        cats = self.listar_categorias()
        if cats:
            estoque.categorias = cats

    # ---------- util ----------
    @staticmethod
    def _row_para_produto(row):
        return Produto(
            codigo=row["codigo"],
            nome=row["nome"],
            preco=row["preco"],
            quantidade=row["quantidade"],
            categoria=row["categoria"],
            id=row["id"],
        )

    def fechar(self):
        self.conn.close()