import os
import subprocess
import glob
import shutil
from datetime import datetime
from app.config import Config

def buscar_pg_dump():
    """
    BUSCA EL DIRECTORIO DE PG_DUMP
    """
    #BUSQUEDA PRINCIPAL EN SERVIDOR (LINUX)
    comando = shutil.which("pg_dump")
    if comando:
        return comando
    
    #SEGUNDA BUSQUEDA (PARA DESARROLLO EN WINDOWS)
    rutas_windows = [
        r"C:\Program Files\PostgreSQL\*\bin\pg_dump.exe",
        r"C:\Program Files (x86)\PostgreSQL\*\bin\pg_dump.exe",
        r"D:\Program Files\PostgreSQL\*\bin\pg_dump.exe"
    ]
    
    for ruta in rutas_windows:
        coincidencias = glob.glob(ruta)
        if coincidencias:
            return sorted(coincidencias)[-1]
            
    #RETORNAR ERROR
    raise FileNotFoundError(
        "No se encontró 'pg_dump'. Si estás en local, instala PostgreSQL. "
        "Añade 'apt-get install -y postgresql-client' a tu Build Command."
    )

def generar_backup_bd_memoria():
    try:
        fecha_actual = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        nombre_archivo = f"backup_red_talleres_{fecha_actual}.sql"
        
        env = os.environ.copy()
        env['PGPASSWORD'] = Config.DB_PASSWORD
        env['PGSSLMODE']='require'

        comando_pg_dump = buscar_pg_dump()

        comando = [
            comando_pg_dump,
            "-h", Config.DB_HOST,
            "-p", str(Config.DB_PORT),
            "-U", Config.DB_USER,
            "-F", "p",  
            "-O",       
            "-x",       
            "-n", Config.SCHEMA,
            Config.DB_NAME
        ]

        
        proceso = subprocess.run(comando, env=env, capture_output=True, text=False, check=True)

        return {
            'file_bytes': proceso.stdout,
            'file_name': nombre_archivo
        }

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
        raise RuntimeError(f'Fallo al extraer los datos de la base de datos: {error_msg}')
        
    except Exception as e:
        raise RuntimeError(f'Error inesperado generando el backup: {str(e)}')