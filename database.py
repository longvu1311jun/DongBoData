# ============================================================
# DATABASE MODULE - MariaDB Connection & Operations
# ============================================================

import mariadb
import config


class Database:
    def __init__(self):
        self.conn = None
        self._connect()

    def _connect(self):
        try:
            self.conn = mariadb.connect(
                host=config.DB_CONFIG["host"],
                port=config.DB_CONFIG["port"],
                user=config.DB_CONFIG["user"],
                password=config.DB_CONFIG["password"],
                database=config.DB_CONFIG["database"],
                autocommit=False,
            )
        except mariadb.Error as e:
            raise ConnectionError("Khong the ket noi MariaDB: %s" % e)

    def ping(self):
        try:
            self.conn.ping(reconnect=True)
            return True
        except Exception:
            return False

    def reconnect(self):
        self.close()
        self._connect()

    def execute(self, query, params=None):
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(query, params or ())
            return cur
        except mariadb.Error as e:
            self.conn.rollback()
            raise e

    def commit(self):
        self.conn.commit()

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None

    def upsert(self, table, row):
        cols = list(row.keys())
        vals = list(row.values())
        placeholders = ", ".join(["%s"] * len(cols))
        col_names = ", ".join(cols)
        update_pairs = ", ".join([c + "=VALUES(" + c + ")" for c in cols])
        sql = "INSERT INTO " + table + " (" + col_names + ") VALUES (" + placeholders + ") ON DUPLICATE KEY UPDATE " + update_pairs
        cur = self.execute(sql, vals)
        rc = cur.rowcount
        self.commit()
        if rc > 0:
            return rc, 0
        elif rc < 0:
            return 0, abs(rc)
        else:
            return 0, 0

    def upsert_batches(self, table, rows, batch_size=200):
        total_ins = 0
        total_upd = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            for row in batch:
                ins, upd = self.upsert(table, row)
                total_ins += ins
                total_upd += upd
        return total_ins, total_upd

    def get_max_updated_at(self, table, col="updated_at"):
        try:
            cur = self.execute("SELECT MAX(" + col + ") as mx FROM " + table)
            row = cur.fetchone()
            return row["mx"] if row and row["mx"] else None
        except Exception:
            return None

    def get_max_id(self, table, col="id"):
        try:
            cur = self.execute("SELECT MAX(" + col + ") as mx FROM " + table)
            row = cur.fetchone()
            return row["mx"] if row and row["mx"] else 0
        except Exception:
            return 0

    def get_row_count(self, table):
        try:
            cur = self.execute("SELECT COUNT(*) as cnt FROM " + table)
            row = cur.fetchone()
            return row["cnt"] if row else 0
        except Exception:
            return 0
