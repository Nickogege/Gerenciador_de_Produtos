import csv
import os
import sqlite3

from produto import Produto
from estoque import Estoque


class BancoDeDados:
    """
    Persistência em SQLite.

    • id      → interno, autoincrement, OCULTO
    • codigo  → visível ao usuário (código de barras)

    Migração automática:
      1) Se 'produtos.db' não for um SQLite válido → move para 'produtos.csv'.
      2) Se existir 'produtos.csv' e o banco estiver vazio → importa e renomeia.
    """

    HEADER_SQLITE = b"SQLite format 3\x00"

    def __init__(self, nome_arquivo="produtos.db", estoque: Estoque = None):
        self.arquivo = nome_arquivo
        self.estoque = estoque if estoque is not None else Estoque()

        # Antes de abrir conexão, garante que o arquivo não seja um impostor
        self._sanar_arquivo_invalido()

        self._criar_tabela()
        self._migrar_csv_se_existir()
        self._carregar_no_estoque()

    # ---------- diagnóstico ----------
    def _arquivo_eh_sqlite(self, caminho: str) -> bool:
        if not os.path.exists(caminho):
            return False
        try:
            with open(caminho, "rb") as f:
                return f.read(16).startswith(self.HEADER_SQLITE)
        except OSError:
            return False

    def _sanar_arquivo_invalido(self):
        """
        Se o arquivo alvo existe mas não é SQLite (ex.: um CSV renomeado),
        renomeia-o para 'produtos.csv' para que a rotina de migração o processe.
        """
        if not os.path.exists(self.arquivo):
            return
        if self._arquivo_eh_sqlite(self.arquivo):
            return

        # É texto → presume-se CSV
        destino = "produtos.csv"
        if os.path.exists(destino):
            # Já tem um produtos.csv — não sobrescreve; guarda como backup
            backup = self.arquivo + ".invalido"
            os.replace(self.arquivo, backup)
            print(f"[BD] '{self.arquivo}' não é SQLite. Movido para '{backup}'.")
        else:
            os.replace(self.arquivo, destino)
            print(f"[BD] '{self.arquivo}' não era SQLite. Renomeado para '{destino}' "
                  f"para ser migrado.")

    # ---------- conexão ----------
    def _conectar(self):
        con = sqlite3.connect(self.arquivo)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con

    # ---------- schema ----------
    def _criar_tabela(self):
        with self._conectar() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS produtos (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo      INTEGER UNIQUE NOT NULL,
                    nome        TEXT    NOT NULL,
                    preco       REAL    NOT NULL,
                    quantidade  INTEGER NOT NULL,
                    categoria   TEXT    DEFAULT 'sem categoria'
                )
                """
            )

    # ---------- migração CSV → SQLite ----------
    def _migrar_csv_se_existir(self, caminho_csv="produtos.csv"):
        if not os.path.exists(caminho_csv):
            return

        with self._conectar() as con:
            ja_tem = con.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] > 0
        if ja_tem:
            return

        try:
            with open(caminho_csv, "r", encoding="utf-8") as f:
                linhas = list(csv.DictReader(f))
        except Exception as e:
            print(f"[BD] Falha lendo '{caminho_csv}': {e}")
            return

        inseridos = 0
        with self._conectar() as con:
            for row in linhas:
                try:
                    con.execute(
                        "INSERT OR IGNORE INTO produtos "
                        "(codigo, nome, preco, quantidade, categoria) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (
                            int(row["codigo"]),
                            str(row["nome"]),
                            float(row["preco"]),
                            int(row["quantidade"]),
                            str(row.get("categoria") or "sem categoria"),
                        ),
                    )
                    inseridos += 1
                except (ValueError, KeyError):
                    continue

        print(f"[BD] Migração concluída: {inseridos} produto(s) importado(s).")
        try:
            os.rename(caminho_csv, caminho_csv + ".migrado")
        except OSError:
            pass

    # ---------- carga inicial ----------
    def _carregar_no_estoque(self):
        self.estoque.produtos.clear()
        with self._conectar() as con:
            rows = con.execute("SELECT * FROM produtos ORDER BY id").fetchall()

        for row in rows:
            p = Produto(
                codigo=row["codigo"],
                nome=row["nome"],
                preco=row["preco"],
                quantidade=row["quantidade"],
                categoria=row["categoria"],
                id=row["id"],
            )
            self.estoque.produtos.append(p)
            if p.categoria and p.categoria not in self.estoque.categorias:
                self.estoque.categorias.append(p.categoria)

    # ---------- memória → banco ----------
    def sincronizar_do_estoque(self):
        with self._conectar() as con:
            existentes = {
                row["codigo"]: row["id"]
                for row in con.execute("SELECT id, codigo FROM produtos")
            }
            memoria = {p.codigo: p for p in self.estoque.produtos}

            for codigo, id_db in existentes.items():
                if codigo not in memoria:
                    con.execute("DELETE FROM produtos WHERE id = ?", (id_db,))

            for p in self.estoque.produtos:
                if p.codigo in existentes:
                    con.execute(
                        "UPDATE produtos SET nome=?, preco=?, quantidade=?, categoria=? "
                        "WHERE id=?",
                        (p.nome, p.preco, p.quantidade, p.categoria,
                         existentes[p.codigo]),
                    )
                    p.id = existentes[p.codigo]
                else:
                    cur = con.execute(
                        "INSERT INTO produtos "
                        "(codigo, nome, preco, quantidade, categoria) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (p.codigo, p.nome, p.preco, p.quantidade, p.categoria),
                    )
                    p.id = cur.lastrowid

        return self.listar_produtos()

    importar_lista = sincronizar_do_estoque

    # ---------- consultas ----------
    def listar_produtos(self):
        with self._conectar() as con:
            rows = con.execute("SELECT * FROM produtos ORDER BY id").fetchall()
        return [dict(r) for r in rows]

    def buscar_produto(self, codigo):
        with self._conectar() as con:
            row = con.execute(
                "SELECT * FROM produtos WHERE codigo = ?", (int(codigo),)
            ).fetchone()
        return dict(row) if row else None

    def buscar_por_id(self, id_produto):
        with self._conectar() as con:
            row = con.execute(
                "SELECT * FROM produtos WHERE id = ?", (int(id_produto),)
            ).fetchone()
        return dict(row) if row else None

    # ---------- CRUD ----------
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