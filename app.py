from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re
from datetime import datetime
import sqlite3
import json
from difflib import get_close_matches

app = Flask(__name__)

# ========== SISTEMA DE DISTRITOS (MANTENIDO EXACTAMENTE IGUAL) ==========

# Base de datos con TODOS los 35 distritos de Lambayeque
distritos_data = {
    "pucalá": {"poblacion": "9,062", "electores": "6,784", "electores_hombres": "3,314 (48.850%)", "electores_mujeres": "3,470 (51.150%)"},
    "saña": {"poblacion": "12,654", "electores": "7,856", "electores_hombres": "3,982 (50.687%)", "electores_mujeres": "3,874 (49.313%)"},
    "cayalti": {"poblacion": "15,153", "electores": "13,087", "electores_hombres": "6,347 (48.499%)", "electores_mujeres": "6,740 (51.501%)"},
    "nueva arica": {"poblacion": "2,561", "electores": "2,233", "electores_hombres": "1,125 (50.381%)", "electores_mujeres": "1,108 (49.619%)"},
    "lagunas": {"poblacion": "11,074", "electores": "8,194", "electores_hombres": "4,084 (49.841%)", "electores_mujeres": "4,110 (50.159%)"},
    "eten": {"poblacion": "13,542", "electores": "9,893", "electores_hombres": "4,739 (47.903%)", "electores_mujeres": "5,154 (52.097%)"},
    "eten puerto": {"poblacion": "2,471", "electores": "2,249", "electores_hombres": "1,145 (50.912%)", "electores_mujeres": "1,104 (49.088%)"},
    "reque": {"poblacion": "18,318", "electores": "13,267", "electores_hombres": "6,425 (48.428%)", "electores_mujeres": "6,842 (51.572%)"},
    "monsefú": {"poblacion": "36,188", "electores": "30,293", "electores_hombres": "14,525 (47.948%)", "electores_mujeres": "15,768 (52.052%)"},
    "santa rosa": {"poblacion": "14,366", "electores": "10,004", "electores_hombres": "5,005 (50.030%)", "electores_mujeres": "4,999 (49.970%)"},
    "la victoria": {"poblacion": "100,801", "electores": "74,326", "electores_hombres": "36,198 (48.702%)", "electores_mujeres": "38,128 (51.298%)"},
    "pomalca": {"poblacion": "27,672", "electores": "21,440", "electores_hombres": "10,324 (48.153%)", "electores_mujeres": "11,116 (51.847%)"},
    "pimentel": {"poblacion": "53,446", "electores": "27,760", "electores_hombres": "13,188 (47.507%)", "electores_mujeres": "14,572 (52.493%)"},
    "jose leonardo ortiz": {"poblacion": "167,037", "electores": "141,401", "electores_hombres": "69,734 (49.316%)", "electores_mujeres": "71,667 (50.684%)"},
    "picsi": {"poblacion": "15,048", "electores": "7,215", "electores_hombres": "3,517 (48.746%)", "electores_mujeres": "3,698 (51.254%)"},
    "tuman": {"poblacion": "30,159", "electores": "23,391", "electores_hombres": "11,364 (48.583%)", "electores_mujeres": "12,027 (51.417%)"},
    "patapo": {"poblacion": "25,723", "electores": "17,705", "electores_hombres": "8,673 (48.986%)", "electores_mujeres": "9,032 (51.014%)"},
    "chongoyape": {"poblacion": "19,966", "electores": "15,323", "electores_hombres": "7,733 (50.467%)", "electores_mujeres": "7,590 (49.533%)"},
    "oyotun": {"poblacion": "8,268", "electores": "6,873", "electores_hombres": "3,479 (50.618%)", "electores_mujeres": "3,394 (49.382%)"},
    "olmos": {"poblacion": "57,359", "electores": "38,812", "electores_hombres": "19,773 (50.946%)", "electores_mujeres": "19,039 (49.054%)"},
    "salas": {"poblacion": "13,801", "electores": "12,618", "electores_hombres": "6,464 (51.228%)", "electores_mujeres": "6,154 (48.772%)"},
    "motupe": {"poblacion": "35,523", "electores": "24,177", "electores_hombres": "12,143 (50.225%)", "electores_mujeres": "12,034 (49.775%)"},
    "chochope": {"poblacion": "1,650", "electores": "1,709", "electores_hombres": "873 (51.083%)", "electores_mujeres": "836 (48.917%)"},
    "jayanca": {"poblacion": "20,559", "electores": "15,153", "electores_hombres": "7,482 (49.376%)", "electores_mujeres": "7,671 (50.624%)"},
    "pacora": {"poblacion": "9,292", "electores": "6,584", "electores_hombres": "3,267 (49.620%)", "electores_mujeres": "3,317 (50.380%)"},
    "illimo": {"poblacion": "9,623", "electores": "8,440", "electores_hombres": "4,185 (49.585%)", "electores_mujeres": "4,255 (50.415%)"},
    "tucume": {"poblacion": "25,048", "electores": "19,999", "electores_hombres": "9,800 (49.002%)", "electores_mujeres": "10,199 (50.998%)"},
    "mochumi": {"poblacion": "20,524", "electores": "16,194", "electores_hombres": "7,988 (49.327%)", "electores_mujeres": "8,206 (50.673%)"},
    "morrope": {"poblacion": "57,818", "electores": "37,973", "electores_hombres": "18,740 (49.351%)", "electores_mujeres": "19,233 (50.649%)"},
    "san jose": {"poblacion": "18,801", "electores": "12,655", "electores_hombres": "6,217 (49.127%)", "electores_mujeres": "6,438 (50.873%)"},
    "cañaris": {"poblacion": "12,096", "electores": "11,513", "electores_hombres": "6,081 (52.819%)", "electores_mujeres": "5,432 (47.181%)"},
    "incahuasi": {"poblacion": "15,266", "electores": "12,336", "electores_hombres": "6,101 (49.457%)", "electores_mujeres": "6,235 (50.543%)"},
    "pitipo": {"poblacion": "22,242", "electores": "17,241", "electores_hombres": "8,601 (49.887%)", "electores_mujeres": "8,640 (50.113%)"},
    "manuel antonio mesones muro": {"poblacion": "4,210", "electores": "3,619", "electores_hombres": "1,899 (52.473%)", "electores_mujeres": "1,720 (47.527%)"},
    "pueblo nuevo": {"poblacion": "16,135", "electores": "11,562", "electores_hombres": "5,677 (49.101%)", "electores_mujeres": "5,885 (50.899%)"}
}

