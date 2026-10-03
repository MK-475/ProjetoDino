import os
import sqlite3

PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.environ.get("DATA_DIR", PASTA_PROJETO)
BANCO = os.path.join(PASTA_DADOS, "dinossauros.db")


def conectar():
    conexao = sqlite3.connect(BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    conexao = conectar()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS dinossauros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            idade INTEGER,
            especie TEXT,
            imagem TEXT
        )
    """)

    # Compatibilidade com o banco antigo, que não tinha a coluna imagem.
    colunas = [
        linha["name"]
        for linha in conexao.execute("PRAGMA table_info(dinossauros)").fetchall()
    ]

    if "imagem" not in colunas:
        conexao.execute("ALTER TABLE dinossauros ADD COLUMN imagem TEXT")

    conexao.commit()
    conexao.close()


def cadastrar_dinossauro(nome, idade, especie, imagem=None):
    conexao = conectar()

    conexao.execute("""
        INSERT INTO dinossauros (nome, idade, especie, imagem)
        VALUES (?, ?, ?, ?)
    """, (nome, idade, especie, imagem))

    conexao.commit()
    conexao.close()


def listar_dinossauros():
    conexao = conectar()

    dinossauros = conexao.execute("""
        SELECT * FROM dinossauros
        ORDER BY id
    """).fetchall()

    conexao.close()

    return dinossauros


def buscar_dinossauro_por_id(dino_id):
    conexao = conectar()

    dinossauro = conexao.execute("""
        SELECT * FROM dinossauros
        WHERE id = ?
    """, (dino_id,)).fetchone()

    conexao.close()

    return dinossauro


def buscar_dinossauro_por_nome(nome):
    conexao = conectar()

    dinossauros = conexao.execute("""
        SELECT * FROM dinossauros
        WHERE nome = ?
    """, (nome,)).fetchall()

    conexao.close()

    return dinossauros


def atualizar_dinossauro(dino_id, nome, idade, especie, imagem=None):
    conexao = conectar()

    if imagem is None:
        cursor = conexao.execute("""
            UPDATE dinossauros
            SET nome = ?, idade = ?, especie = ?
            WHERE id = ?
        """, (nome, idade, especie, dino_id))
    else:
        cursor = conexao.execute("""
            UPDATE dinossauros
            SET nome = ?, idade = ?, especie = ?, imagem = ?
            WHERE id = ?
        """, (nome, idade, especie, imagem, dino_id))

    conexao.commit()

    alterado = cursor.rowcount > 0

    conexao.close()

    return alterado


def excluir_dinossauro(dino_id):
    conexao = conectar()

    cursor = conexao.execute("""
        DELETE FROM dinossauros
        WHERE id = ?
    """, (dino_id,))

    conexao.commit()

    excluido = cursor.rowcount > 0

    conexao.close()

    return excluido


def contar_dinossauros():
    conexao = conectar()

    resultado = conexao.execute("""
        SELECT COUNT(*) AS total
        FROM dinossauros
    """).fetchone()

    conexao.close()

    return resultado["total"]
