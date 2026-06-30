from typing import Optional
from database import get_db, row_to_dict


# ─── Portais ───────────────────────────────────────────────────────

def criar_portal(nome: str, url_base: str = "", tipo_login: str = "",
                 notas: str = "") -> int | None:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO portais (nome, url_base, tipo_login, notas)"
            " VALUES (?, ?, ?, ?)",
            (nome, url_base, tipo_login, notas),
        )
        return cur.lastrowid


def listar_portais() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM portais ORDER BY nome"
        ).fetchall()
        return [row_to_dict(r) for r in rows]


def get_portal(portal_id: int) -> Optional[dict]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM portais WHERE id = ?", (portal_id,)
        ).fetchone()
        return row_to_dict(row) if row else None


def atualizar_portal(portal_id: int, nome: str, url_base: str = "",
                     tipo_login: str = "", notas: str = "") -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE portais SET nome=?, url_base=?, tipo_login=?, notas=?"
            " WHERE id=?",
            (nome, url_base, tipo_login, notas, portal_id),
        )


def excluir_portal(portal_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM portais WHERE id = ?", (portal_id,))


# ─── Vagas ─────────────────────────────────────────────────────────

def criar_vaga(
    nome: str,
    empresa: str = "",
    link: str = "",
    salario: Optional[float] = None,
    salario_max: Optional[float] = None,
    modalidade: str = "",
    descricao: str = "",
    interesse: int = 3,
    aderencia: int = 3,
    status: str = "Interessado",
    portal_id: Optional[int] = None,
    data_encontrada: str = "",
    data_envio: str = "",
    notas: str = "",
    tag_ids: Optional[list[int]] = None,
    data_publicacao: str = "",
    fonte_id: str = "",
) -> int | None:
    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO vagas
               (nome, empresa, link, salario, salario_max, modalidade,
                descricao, interesse, aderencia, status, portal_id,
                data_encontrada, data_envio, notas, data_publicacao, fonte_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (nome, empresa, link, salario, salario_max, modalidade,
             descricao, interesse, aderencia, status, portal_id,
             data_encontrada, data_envio, notas, data_publicacao, fonte_id),
        )
        vaga_id = cur.lastrowid
        if tag_ids:
            for tag_id in tag_ids:
                conn.execute(
                    "INSERT OR IGNORE INTO vaga_tags (vaga_id, tag_id)"
                    " VALUES (?, ?)", (vaga_id, tag_id),
                )
        return vaga_id


def get_vaga(vaga_id: int) -> Optional[dict]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM vagas WHERE id = ?", (vaga_id,)
        ).fetchone()
        return row_to_dict(row) if row else None


def atualizar_vaga(
    vaga_id: int,
    nome: str,
    empresa: str = "",
    link: str = "",
    salario: Optional[float] = None,
    salario_max: Optional[float] = None,
    modalidade: str = "",
    descricao: str = "",
    interesse: int = 3,
    aderencia: int = 3,
    status: str = "Interessado",
    portal_id: Optional[int] = None,
    data_encontrada: str = "",
    data_envio: str = "",
    notas: str = "",
    tag_ids: Optional[list[int]] = None,
    data_publicacao: str = "",
    fonte_id: str = "",
) -> None:
    with get_db() as conn:
        conn.execute(
            """UPDATE vagas SET
               nome=?, empresa=?, link=?, salario=?, salario_max=?,
               modalidade=?, descricao=?, interesse=?, aderencia=?,
               status=?, portal_id=?, data_encontrada=?, data_envio=?,
               notas=?, data_publicacao=?, fonte_id=?
               WHERE id=?""",
            (nome, empresa, link, salario, salario_max, modalidade,
             descricao, interesse, aderencia, status, portal_id,
             data_encontrada, data_envio, notas, data_publicacao, fonte_id, vaga_id),
        )
        if tag_ids is not None:
            conn.execute(
                "DELETE FROM vaga_tags WHERE vaga_id = ?", (vaga_id,)
            )
            for tag_id in tag_ids:
                conn.execute(
                    "INSERT OR IGNORE INTO vaga_tags (vaga_id, tag_id)"
                    " VALUES (?, ?)", (vaga_id, tag_id),
                )