# Diccionario alternativo para búsquedas por nombres cortos (DISTRITOS)
nombres_alternativos_distritos = {
    "mesones muro": "manuel antonio mesones muro",
    "mesones": "manuel antonio mesones muro",
    "jlo": "jose leonardo ortiz"
}

# ========== FUNCIONES DE DISTRITOS (MANTENIDAS EXACTAMENTE IGUAL) ==========

def buscar_datos_distrito(mensaje):
    """Busca el nombre del distrito en el mensaje del usuario."""
    mensaje = mensaje.lower().strip()
    
    # Primero verifica nombres alternativos
    for nombre_corto, nombre_completo in nombres_alternativos_distritos.items():
        if nombre_corto in mensaje:
            return nombre_completo
    
    # Luego busca en los distritos principales
    for distrito in distritos_data:
        if distrito in mensaje:
            return distrito
    
    return None

def obtener_lista_distritos():
    """Genera una lista formateada de todos los distritos disponibles."""
    distritos_ordenados = sorted(distritos_data.keys())
    
    # Dividir en grupos para mejor presentación
    grupo1 = distritos_ordenados[:18]
    grupo2 = distritos_ordenados[18:]
    
    lista = "*Primera parte:*\n"
    for i, distrito in enumerate(grupo1, 1):
        nombre_formateado = distrito.title()
        lista += f"{i}. {nombre_formateado}\n"
    
    lista += "\n*Segunda parte:*\n"
    for i, distrito in enumerate(grupo2, 19):
        nombre_formateado = distrito.title()
        lista += f"{i}. {nombre_formateado}\n"
    
    return lista

def obtener_top_5_distritos(criterio="electores"):
    """Genera el top 5 de distritos según criterio."""
    texto = ""
    if criterio == "electores":
        # Ordenar por número de electores (mayor a menor)
        distritos_ordenados = sorted(
            distritos_data.items(),
            key=lambda x: int(x[1]['electores'].replace(',', '')),
            reverse=True
        )[:5]
        
        titulo = "🏆 *TOP 5 DISTRITOS CON MÁS ELECTORES*\n\n"
        for i, (nombre, datos) in enumerate(distritos_ordenados, 1):
            texto += f"{i}. *{nombre.title()}*: {datos['electores']} electores\n"
        
        texto += f"\n_Total de electores en estos 5 distritos: {sum(int(d[1]['electores'].replace(',', '')) for d in distritos_ordenados):,}_"
        return titulo + texto
    
    elif criterio == "poblacion":
        # Ordenar por población (mayor a menor)
        distritos_ordenados = sorted(
            distritos_data.items(),
            key=lambda x: int(x[1]['poblacion'].replace(',', '')),
            reverse=True
        )[:5]
        
        titulo = "👥 *TOP 5 DISTRITOS CON MÁS POBLACIÓN*\n\n"
        for i, (nombre, datos) in enumerate(distritos_ordenados, 1):
            texto += f"{i}. *{nombre.title()}*: {datos['poblacion']} habitantes\n"
        
        texto += f"\n_Total población en estos 5 distritos: {sum(int(d[1]['poblacion'].replace(',', '')) for d in distritos_ordenados):,}_"
        return titulo + texto
    
    return texto

