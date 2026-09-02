from app.config import Config
import psycopg2

class PostgreSQL():

    def __init__(self):
        self.db_host=Config.DB_HOST
        self.db_port=Config.DB_PORT
        self.db_name=Config.DB_NAME
        self.db_user=Config.DB_USER
        self.db_password=Config.DB_PASSWORD
        self.conn=None
        self.cur=None

    def create_connection(self):
        try:
            self.conn=psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password
            )

            self.cur=self.conn.cursor()
            print('CONEXION EXITOSA')
        except Exception as e:
            print(f'ERROR DE CONEXION A LA DB: {e}')

    def close_connection(self,commit=False):
        try:
            if self.conn:
                if commit:
                    self.conn.commit()
                if self.cur:
                    self.cur.close()
                self.conn.close()
                print('CONEXION A LA DB CERRADA EXITOSAMENTE')
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