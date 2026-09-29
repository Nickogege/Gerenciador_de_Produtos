import os
import sqlite3

# O banco fica sempre ao lado dos arquivos do programa, não importa de
# qual pasta o app.py é executado.
CAMINHO_BANCO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estoque.db")


class BancoDados:
    """Camada de acesso ao banco de dados SQLite (arquivo estoque.db).

    Responsável só por ler/gravar linhas; quem decide regras de negócio
    (validações, duplicados etc.) continua sendo a classe Estoque.
    """

    def __init__(self, caminho=CAMINHO_BANCO):
        self.conexao = sqlite3.connect(caminho)
        self.conexao.execute("PRAGMA foreign_keys = ON")
        self._criar_tabelas()

    def _criar_tabelas(self):
        self.conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS categorias (
                nome TEXT PRIMARY KEY
            )
            """
        )
        self.conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo INTEGER NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                preco REAL NOT NULL,
                quantidade INTEGER NOT NULL,
                categoria TEXT NOT NULL DEFAULT 'sem categoria'
            )
            """
        )
        # Garante que a categoria padrão sempre exista, mesmo num banco novo.
        self.conexao.execute(
            "INSERT OR IGNORE INTO categorias (nome) VALUES ('sem categoria')"
        )
        self.conexao.commit()
        self._migrar_id_se_necessario()

    def _migrar_id_se_necessario(self):
        """Bancos criados antes de existir a coluna 'id' não têm essa coluna
        ainda; aqui a tabela é recriada preservando os dados e ganhando o id
        autoincrementado. Esse id é só de uso interno do banco (chave técnica)
        — o app continua trabalhando só com 'codigo', o id nunca é lido nem
        exposto em nenhuma tela."""
        colunas = [linha[1] for linha in self.conexao.execute("PRAGMA table_info(produtos)")]
        if "id" in colunas:
            return  # já está no formato novo, nada a fazer

        self.conexao.execute("ALTER TABLE produtos RENAME TO produtos_antigo")
        self.conexao.execute(
            """
            CREATE TABLE produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo INTEGER NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                preco REAL NOT NULL,
                quantidade INTEGER NOT NULL,
                categoria TEXT NOT NULL DEFAULT 'sem categoria'
            )
            """
        )
        self.conexao.execute(
            """
            INSERT INTO produtos (codigo, nome, preco, quantidade, categoria)
            SELECT codigo, nome, preco, quantidade, categoria FROM produtos_antigo
            """
        )
        self.conexao.execute("DROP TABLE produtos_antigo")
        self.conexao.commit()

    # ------------------------------------------------------------------
    # CATEGORIAS
    # ------------------------------------------------------------------
    def carregar_categorias(self):
        cursor = self.conexao.execute("SELECT nome FROM categorias ORDER BY rowid")
        return [linha[0] for linha in cursor.fetchall()]

    def inserir_categoria(self, nome):
        self.conexao.execute("INSERT INTO categorias (nome) VALUES (?)", (nome,))
        self.conexao.commit()

    # ------------------------------------------------------------------
    # PRODUTOS
    # ------------------------------------------------------------------
    def carregar_produtos(self):
        cursor = self.conexao.execute(
            "SELECT codigo, nome, preco, quantidade, categoria FROM produtos ORDER BY codigo"
        )
        return cursor.fetchall()

    def buscar_produto(self, codigo):
        cursor = self.conexao.execute(
            "SELECT codigo, nome, preco, quantidade, categoria FROM produtos WHERE codigo = ?",
            (codigo,),
        )
        return cursor.fetchone()

    def inserir_produto(self, codigo, nome, preco, quantidade, categoria):
        self.conexao.execute(
            "INSERT INTO produtos (codigo, nome, preco, quantidade, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            (codigo, nome, preco, quantidade, categoria),
        )
        self.conexao.commit()

    def atualizar_produto(self, codigo, nome, preco, quantidade, categoria):
        self.conexao.execute(
            "UPDATE produtos SET nome = ?, preco = ?, quantidade = ?, categoria = ? "
            "WHERE codigo = ?",
            (nome, preco, quantidade, categoria, codigo),
        )
        self.conexao.commit()

    def remover_produto(self, codigo):
        self.conexao.execute("DELETE FROM produtos WHERE codigo = ?", (codigo,))
        self.conexao.commit()

    def fechar(self):
        self.conexao.close()