def obtener_estadisticas_generales_distritos():
    """Calcula estadísticas generales de todos los distritos."""
    total_poblacion = sum(int(datos['poblacion'].replace(',', '')) for datos in distritos_data.values())
    total_electores = sum(int(datos['electores'].replace(',', '')) for datos in distritos_data.values())
    promedio_electores = total_electores / len(distritos_data)
    
    # Encontrar distritos extremos
    distrito_mas_electores = max(distritos_data.items(), key=lambda x: int(x[1]['electores'].replace(',', '')))
    distrito_menos_electores = min(distritos_data.items(), key=lambda x: int(x[1]['electores'].replace(',', '')))
    
    return (
        "📊 *ESTADÍSTICAS GENERALES DE LAMBAYEQUE*\n\n"
        f"• Total de distritos: {len(distritos_data)}\n"
        f"• Población total estimada (2022): {total_poblacion:,}\n"
        f"• Total de electores (2025): {total_electores:,}\n"
        f"• Promedio de electores por distrito: {promedio_electores:,.0f}\n\n"
        f"🏆 *Récords:*\n"
        f"• Más electores: *{distrito_mas_electores[0].title()}* ({distrito_mas_electores[1]['electores']})\n"
        f"• Menos electores: *{distrito_menos_electores[0].title()}* ({distrito_menos_electores[1]['electores']})\n\n"
        f"_Datos actualizados al 10/06/2025_"
    )

# ========== SISTEMA DE INFORMACIÓN POLÍTICA ==========

# Diccionario para manejar estado de conversación por usuario (POLÍTICA)
conversaciones_politica = {}

# Base de datos de ejemplo para partidos y candidatos (en producción usarías scraping del JNE)
partidos_politicos = {
    "apra": {
        "nombre_completo": "Partido Aprista Peruano",
        "diputados": [
            {"nombre": "Juan Pérez García", "dni": "12345678"},
            {"nombre": "María López Soto", "dni": "87654321"},
            {"nombre": "Carlos Ramírez Mendoza", "dni": "45678912"}
        ],
        "senadores": [],
        "presidente": {"nombre": "Luis Castillo Ríos", "dni": "98765432"},
        "alcaldes": []
    },
    "alianza para el progreso": {
        "nombre_completo": "Alianza para el Progreso",
        "diputados": [
            {"nombre": "Ana Torres Villegas", "dni": "23456789"},
            {"nombre": "Pedro Sánchez Ruiz", "dni": "76543210"}
        ],
        "senadores": [],
        "presidente": {"nombre": "César Acuña Peralta", "dni": "87654321"},
        "alcaldes": []
    },
    "fuerza popular": {
        "nombre_completo": "Fuerza Popular",
        "diputados": [
            {"nombre": "Keiko Fujimori Higuchi", "dni": "01234567"},
            {"nombre": "Lourdes Flores Nano", "dni": "12345098"}
        ],
        "senadores": [],
        "presidente": {"nombre": "Keiko Fujimori Higuchi", "dni": "01234567"},
        "alcaldes": []
    }
}

# Hoja de vida de ejemplo (en producción usarías scraping del JNE)
hojas_vida = {
    "12345678": {
        "nombre": "Juan Pérez García",
        "dni": "12345678",
        "partido": "Partido Aprista Peruano",
        "cargo": "Diputado",
        "datos_personales": {
            "sexo": "Masculino",
            "lugar_nacimiento": "Lima, Lima, Lima",
            "lugar_domicilio": "Lambayeque, Chiclayo, Chiclayo"
        },
        "educacion": [
            {"nivel": "Primaria", "institucion": "Colegio Nacional 123", "año": "1990"},
            {"nivel": "Secundaria", "institucion": "Colegio Nacional 123", "año": "1996"},
            {"nivel": "Universitario", "institucion": "Universidad Nacional de Trujillo", 
             "grado": "Bachiller en Derecho", "año": "2002"}
        ],
        "experiencia": [
            {"cargo": "Asesor", "institucion": "Congreso de la República", "periodo": "2010-2011"},
            {"cargo": "Regidor", "institucion": "Municipalidad de Chiclayo", "periodo": "2011-2014"}
        ],
        "patrimonio": {
            "ingresos": 120000,
            "bienes": ["Casa en Chiclayo", "Terreno en Lambayeque"]
        },
        "antecedentes": []
    },
    "87654321": {
        "nombre": "María López Soto",
        "dni": "87654321",
        "partido": "Partido Aprista Peruano",
        "cargo": "Diputado",
        "datos_personales": {
            "sexo": "Femenino",
            "lugar_nacimiento": "Chiclayo, Lambayeque, Lambayeque",
            "lugar_domicilio": "Lambayeque, Chiclayo, La Victoria"
        },
        "educacion": [
            {"nivel": "Primaria", "institucion": "Colegio Santa María", "año": "1992"},
            {"nivel": "Secundaria", "institucion": "Colegio Santa María", "año": "1998"},
            {"nivel": "Universitario", "institucion": "Universidad de Chiclayo", 
             "grado": "Bachiller en Economía", "año": "2004"}
        ],
        "experiencia": [
            {"cargo": "Economista", "institucion": "Ministerio de Economía", "periodo": "2005-2010"},
            {"cargo": "Consejera Regional", "institucion": "Gobierno Regional Lambayeque", "periodo": "2011-2014"}
        ],
        "patrimonio": {
            "ingresos": 95000,
            "bienes": ["Departamento en Chiclayo"]
        },
        "antecedentes": []
    }
}

