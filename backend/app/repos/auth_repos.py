from app.classes.postgres import PostgreSQL
from app.config import Config

def obtener_usuario_por_ci(ci: str):
    db = PostgreSQL()    
    try:
        db.create_connection()

        query = f"""
            SELECT a.password_hash,a.nro_usuario,a.ci,b.nombre_completo,b.correo,b.telefono,
            a.nombre_usuario,c.nombre_rol,a.id_empresa,nro_taller
            FROM {Config.SCHEMA}.usuario a
            INNER JOIN taller.persona b ON a.ci = b.ci
            INNER JOIN taller.rol c ON a.nro_rol = c.nro_rol
            WHERE a.ci = %s AND a.estado = 'ACTIVO';
        """
        
        
        resultado = db.execute_query(query, (ci,), fetchone=True)
        
        if resultado:
            return {
                "password_hash": resultado[0],
                "nro_usuario": resultado[1],
                "ci": resultado[2],
                "nombre_completo": resultado[3],
                "correo": resultado[4],
                "telefono": resultado[5],
                "nombre_usuario": resultado[6],
                "nombre_rol": resultado[7],
                "id_empresa":resultado[8],
                "nro_taller":resultado[9]
            }
            
        return None
    except Exception as e:
        raise ValueError(f'ERROR: {str(e)}') 
    finally:
        db.close_connection()


def existe_persona_por_ci(ci: str):
    db = PostgreSQL()
    try:
        db.create_connection()

        query = f"SELECT 1 FROM {Config.SCHEMA}.persona WHERE ci = %s;"

        result=db.execute_query(query, (ci,), fetchone=True)

        if result:
            return True
        
        return False
    except Exception as e:
        raise ValueError(f'ERROR: {str(e)}') 
    finally:
        db.close_connection()


def existe_nombre_usuario(nombre_usuario: str):
    db = PostgreSQL()
    
    try:

        db.create_connection()

        query = f"SELECT 1 FROM {Config.SCHEMA}.usuario WHERE UPPER(nombre_usuario) = %s;"

        result=db.execute_query(query, (nombre_usuario,), fetchone=True)

        if result:
            return True
        
        return False
    except Exception as e:
        raise ValueError(f'ERROR: {str(e)}') 
    finally:
        db.close_connection()


def registrar_usuario_bd(data: dict, persona_existe: bool):
    db = PostgreSQL()

    try:
        db.create_connection()

        #SI LA PERSONA NO EXISTE LA REGISTRAMOS
        if not persona_existe:
            query_persona = """
                INSERT INTO taller.persona (ci, nombre_completo, telefono, correo, direccion)
                VALUES (%s, %s, %s, %s, %s);
            """
            params_persona = (
                data.get('ci'), data.get('nombre_completo').upper(), data.get('telefono'), 
                data.get('correo'), data.get('direccion')
            )
            
            db.execute_query(query_persona, params_persona)
        
        #INSERTAMOS EL USUARIO
        query_usuario = """
            INSERT INTO taller.usuario (nombre_usuario, password_hash, estado, ci, nro_rol, id_empresa)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING nro_usuario;
        """
        params_usuario = (
            data.get('nombre_usuario').upper(), data.get('password_hash'), data.get('estado'),
            data.get('ci'), data.get('nro_rol'), data.get('id_empresa')
        )
        
        #EJECUTAMOS EL INSERT Y HACEMOS COMMIT=TRUE PARA GUARDAR AMBOS INSERTS 
        resultado = db.execute_query(query_usuario, params_usuario, commit=True, fetchone=True)
        
        return resultado[0] if resultado else None
        
    except Exception as e:
        raise ValueError(f'ERROR: {str(e)}') 
    finally:
        db.close_connection()