def excluir_vaga(vaga_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM vagas WHERE id = ?", (vaga_id,))


def listar_vagas(
    status_filtro: Optional[list[str]] = None,
    portal_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    busca: str = "",
) -> list[dict]:
    sql = "SELECT * FROM vagas WHERE 1=1"
    params = []
    if status_filtro:
        placeholders = ",".join("?" for _ in status_filtro)
        sql += f" AND status IN ({placeholders})"
        params.extend(status_filtro)
    if portal_id:
        sql += " AND portal_id = ?"
        params.append(portal_id)
    if tag_id:
        sql += """ AND id IN (
            SELECT vaga_id FROM vaga_tags WHERE tag_id = ?
        )"""
        params.append(tag_id)
    if busca:
        sql += """ AND (
            nome LIKE ? OR empresa LIKE ? OR descricao LIKE ?
        )"""
        like = f"%{busca}%"
        params.extend([like, like, like])
    sql += " ORDER BY created_at DESC"
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [row_to_dict(r) for r in rows]


def obter_metricas() -> dict:
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM vagas").fetchone()[0]
        ativas = conn.execute(
            "SELECT COUNT(*) FROM vagas WHERE status NOT IN ('Aceito','Rejeitado')"
        ).fetchone()[0]
        entrevista = conn.execute(
            "SELECT COUNT(*) FROM vagas WHERE status IN ('Entrevista Agendada','Em Processo')"
        ).fetchone()[0]
        curriculos = conn.execute(
            "SELECT COUNT(*) FROM vagas WHERE data_envio IS NOT NULL AND data_envio != ''"
        ).fetchone()[0]
        return dict(total=total, ativas=ativas,
                    entrevista=entrevista, curriculos=curriculos)


def vagas_por_status() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) as qtd FROM vagas"
            " GROUP BY status ORDER BY qtd DESC"
        ).fetchall()
        return [row_to_dict(r) for r in rows]


def curriculos_por_dia() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT data_envio, COUNT(*) as qtd FROM vagas"
            " WHERE data_envio IS NOT NULL AND data_envio != ''"
            " GROUP BY data_envio ORDER BY data_envio"
        ).fetchall()
        return [row_to_dict(r) for r in rows]


def vagas_por_portal() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT COALESCE(p.nome, 'Sem portal') as portal, COUNT(*) as qtd
               FROM vagas v LEFT JOIN portais p ON v.portal_id = p.id
               GROUP BY v.portal_id ORDER BY qtd DESC"""
        ).fetchall()
        return [row_to_dict(r) for r in rows]


# ─── Tags ──────────────────────────────────────────────────────────

def criar_tag(nome: str) -> int | None:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO tags (nome) VALUES (?)", (nome,)
        )
        if cur.rowcount:
            return cur.lastrowid
        row = conn.execute(
            "SELECT id FROM tags WHERE nome = ?", (nome,)
        ).fetchone()
        return row["id"]


def listar_tags() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM tags ORDER BY nome"
        ).fetchall()
        return [row_to_dict(r) for r in rows]


def excluir_tag(tag_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))


def get_tags_da_vaga(vaga_id: int) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT t.* FROM tags t
               JOIN vaga_tags vt ON t.id = vt.tag_id
               WHERE vt.vaga_id = ?
               ORDER BY t.nome""",
            (vaga_id,),
        ).fetchall()
        return [row_to_dict(r) for r in rows]


# ─── Histórico de Status ───────────────────────────────────────────

def listar_historico(vaga_id: int) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM historico_status"
            " WHERE vaga_id = ? ORDER BY data_mudanca",
            (vaga_id,),
        ).fetchall()
        return [row_to_dict(r) for r in rows]
