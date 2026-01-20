from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re

app = Flask(__name__)

# ... (El resto del código anterior permanece igual)

# Base de datos actualizada con TODOS los distritos de Chiclayo
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
    "oyotun": {"poblacion": "8,268", "electores": "6,873", "electores_hombres": "3,479 (50.618%)", "electores_mujeres": "3,394 (49.382%)"}
}

## ... (El resto del código, incluyendo la función buscar_datos_distrito y el endpoint /whatsapp, permanece igual)

def buscar_datos_distrito(mensaje):
    """Busca el nombre del distrito en el mensaje del usuario."""
    mensaje = mensaje.lower().strip()
    for distrito in distritos_data:
        if distrito in mensaje:
            return distrito
    return None

@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    # El mensaje entrante del usuario
    mensaje_usuario = request.values.get("Body", "").lower()
    respuesta = MessagingResponse()
    mensaje_respuesta = respuesta.message()

    # Lógica para buscar el distrito
    distrito_encontrado = buscar_datos_distrito(mensaje_usuario)

    if distrito_encontrado:
        datos = distritos_data[distrito_encontrado]
        # Formatea la respuesta
        texto_respuesta = (f"*Datos de {distrito_encontrado.title()}*\n\n"
                           f"👥 Población estimada (2022): {datos['poblacion']}\n"
                           f"🗳️ Electores (2025): {datos['electores']}\n"
                           f"   👨 Hombres: {datos['electores_hombres']}\n"
                           f"   👩 Mujeres: {datos['electores_mujeres']}")
    elif "hola" in mensaje_usuario or "ayuda" in mensaje_usuario:
        texto_respuesta = ("*Hola* 👋\nPregúntame por los datos de un distrito de Lambayeque.\n"
                           "*Ejemplo:* \"¿Cuántos electores hay en Pimentel?\"")
    else:
        texto_respuesta = ("No encontré ese distrito en la base de datos. "
                           "Prueba con nombres como: *Pimentel, José Leonardo Ortiz, Picsi, Tuman*.")

    mensaje_respuesta.body(texto_respuesta)
    return str(respuesta)

if __name__ == "__main__":
    app.run(debug=True)