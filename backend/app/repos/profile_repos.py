from app.config import Config
from app.classes.postgres import PostgreSQL

def get_profile(nro_usuario):
    db=PostgreSQL()

    try:
        db.create_connection()

        query=f'''
            SELECT A.ci,A.nombre_usuario,A.fecha_registro, A.nro_usuario,A.estado,A.nro_rol,A.id_empresa,E.nombre_empresa,B.nombre_completo,B.telefono,B.correo,B.direccion,
            C.nombre_rol,COUNT(D.nro_vehiculo) AS cant_vehiculos
            FROM {Config.SCHEMA}.USUARIO A
            INNER JOIN {Config.SCHEMA}.PERSONA B ON A.ci =B.ci 
            INNER JOIN {Config.SCHEMA}.ROL C ON A.nro_rol =C.nro_rol 
            LEFT JOIN {Config.SCHEMA}.vehiculo D ON A.nro_usuario = D.nro_usuario
            LEFT JOIN {Config.SCHEMA}.empresa E ON e.id_empresa =A.id_empresa
            WHERE A.nro_usuario =%s
            GROUP BY A.ci,A.nombre_usuario,A.fecha_registro, A.nro_usuario,A.estado,A.nro_rol,A.id_empresa,E.nombre_empresa,B.nombre_completo,B.telefono,B.correo,B.direccion,
            C.nombre_rol;
        '''

        user=db.execute_query(query,(nro_usuario,),fetchone=True)

        columns=[]
        for column in  db.cur.description:
            columns.append(column[0])
        print(columns) 
        
        data=dict(zip(columns,user))

        print(data)

        return data

    except Exception as e:
        raise ValueError(f'ERROR: {str(e)}')
    finally:
        db.close_connection()

def update_profile(data:dict):
    db=PostgreSQL()
    try:
        db.create_connection()

       #PREPARAR INSERT PERSONA
        query=f"""
            UPDATE {Config.SCHEMA}.persona
            SET telefono=%s, correo=%s, direccion=%s
            WHERE ci=%s
        """
        params=(data['telefono'],data['correo'],data['direccion'],data['ci'])

        if data.get('password_hash'):
            hacer_commit=False
        else:
            hacer_commit=True

        db.execute_query(query,params,commit=hacer_commit)

        if data.get('password_hash'):
            query_user=f"""
            UPDATE {Config.SCHEMA}.usuario
            SET password_hash=%s
            WHERE nro_usuario=%s
            """
            param_user=(data['password_hash'],data['nro_usuario'])
            db.execute_query(query_user,param_user,commit=True)
        
        return {
            'success':True,
            'message':'Perfil Actualizado Correctamente.'
        }  
            
        
    except Exception as e:
        raise ValueError(f'ERROR: {str(e)}')