def menu_principal_unificado():
    """Genera el menú principal unificado con ambas funcionalidades."""
    return (
        "🤖 *BOT DE INFORMACIÓN - PERÚ*\n\n"
        "📌 *Elige una opción:*\n\n"
        
        "🏛️ *INFORMACIÓN POLÍTICA:*\n"
        "1. 📋 *Partidos políticos*\n"
        "   Ver lista de partidos registrados\n\n"
        
        "🗺️ *INFORMACIÓN TERRITORIAL:*\n"
        "2. 🔍 *Buscar distrito*\n"
        "   Ejemplo: \"Pimentel\" o \"Monsefú\"\n"
        "3. 🏆 *Top 5 distritos*\n"
        "   Por electores o población\n"
        "4. 📊 *Estadísticas generales*\n"
        "   Totales de Lambayeque\n"
        "5. 📋 *Lista completa de distritos*\n\n"
        
        "❓ *OTRAS OPCIONES:*\n"
        "6. ℹ️ *Ayuda*\n"
        "   Cómo usar el bot\n\n"
        "---\n"
        "También puedes escribir directamente:\n"
        "• Nombre de un *distrito* (ej: \"Pimentel\")\n"
        "• Nombre de un *partido* (ej: \"APRA\")\n"
        "• \"Partidos\" para lista política"
    )

def menu_partidos_politica():
    """Genera mensaje con lista de partidos políticos."""
    mensaje = "📋 *PARTIDOS POLÍTICOS REGISTRADOS*\n\n"
    
    for i, (codigo, info) in enumerate(partidos_politicos.items(), 1):
        mensaje += f"{i}. *{info['nombre_completo']}*\n"
        mensaje += f"   Código: {codigo.upper()}\n\n"
    
    mensaje += "---\n"
    mensaje += "Escribe el *nombre o código del partido* que te interesa.\n"
    mensaje += "*Ejemplo:* \"APRA\" o \"Partido Aprista Peruano\""
    
    return mensaje

def menu_cargos_partido(partido_nombre):
    """Genera menú de cargos para un partido específico."""
    if partido_nombre.lower() in partidos_politicos:
        info = partidos_politicos[partido_nombre.lower()]
        mensaje = f"🏛️ *{info['nombre_completo'].upper()}*\n\n"
        mensaje += "Selecciona el tipo de candidato:\n\n"
        
        if info['diputados']:
            mensaje += "1. 🗳️ *Diputados* (" + str(len(info['diputados'])) + " candidatos)\n"
        else:
            mensaje += "1. 🗳️ Diputados (No disponible)\n"
            
        if info['senadores']:
            mensaje += "2. ⚖️ *Senadores* (" + str(len(info['senadores'])) + " candidatos)\n"
        else:
            mensaje += "2. ⚖️ Senadores (No disponible)\n"
            
        if info['presidente']:
            mensaje += "3. 🎖️ *Presidente*\n"
        else:
            mensaje += "3. 🎖️ Presidente (No disponible)\n"
            
        if info['alcaldes']:
            mensaje += "4. 🏙️ *Alcaldes* (" + str(len(info['alcaldes'])) + " candidatos)\n"
        else:
            mensaje += "4. 🏙️ Alcaldes (No disponible)\n"
            
        mensaje += "5. ↩️ *Volver a partidos*\n\n"
        mensaje += "Escribe el número o el nombre del cargo.\n"
        mensaje += "*Ejemplo:* \"1\" o \"Diputados\""
        
        return mensaje
    else:
        return "❌ Partido no encontrado. Escribe *\"partidos\"* para ver la lista."

def obtener_candidatos_partido(partido_nombre, cargo):
    """Obtiene candidatos de un partido para un cargo específico."""
    if partido_nombre.lower() not in partidos_politicos:
        return None
    
    info = partidos_politicos[partido_nombre.lower()]
    
    if cargo.lower() == "diputados":
        return info['diputados']
    elif cargo.lower() == "senadores":
        return info['senadores']
    elif cargo.lower() == "presidente":
        return [info['presidente']] if info['presidente'] else []
    elif cargo.lower() == "alcaldes":
        return info['alcaldes']
    
    return None

