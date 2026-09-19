from app.config import Config
import psycopg2
from psycopg2 import pool
import logging

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
        try:
            p = self.get_pool()
            if p is not None:
                self.conn = p.getconn()
                self._from_pool = True
                
                # Validar que la conexión esté realmente viva antes de usarla
                is_alive = False
                if self.conn and self.conn.closed == 0:
                    try:
                        with self.conn.cursor() as test_cur:
                            test_cur.execute("SELECT 1;")
                        is_alive = True
                    except Exception:
                        is_alive = False
                
                if not is_alive:
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

            if commit:
                self.conn.commit()
            
            if fetchone:
                return self.cur.fetchone() if self.cur.description is not None else None
            
            if fetchall:
                return self.cur.fetchall() if self.cur.description is not None else []
            
            return self.cur.rowcount
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f'ERROR: {e}, EJECUTANDO ROLLBACK')
            raise

    #def insert_log():