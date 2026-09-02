import os
import json
from groq import Groq
from app.repos import diagnostico_repos

def generar_diagnostico_ia(nro_emergencia: int):
    contexto = diagnostico_repos.get_contexto_emergencia(nro_emergencia)
    if not contexto:
        raise ValueError(f"No se encontró la emergencia {nro_emergencia}.")

    # 1. Buscamos si el usuario adjuntó una imagen real en Base64
    imagen_base64 = None
    for ev in contexto["evidencias"]:
        # Si la descripción guardada es el Base64 puro que recuperamos del repositorio
        if str(ev["descripcion"]).startswith("data:image"):
            imagen_base64 = ev["descripcion"]
            break

    # 2. Construimos las instrucciones maestras
    prompt_instrucciones = _construir_prompt_mecanico(contexto)
    
    # 3. Llamamos a la IA pasándole la imagen de forma multimodal si existe
    try:
        respuesta_texto = _llamar_ia_vision(prompt_instrucciones, imagen_base64)
        resultado_json = _parsear_respuesta(respuesta_texto)
    except Exception as e:
        raise ValueError(f"Falla al contactar con la IA de Visión: {str(e)}")

    return {
        "success": True,
        "message": "Diagnóstico y análisis visual generado exitosamente por Llama Vision.",
        "data": resultado_json
    }

def _construir_prompt_mecanico(ctx: dict) -> str:
    em = ctx["emergencia"]
    # Filtramos las evidencias de texto normales (como audios ya transcritos)
    ev_texto = [f"- {e['tipo_archivo']}: {e['descripcion']}" for e in ctx["evidencias"] if not e['descripcion'].startswith("data:image")]
    ev_txt = "\n".join(ev_texto) if ev_texto else "Ninguna descripción de texto extra."

    return f"""Eres un mecánico automotriz experto y jefe de soporte.
Tu tarea es analizar los datos del incidente y la imagen adjunta (si corresponde) para emitir un pre-diagnóstico preciso.

═══════════════════════════════════════
DATOS DEL VEHÍCULO E INFORME DEL CLIENTE
═══════════════════════════════════════
Vehículo          : {em['marca_modelo']} (Año: {em['año_vehiculo']})
Incidente Inicial : {em['tipo_emergencia']}
Síntomas de Texto : {ev_txt}

═══════════════════════════════════════
INSTRUCCIÓN DE ANÁLISIS VISUAL
═══════════════════════════════════════
Si hay una imagen adjunta, actúa como inspector: analiza visualmente la pieza, el choque, la llanta o el motor para identificar daños visibles que coincidan con la falla '{em['tipo_emergencia']}'.

Responde ÚNICAMENTE con un objeto JSON válido, sin formato markdown:
{{
    "diagnostico_estimado": "<Explicación técnica deductiva basada en los síntomas y la inspección de la imagen>",
    "prioridad_sugerida": "<ALTA, MEDIA o BAJA>",
    "requiere_grua": <true o false>
}}
"""

def _llamar_ia_vision(prompt: str, imagen_base64: str = None) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("La variable GROQ_API_KEY no está configurada.")

    client = Groq(api_key=api_key)
    
    # Si NO hay imagen, usamos una petición de texto tradicional liviana
    if not imagen_base64:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()

    # Si SÍ hay una imagen en Base64, estructuramos un contenido MULTIMODAL para el modelo de visión
    content_multimodal = [
        {"type": "text", "text": prompt},
        {
            "type": "image_url",
            "image_url": {
                "url": imagen_base64  # Mandamos el string data:image/jpeg;base64,... directo
            }
        }
    ]

    response = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",  # <-- ESTE MODELO TIENE CÓDIGO DE VISIÓN
        messages=[{"role": "user", "content": content_multimodal}],
        max_tokens=300,
        temperature=0.1
    )
    return response.choices[0].message.content.strip()

def _parsear_respuesta(texto: str) -> dict:
    texto_limpio = texto.strip()
    if texto_limpio.startswith("```"):
        texto_limpio = texto_limpio.split("```")[1]
        if texto_limpio.lower().startswith("json"):
            texto_limpio = texto_limpio[4:]
        texto_limpio = texto_limpio.strip()
    try:
        return json.loads(texto_limpio)
    except Exception:
        raise ValueError(f"La IA no devolvió un JSON limpio: {texto_limpio}")