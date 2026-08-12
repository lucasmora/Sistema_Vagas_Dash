import os
import sqlite3
from contextlib import contextmanager
from typing import Generator

DB_PATH = os.getenv("DB_PATH", "vagas.db")

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS portais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    url_base TEXT,
    tipo_login TEXT,
    ultima_atualizacao DATE,
    notas TEXT,
    created_at TIMESTAMP DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS vagas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    empresa TEXT,
    link TEXT,
    salario REAL,
    salario_max REAL,
    modalidade TEXT,
    descricao TEXT,
    interesse INTEGER CHECK(interesse BETWEEN 1 AND 5),
    aderencia INTEGER CHECK(aderencia BETWEEN 1 AND 5),
    status TEXT CHECK(status IN (
        'Interessado', 'Currículo Enviado', 'Entrevista Agendada',
        'Em Processo', 'Oferta', 'Aceito', 'Rejeitado'
    )),
    portal_id INTEGER REFERENCES portais(id) ON DELETE SET NULL,
    data_encontrada DATE,
    data_envio DATE,
    notas TEXT,
    created_at TIMESTAMP DEFAULT (datetime('now','localtime')),
    updated_at TIMESTAMP DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS vaga_tags (
    vaga_id INTEGER NOT NULL REFERENCES vagas(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (vaga_id, tag_id)
);

CREATE TABLE IF NOT EXISTS historico_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vaga_id INTEGER NOT NULL REFERENCES vagas(id) ON DELETE CASCADE,
    status_anterior TEXT,
    status_novo TEXT NOT NULL,
    data_mudanca TIMESTAMP DEFAULT (datetime('now','localtime'))
);

CREATE TRIGGER IF NOT EXISTS trigger_vagas_updated_at
AFTER UPDATE ON vagas
BEGIN
    UPDATE vagas SET updated_at = datetime('now','localtime') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trigger_historico_status
AFTER UPDATE OF status ON vagas
WHEN OLD.status != NEW.status
BEGIN
    INSERT INTO historico_status (vaga_id, status_anterior, status_novo)
    VALUES (NEW.id, OLD.status, NEW.status);
END;
"""


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.executescript(SCHEMA_SQL)
    migrar_schema()


def migrar_schema() -> None:
    """Adiciona colunas novas que não existiam no schema original"""
    migracoes = [
        "ALTER TABLE vagas ADD COLUMN data_publicacao DATE",
        "ALTER TABLE vagas ADD COLUMN fonte_id TEXT",
    ]
    for sql in migracoes:
        try:
            with get_db() as conn:
                conn.execute(sql)
        except sqlite3.OperationalError:
            pass  # coluna já existe

    _normalizar_tags_existentes()


def _normalizar_tags_existentes() -> None:
    """Normaliza tags para minúsculas, mesclando duplicatas caixa-insensíveis."""
    with get_db() as conn:
        manter: dict[str, int] = {}
        for row in conn.execute("SELECT id, trim(nome) AS nome FROM tags"):
            nome = row["nome"].lower()
            if nome in manter:
                original = manter[nome]
                conn.execute(
                    "INSERT OR IGNORE INTO vaga_tags (vaga_id, tag_id)"
                    " SELECT vaga_id, ? FROM vaga_tags WHERE tag_id = ?",
                    (original, row["id"]),
                )
                conn.execute("DELETE FROM vaga_tags WHERE tag_id = ?", (row["id"],))
                conn.execute("DELETE FROM tags WHERE id = ?", (row["id"],))
            else:
                manter[nome] = row["id"]

        conn.execute("UPDATE tags SET nome = lower(trim(nome))")


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)