def formato_hoja_vida_politica(datos):
    """Formatea la hoja de vida para mostrar en WhatsApp."""
    if not datos:
        return "❌ No se encontró la hoja de vida de este candidato."
    
    mensaje = f"📄 *HOJA DE VIDA - {datos['nombre']}*\n\n"
    mensaje += f"🆔 *DNI:* {datos.get('dni', 'No disponible')}\n"
    mensaje += f"🏛️ *Partido:* {datos.get('partido', 'No disponible')}\n"
    mensaje += f"🎖️ *Cargo:* {datos.get('cargo', 'No disponible')}\n"
    
    # Información personal
    if 'datos_personales' in datos:
        mensaje += "\n👤 *INFORMACIÓN PERSONAL*\n"
        mensaje += f"• Sexo: {datos['datos_personales'].get('sexo', 'N/A')}\n"
        mensaje += f"• Lugar Nacimiento: {datos['datos_personales'].get('lugar_nacimiento', 'N/A')}\n"
        mensaje += f"• Domicilio: {datos['datos_personales'].get('lugar_domicilio', 'N/A')}\n"
    
    # Educación
    if 'educacion' in datos and datos['educacion']:
        mensaje += "\n🎓 *FORMACIÓN ACADÉMICA*\n"
        for estudio in datos['educacion'][:3]:  # Mostrar solo primeros 3
            nivel = estudio.get('nivel', '')
            institucion = estudio.get('institucion', '')
            año = estudio.get('año', '')
            grado = estudio.get('grado', '')
            
            if grado:
                mensaje += f"• {nivel}: {grado} en {institucion} ({año})\n"
            else:
                mensaje += f"• {nivel}: {institucion} ({año})\n"
        
        if len(datos['educacion']) > 3:
            mensaje += f"• ... y {len(datos['educacion']) - 3} estudios más\n"
    
    # Experiencia laboral
    if 'experiencia' in datos and datos['experiencia']:
        mensaje += "\n💼 *EXPERIENCIA LABORAL*\n"
        for exp in datos['experiencia'][:2]:  # Mostrar solo primeras 2
            mensaje += f"• {exp.get('cargo', '')} en {exp.get('institucion', '')} ({exp.get('periodo', '')})\n"
        
        if len(datos['experiencia']) > 2:
            mensaje += f"• ... y {len(datos['experiencia']) - 2} experiencias más\n"
    
    # Información patrimonial
    if 'patrimonio' in datos:
        mensaje += "\n💰 *INFORMACIÓN PATRIMONIAL*\n"
        if 'ingresos' in datos['patrimonio']:
            mensaje += f"• Ingresos anuales: S/ {datos['patrimonio']['ingresos']:,}\n"
        if 'bienes' in datos['patrimonio'] and datos['patrimonio']['bienes']:
            mensaje += f"• Bienes declarados: {len(datos['patrimonio']['bienes'])}\n"
            for bien in datos['patrimonio']['bienes'][:2]:  # Mostrar solo primeros 2
                mensaje += f"  - {bien}\n"
    
    # Antecedentes
    if 'antecedentes' in datos and datos['antecedentes']:
        mensaje += "\n⚖️ *ANTECEDENTES*\n"
        for ant in datos['antecedentes']:
            mensaje += f"• {ant}\n"
    else:
        mensaje += "\n⚖️ *ANTECEDENTES:* No registra antecedentes\n"
    
    mensaje += "\n---\n"
    mensaje += "📅 *Fuente:* Datos de ejemplo - JNE\n"
    mensaje += f"*Fecha consulta:* {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    mensaje += "📌 *Comandos útiles:*\n"
    mensaje += "• \"partidos\" - Ver lista de partidos\n"
    mensaje += "• \"inicio\" - Volver al menú principal\n"
    mensaje += "• \"ayuda\" - Instrucciones completas"
    
    return mensaje

def buscar_candidato_por_nombre(nombre):
    """Busca un candidato por nombre aproximado."""
    nombre_lower = nombre.lower()
    
    # Buscar en todas las hojas de vida
    for dni, datos in hojas_vida.items():
        if nombre_lower in datos['nombre'].lower():
            return datos
    
    # Búsqueda aproximada
    todos_nombres = [datos['nombre'] for datos in hojas_vida.values()]
    coincidencias = get_close_matches(nombre, todos_nombres, n=1, cutoff=0.6)
    
    if coincidencias:
        for dni, datos in hojas_vida.items():
            if datos['nombre'] == coincidencias[0]:
                return datos
    
    return None

# ========== RUTA PRINCIPAL DEL BOT UNIFICADO ==========

