# db.py
# =========================
# POSTGRESQL CONNECTION POOL (ASYNC WRAPPER)
# =========================

import psycopg2
from psycopg2 import pool
import asyncio

# =========================
# DATABASE CONFIG
# =========================
DB_CONFIG = {
    "dbname": "neurova",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

# =========================
# CONNECTION POOL
# =========================
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1,
    20,
    **DB_CONFIG
)


# =========================
# DATABASE CORE CLASS
# =========================
class Database:

    # =========================
    # GET CONNECTION
    # =========================
    @staticmethod
    def get_conn():
        return connection_pool.getconn()

    # =========================
    # RETURN CONNECTION
    # =========================
    @staticmethod
    def return_conn(conn):
        connection_pool.putconn(conn)

    # =========================
    # EXECUTE QUERY (SYNC CORE)
    # =========================
    @staticmethod
    def _execute_sync(query, params=None):
        conn = Database.get_conn()
        cur = conn.cursor()

        try:
            cur.execute(query, params)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("❌ DB ERROR:", e)
        finally:
            cur.close()
            Database.return_conn(conn)

    # =========================
    # FETCH ONE (SYNC CORE)
    # =========================
    @staticmethod
    def _fetch_one_sync(query, params=None):
        conn = Database.get_conn()
        cur = conn.cursor()

        result = None
        try:
            cur.execute(query, params)
            result = cur.fetchone()
        except Exception as e:
            print("❌ DB ERROR:", e)
        finally:
            cur.close()
            Database.return_conn(conn)

        return result

    # =========================
    # FETCH ALL (SYNC CORE)
    # =========================
    @staticmethod
    def _fetch_all_sync(query, params=None):
        conn = Database.get_conn()
        cur = conn.cursor()

        result = []
        try:
            cur.execute(query, params)
            result = cur.fetchall()
        except Exception as e:
            print("❌ DB ERROR:", e)
        finally:
            cur.close()
            Database.return_conn(conn)

        return result

    # ==========================================================
    # 🟢 ASYNC WRAPPERS (IMPORTANT FOR YOUR models.py)
    # ==========================================================

    @staticmethod
    async def execute(query, *params):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, Database._execute_sync, query, params)

    @staticmethod
    async def fetch_one(query, *params):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, Database._fetch_one_sync, query, params)

    @staticmethod
    async def fetch_all(query, *params):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, Database._fetch_all_sync, query, params)
