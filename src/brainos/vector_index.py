from __future__ import annotations

import json
import sqlite3

from .errors import VectorIndexContractError
from .schema import get_vec_table_sql


class VectorIndexStorage:
    """Owns the sqlite-vec table contract and low-level vector writes."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def vec_table_dimensions(self, table_name: str) -> int | None:
        row = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
        if row is None or row[0] is None:
            return None
        sql = str(row[0])
        marker = "embedding FLOAT["
        if marker not in sql:
            return None
        dim_text = sql.split(marker, 1)[1].split("]", 1)[0].strip()
        return int(dim_text)

    def ensure_vec_table_contract(self, table_name: str, dimensions: int) -> None:
        current_dimensions = self.vec_table_dimensions(table_name)
        if current_dimensions is None:
            self.conn.execute(get_vec_table_sql(dimensions, table_name=table_name))
            return
        if current_dimensions != dimensions:
            raise VectorIndexContractError(
                "vector index dimension mismatch: "
                f"table={table_name}, expected={current_dimensions}, got={dimensions}; "
                "rebuild required"
            )

    def vec_table_exists(self, table_name: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
        return row is not None

    def upsert_vector(
        self,
        *,
        table_name: str,
        object_id: str,
        vector: list[float],
        dimensions: int,
        ensure_contract: bool = True,
    ) -> None:
        if ensure_contract:
            self.ensure_vec_table_contract(table_name, dimensions)
        vector_json = json.dumps(vector, ensure_ascii=False)
        self.conn.execute(f"DELETE FROM {table_name} WHERE id = ?", (object_id,))
        self.conn.execute(
            f"INSERT INTO {table_name}(id, embedding) VALUES (?, ?)",
            (object_id, vector_json),
        )