@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    # Obtener datos del mensaje
    numero_usuario = request.values.get('From', '')
    mensaje_usuario = request.values.get('Body', '').strip()
    mensaje_lower = mensaje_usuario.lower()
    
    respuesta = MessagingResponse()
    mensaje_respuesta = respuesta.message()
    
    # Inicializar estado de conversación política si es nuevo usuario
    if numero_usuario not in conversaciones_politica:
        conversaciones_politica[numero_usuario] = {
            'estado': 'inicio',
            'partido_actual': None,
            'cargo_actual': None
        }
    
    estado = conversaciones_politica[numero_usuario]
    
    # ========== LÓGICA PRINCIPAL UNIFICADA ==========
    
    # ----- COMANDOS GLOBALES -----
    if mensaje_lower in ['hola', 'hi', 'hello', 'inicio', 'menu', 'menú']:
        texto_respuesta = menu_principal_unificado()
        estado['estado'] = 'inicio'
        estado['partido_actual'] = None
        estado['cargo_actual'] = None
    
    elif mensaje_lower in ['ayuda', 'help', '?', '6', 'opcion 6', 'opción 6']:
        texto_respuesta = (
            "❓ *AYUDA - BOT DE INFORMACIÓN PERÚ*\n\n"
            "📌 *FLUJO DE INFORMACIÓN POLÍTICA:*\n"
            "1. Escribe *\"partidos\"* o *\"1\"*\n"
            "2. Elige un partido (ej: *\"APRA\"*)\n"
            "3. Elige tipo de candidato (ej: *\"Diputados\"*)\n"
            "4. Escribe *nombre del candidato*\n\n"
            
            "📌 *FLUJO DE DISTRITOS:*\n"
            "• Escribe directamente *nombre de distrito* (ej: \"Pimentel\")\n"
            "• O usa el menú:\n"
            "  2: Buscar distrito\n"
            "  3: Top 5 distritos\n"
            "  4: Estadísticas generales\n"
            "  5: Lista completa\n\n"
            
            "📌 *COMANDOS RÁPIDOS:*\n"
            "• \"partidos\" - Lista partidos políticos\n"
            "• \"distritos\" - Lista distritos Lambayeque\n"
            "• \"estadísticas\" - Datos generales\n"
            "• \"top electores\" - Ranking distritos\n\n"
            
            "📌 *EJEMPLOS PRÁCTICOS:*\n"
            "• \"APRA\" → \"Diputados\" → \"Juan Pérez\"\n"
            "• \"Pimentel\" (datos del distrito)\n"
            "• \"2\" → \"Pimentel\" (búsqueda distrito)\n"
            "• \"3\" → \"electores\" (top 5)\n\n"
            
            "¿Necesitas más ayuda? Escribe *\"inicio\"*"
        )
    
    # ----- ESTADO: INICIO (MENÚ PRINCIPAL) -----
    elif estado['estado'] == 'inicio':
        # Opción 1: Información Política - Partidos
        if mensaje_lower in ['1', 'partidos', 'partidos políticos', 'politica', 'política']:
            texto_respuesta = menu_partidos_politica()
            estado['estado'] = 'seleccion_partido'
        
        # Opción 2: Buscar distrito
        elif mensaje_lower in ['2', 'buscar', 'buscar distrito']:
            texto_respuesta = (
                "🔍 *BUSCAR DISTRITO*\n\n"
                "Escribe el nombre del distrito que buscas:\n\n"
                "• *Ejemplos:*\n"
                "  - \"Pimentel\"\n"
                "  - \"Monsefú\"\n"
                "  - \"La Victoria\"\n"
                "  - \"José Leonardo Ortiz\"\n\n"
                "También puedes usar nombres cortos:\n"
                "• \"JLO\" para José Leonardo Ortiz\n"
                "• \"Mesones\" para Manuel Antonio Mesones Muro\n\n"
                "¿Qué distrito te interesa?"
            )
        
        # Opción 3: Top 5 distritos
        elif mensaje_lower in ['3', 'top', 'top 5', 'top5', 'ranking']:
            texto_respuesta = (
                "🏆 *TOP 5 DISTRITOS*\n\n"
                "Elige el tipo de ranking:\n\n"
                "• \"electores\" - Más electores\n"
                "• \"poblacion\" - Más población\n\n"
                "Ejemplo: Escribe *\"electores\"*"
            )
        
        # Opción 4: Estadísticas generales
        elif mensaje_lower in ['4', 'estadisticas', 'estadísticas', 'estadisticas generales']:
            texto_respuesta = obtener_estadisticas_generales_distritos()
        
        # Opción 5: Lista completa de distritos
        elif mensaje_lower in ['5', 'lista', 'listar', 'todos', 'distritos']:
            lista = obtener_lista_distritos()
            texto_respuesta = (
                f"📋 *LISTA COMPLETA DE DISTRITOS*\n\n"
                f"Tengo información de {len(distritos_data)} distritos:\n\n"
                f"{lista}\n"
                f"_Escribe el nombre de cualquier distrito para ver sus datos._"
            )
        
        # Búsqueda directa de distrito
        elif buscar_datos_distrito(mensaje_lower):
            distrito_encontrado = buscar_datos_distrito(mensaje_lower)
            datos = distritos_data[distrito_encontrado]
            texto_respuesta = (
                f"📊 *DATOS DE {distrito_encontrado.upper()}*\n\n"
                f"👥 *Población estimada (2022):* {datos['poblacion']}\n"
                f"🗳️ *Electores (al 10/06/2025):* {datos['electores']}\n"
                f"   👨 Hombres: {datos['electores_hombres']}\n"
                f"   👩 Mujeres: {datos['electores_mujeres']}\n\n"
                f"📍 *Ubicación:* Provincia de Chiclayo\n"
                f"📅 *Datos actualizados:* Junio 2025\n\n"
                f"_Fuente: Infogob JNE - Datos oficiales_\n\n"
                f"¿Qué más necesitas? Escribe *\"inicio\"* para el menú."
            )
        
        # Búsqueda directa de partido político
        elif mensaje_lower in partidos_politicos:
            texto_respuesta = menu_cargos_partido(mensaje_lower)
            estado['estado'] = 'seleccion_cargo'
            estado['partido_actual'] = mensaje_lower
        
        # Comandos de top distritos
        elif mensaje_lower in ['electores', 'top electores', 'mas electores']:
            texto_respuesta = obtener_top_5_distritos("electores")
        
        elif mensaje_lower in ['poblacion', 'población', 'top poblacion', 'mas poblacion']:
            texto_respuesta = obtener_top_5_distritos("poblacion")
        
        else:
            texto_respuesta = (
                "❓ *No entendí tu mensaje*\n\n"
                "Puedes:\n\n"
                "1. Escribir *\"inicio\"* para ver el menú\n"
                "2. Usar números del 1 al 6\n"
                "3. Escribir el nombre de un distrito\n"
                "4. Escribir *\"partidos\"* para información política\n"
                "5. Escribir *\"ayuda\"* para instrucciones\n\n"
                "*Ejemplos claros:*\n"
                "• \"Pimentel\" (datos del distrito)\n"
                "• \"APRA\" (información del partido)\n"
                "• \"2\" (buscar distrito)\n"
                "• \"estadísticas\" (datos generales)"
            )
    
    # ----- ESTADO: SELECCIÓN DE PARTIDO (POLÍTICA) -----
    elif estado['estado'] == 'seleccion_partido':
        if mensaje_lower in ['inicio', 'menu', 'menú', 'volver']:
            texto_respuesta = menu_principal_unificado()
            estado['estado'] = 'inicio'
        
        elif mensaje_lower in partidos_politicos:
            texto_respuesta = menu_cargos_partido(mensaje_lower)
            estado['estado'] = 'seleccion_cargo'
            estado['partido_actual'] = mensaje_lower
        
        else:
            # Verificar si es un partido por nombre completo
            partido_encontrado = None
            for codigo, info in partidos_politicos.items():
                if mensaje_lower in info['nombre_completo'].lower():
                    partido_encontrado = codigo
                    break
            
            if partido_encontrado:
                texto_respuesta = menu_cargos_partido(partido_encontrado)
                estado['estado'] = 'seleccion_cargo'
                estado['partido_actual'] = partido_encontrado
            else:
                texto_respuesta = (
                    f"❌ *\"{mensaje_usuario}\" no es un partido válido.*\n\n"
                    "Escribe *\"partidos\"* para ver la lista completa o\n"
                    "escribe *\"inicio\"* para volver al menú principal.\n\n"
                    "*Partidos disponibles:* APRA, Alianza para el Progreso, Fuerza Popular"
                )
    
    # ----- ESTADO: SELECCIÓN DE CARGO (POLÍTICA) -----
    elif estado['estado'] == 'seleccion_cargo':
        if mensaje_lower in ['inicio', 'menu', 'menú']:
            texto_respuesta = menu_principal_unificado()
            estado['estado'] = 'inicio'
            estado['partido_actual'] = None
        
        elif mensaje_lower in ['5', 'volver', 'atrás', 'partidos']:
            texto_respuesta = menu_partidos_politica()
            estado['estado'] = 'seleccion_partido'
            estado['partido_actual'] = None
        
        elif mensaje_lower in ['1', 'diputados', 'diputado']:
            if estado['partido_actual'] in partidos_politicos:
                candidatos = obtener_candidatos_partido(estado['partido_actual'], 'diputados')
                
                if candidatos:
                    texto_respuesta = f"🗳️ *DIPUTADOS - {partidos_politicos[estado['partido_actual']]['nombre_completo'].upper()}*\n\n"
                    for i, candidato in enumerate(candidatos, 1):
                        texto_respuesta += f"{i}. *{candidato['nombre']}*\n"
                    
                    texto_respuesta += "\n---\n"
                    texto_respuesta += "Escribe el *nombre completo* del diputado para ver su hoja de vida.\n"
                    texto_respuesta += "*Ejemplo:* \"Juan Pérez García\""
                    
                    estado['estado'] = 'lista_candidatos'
                    estado['cargo_actual'] = 'diputados'
                else:
                    texto_respuesta = f"📭 No hay diputados registrados para *{partidos_politicos[estado['partido_actual']]['nombre_completo']}*"
            else:
                texto_respuesta = "❌ Error: Partido no encontrado. Escribe *\"inicio\"*"
        
        elif mensaje_lower in ['2', 'senadores', 'senador']:
            texto_respuesta = (
                "⚠️ *SENADORES*\n\n"
                "Actualmente en Perú no existen cargos de Senadores.\n"
                "La última elección de senadores fue en 1992.\n\n"
                "Elige otro cargo o escribe *\"inicio\"* para volver."
            )
        
        elif mensaje_lower in ['3', 'presidente', 'presidencial']:
            if estado['partido_actual'] in partidos_politicos:
                candidato = partidos_politicos[estado['partido_actual']]['presidente']
                
                if candidato:
                    hoja_vida = hojas_vida.get(candidato['dni'])
                    if hoja_vida:
                        texto_respuesta = formato_hoja_vida_politica(hoja_vida)
                        estado['estado'] = 'ver_hoja_vida'
                    else:
                        texto_respuesta = f"🎖️ *PRESIDENTE: {candidato['nombre']}*\n\nHoja de vida no disponible."
                else:
                    texto_respuesta = f"📭 No hay candidato presidencial registrado para *{partidos_politicos[estado['partido_actual']]['nombre_completo']}*"
            else:
                texto_respuesta = "❌ Error: Partido no encontrado."
        
        elif mensaje_lower in ['4', 'alcaldes', 'alcalde']:
            texto_respuesta = (
                "🏙️ *ALCALDES*\n\n"
                "Los datos de candidatos a alcaldías se organizan por distrito.\n\n"
                "Próximamente: Consulta por distrito/provincia.\n\n"
                "Por ahora, puedes consultar:\n"
                "1. Diputados\n"
                "3. Presidente\n\n"
                "Escribe *\"inicio\"* para volver al menú principal."
            )
        
        else:
            texto_respuesta = (
                f"❌ Opción no válida para *{partidos_politicos[estado['partido_actual']]['nombre_completo'] if estado['partido_actual'] in partidos_politicos else 'este partido'}*\n\n"
                "Elige una opción:\n"
                "1. Diputados\n"
                "2. Senadores\n"
                "3. Presidente\n"
                "4. Alcaldes\n"
                "5. Volver a partidos"
            )
    
    # ----- ESTADO: LISTA DE CANDIDATOS (POLÍTICA) -----
    elif estado['estado'] == 'lista_candidatos':
        if mensaje_lower in ['inicio', 'menu', 'menú']:
            texto_respuesta = menu_principal_unificado()
            estado['estado'] = 'inicio'
            estado['partido_actual'] = None
            estado['cargo_actual'] = None
        
        elif mensaje_lower in ['volver', 'atrás'] and estado['partido_actual']:
            texto_respuesta = menu_cargos_partido(estado['partido_actual'])
            estado['estado'] = 'seleccion_cargo'
        
        else:
            # Buscar candidato por nombre
            hoja_vida = buscar_candidato_por_nombre(mensaje_usuario)
            
            if hoja_vida:
                texto_respuesta = formato_hoja_vida_politica(hoja_vida)
                estado['estado'] = 'ver_hoja_vida'
            else:
                # Obtener candidatos para sugerencias
                candidatos = obtener_candidatos_partido(estado['partido_actual'], estado['cargo_actual'])
                
                if candidatos:
                    nombres = [c['nombre'] for c in candidatos]
                    sugerencias = get_close_matches(mensaje_usuario, nombres, n=3, cutoff=0.5)
                    
                    texto_respuesta = f"❌ *\"{mensaje_usuario}\" no encontrado*\n\n"
                    
                    if sugerencias:
                        texto_respuesta += "¿Quizás quisiste decir?\n"
                        for sug in sugerencias:
                            texto_respuesta += f"• *{sug}*\n"
                        texto_respuesta += "\nCopia y pega el nombre exacto."
                    else:
                        texto_respuesta += "Candidatos disponibles:\n"
                        for nombre in nombres:
                            texto_respuesta += f"• {nombre}\n"
                else:
                    texto_respuesta = "📭 No hay candidatos disponibles."
    
    # ----- ESTADO: VIENDO HOJA DE VIDA (POLÍTICA) -----
    elif estado['estado'] == 'ver_hoja_vida':
        if mensaje_lower in ['inicio', 'menu', 'menú']:
            texto_respuesta = menu_principal_unificado()
            estado['estado'] = 'inicio'
            estado['partido_actual'] = None
            estado['cargo_actual'] = None
        
        elif mensaje_lower == 'partidos':
            texto_respuesta = menu_partidos_politica()
            estado['estado'] = 'seleccion_partido'
            estado['partido_actual'] = None
        
        else:
            texto_respuesta = (
                "📄 *Estás viendo una hoja de vida*\n\n"
                "Puedes:\n"
                "• Escribir *\"partidos\"* para ver todos los partidos\n"
                "• Escribir *\"inicio\"* para volver al menú principal\n"
                "• Escribir otro *nombre de candidato* para buscar\n\n"
                "¿Qué más necesitas?"
            )
    
    else:
        texto_respuesta = "🔄 Estado no reconocido. Escribe \"inicio\" para reiniciar."
        estado['estado'] = 'inicio'
    
    # Enviar respuesta
    mensaje_respuesta.body(texto_respuesta)
    return str(respuesta)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)