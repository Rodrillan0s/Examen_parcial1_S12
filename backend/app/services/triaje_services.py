import os
import json
from groq import Groq
from app.repos import triaje_repos

def iniciar_chat_triaje(token_data: dict):
    id_conv = triaje_repos.iniciar_conversacion_ia_db(token_data['nro_usuario'])
    return {"id_conversacion": id_conv, "mensaje_ia": "Hola, soy el asistente virtual del taller. ¿Qué problema presenta tu vehículo hoy?"}

def interactuar_con_chatbot(id_conversacion: int, mensaje_cliente: str):
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    
    prompt = f"""
    Eres un asistente virtual de triaje mecánico automotriz. 
    El cliente acaba de decirte: "{mensaje_cliente}"
    
    Analiza la situación. Si es un problema menor (ej. cambiar una llanta, batería descargada), dale un consejo breve y amigable. 
    Si notas que es grave (ej. humo en el motor, frenos no responden, choque), debes escalar a un mecánico.
    
    Responde estrictamente en formato JSON válido:
    {{
        "respuesta_al_cliente": "Lo que le dirás al usuario",
        "escalar_a_humano": <true o false>,
        "resumen_oculto_para_mecanico": "Breve resumen técnico del problema",
        "nivel_riesgo_detectado": "BAJO, MEDIO o ALTO"
    }}
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    data_ia = json.loads(response.choices[0].message.content)
    
    # Si la IA decide escalar, actualizamos la base de datos (CU42)
    if data_ia.get("escalar_a_humano"):
        triaje_repos.escalar_conversacion_db(
            id_conversacion, 
            data_ia.get("resumen_oculto_para_mecanico"), 
            data_ia.get("nivel_riesgo_detectado")
        )
        data_ia["respuesta_al_cliente"] += "\n\n⚠️ He notificado a nuestro equipo humano. Un mecánico se pondrá en contacto contigo enseguida."

    return data_ia