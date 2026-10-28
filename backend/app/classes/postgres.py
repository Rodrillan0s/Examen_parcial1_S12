from app.config import Config
import psycopg2
from psycopg2 import pool
import logging
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps

_transaction_db = ContextVar('transaction_db', default=None)


@contextmanager
def transaction():
    """Share one connection across existing repositories; commit only at the boundary."""
    if _transaction_db.get() is not None:
        yield _transaction_db.get()
        return
    db = PostgreSQL()
    db.create_connection()
    if db.conn is None:
        raise RuntimeError('No se pudo abrir la transacción.')
    token = _transaction_db.set(db)
    try:
        yield db
        if getattr(db, '_rollback_only', False):
            raise RuntimeError('La transacción fue revertida por un error previo.')
        db.conn.commit()
    except BaseException:
        db.conn.rollback()
        raise
    finally:
        _transaction_db.reset(token)
        db.close_connection()


def atomic(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        with transaction():
            return fn(*args, **kwargs)
    return wrapped

logger = logging.getLogger(__name__)

class PostgreSQL:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = pool.ThreadedConnectionPool(
                    minconn=2,
                    maxconn=20,
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    dbname=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    connect_timeout=10
                )
            except Exception as e:
                logger.error(f"Error inicializando Connection Pool: {e}")
                cls._pool = None
        return cls._pool

    def __init__(self):
        self.db_host = Config.DB_HOST
        self.db_port = Config.DB_PORT
        self.db_name = Config.DB_NAME
        self.db_user = Config.DB_USER
        self.db_password = Config.DB_PASSWORD
        self.conn = None
        self.cur = None
        self._from_pool = False

    def create_connection(self):
        shared = _transaction_db.get()
        if shared is not None:
            self.conn, self.cur = shared.conn, shared.cur
            return
        try:
            p = self.get_pool()
            if p is not None:
                self.conn = p.getconn()
                self._from_pool = True
                
                # Verificar si la conexión del pool está activa sin sobrecosto de red
                if not self.conn or self.conn.closed != 0:
                    try:
                        p.putconn(self.conn, close=True)
                    except Exception:
                        pass
                    self.conn = psycopg2.connect(
                        host=self.db_host,
                        port=self.db_port,
                        dbname=self.db_name,
                        user=self.db_user,
                        password=self.db_password,
                        connect_timeout=10
                    )
                    self._from_pool = False
                    try:
                        p.putconn(self.conn, close=True)
                    except Exception:
                        pass
                    self.conn = psycopg2.connect(
                        host=self.db_host,
                        port=self.db_port,
                        dbname=self.db_name,
                        user=self.db_user,
                        password=self.db_password,
                        connect_timeout=10
                    )
                    self._from_pool = False
            else:
                self.conn = psycopg2.connect(
                    host=self.db_host,
                    port=self.db_port,
                    dbname=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                    connect_timeout=10
                )
                self._from_pool = False

            self.cur = self.conn.cursor()
        except Exception as e:
            # Fallback en caso de error
            try:
                self.conn = psycopg2.connect(
                    host=self.db_host,
                    port=self.db_port,
                    dbname=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                    connect_timeout=10
                )
                self._from_pool = False
                self.cur = self.conn.cursor()
            except Exception as ex:
                print(f'ERROR DE CONEXION A LA DB: {ex}')

    def close_connection(self, commit=False):
        if _transaction_db.get() is not None:
            return
        try:
            if self.cur:
                try:
                    self.cur.close()
                except Exception:
                    pass
                self.cur = None

            if self.conn:
                conn_is_bad = (self.conn.closed != 0)
                if not conn_is_bad:
                    if commit:
                        try:
                            self.conn.commit()
                        except Exception:
                            conn_is_bad = True
                    else:
                        try:
                            self.conn.rollback()
                        except Exception:
                            conn_is_bad = True

                if self._from_pool and self._pool is not None:
                    try:
                        self._pool.putconn(self.conn, close=conn_is_bad)
                    except Exception:
                        try:
                            self.conn.close()
                        except Exception:
                            pass
                else:
                    try:
                        self.conn.close()
                    except Exception:
                        pass
                self.conn = None
        except Exception as e:
            print(f'ERROR AL CERRAR LA CONEXION CON LA DB: {e}')



    def execute_query(self,query,params=None,fetchall=False,fetchone=False,commit=False):
        if not self.conn or not self.cur:
            print('NO HAY UNA CONEXION ACTIVA A LA BASE DE DATOS')
            return
        
        if fetchall and fetchone:
            print('SOLO PUEDE HACER UNA OPCION "FETCHALL" O "FETCHONE"')
            return

        try:
            self.cur.execute(query,params)

            if commit and _transaction_db.get() is None:
                self.conn.commit()
            
            if fetchone:
                return self.cur.fetchone() if self.cur.description is not None else None
            
            if fetchall:
                return self.cur.fetchall() if self.cur.description is not None else []
            
            return self.cur.rowcount
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            if _transaction_db.get() is not None:
                _transaction_db.get()._rollback_only = True
            from app.utils.saas_errors import translate_database_error
            translate_database_error(e)
            print(f'ERROR: {e}, EJECUTANDO ROLLBACK')
            raise

    #def insert_log():

    def commit(self):
        if self.conn and _transaction_db.get() is None:
            self.conn.commit()
