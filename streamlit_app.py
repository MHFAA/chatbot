import streamlit as st
import openai
import os
import tempfile

# 🔹 Instalación Automática de Librerías
try:
    from deep_translator import GoogleTranslator
except ModuleNotFoundError:
    os.system("pip install deep-translator")
    from deep_translator import GoogleTranslator

try:
    from gtts import gTTS
except ModuleNotFoundError:
    os.system("pip install gtts")
    from gtts import gTTS

# 🔐 Clave API de OpenAI (⚠️ No subas este código a GitHub con la clave visible)
OPENAI_API_KEY = "SECRET KEY"

# Verificar si la clave API está disponible
if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
    st.error("⚠️ No se encontró una clave API válida. Asegúrate de agregar tu clave en el código.")
    st.stop()

# Configurar OpenAI API
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Lista de idiomas disponibles
LANGUAGES = {
    "Inglés": "en",  # AHORA INGLÉS ES EL PRIMERO EN LA LISTA
    "Español": "es",
    "Árabe": "ar",
    "Urdu": "ur",
    "Ucraniano": "uk",
    "Coreano": "ko"
}

# Configuración de la app en Streamlit
st.set_page_config(page_title="Asistente para Migrantes", layout="wide")

# 💡 Ahora el idioma por defecto es INGLÉS
selected_lang = st.selectbox("🌎 Select your language:", list(LANGUAGES.keys()), index=0)
lang_code = LANGUAGES[selected_lang]

# Traducir la interfaz automáticamente
def translate_text(text, lang_code):
    return GoogleTranslator(source="es", target=lang_code).translate(text)

# Traducir todos los textos de la interfaz
title = translate_text("Chatbot de Ayuda para Migrantes y Refugiados", lang_code)
subtitle = translate_text("Escribe tu pregunta sobre alojamiento, empleo, trámites o asistencia sanitaria en tu nueva ciudad.", lang_code)
input_prompt = translate_text("¿Cómo quieres ingresar tu pregunta?", lang_code)
write_option = translate_text("Escribir", lang_code)
audio_option = translate_text("Subir archivo de audio", lang_code)
chat_input_placeholder = translate_text("Escribe tu pregunta aquí...", lang_code)

# Mostrar los textos traducidos en la interfaz
st.title(f"🌍 {title}")
st.write(subtitle)

# Selector de entrada de texto o audio
st.write(f"🔊 {input_prompt}")
input_method = st.radio("", (write_option, audio_option))

# Inicializar `user_input`
user_input = ""

# Función para obtener respuesta del chatbot
def get_response(user_input, lang_code):
    translated_input = GoogleTranslator(source=lang_code, target="en").translate(user_input)

    prompt = f"""
    Actúa como un asistente de ayuda para migrantes y refugiados que llegan a una nueva ciudad. 
    Responde a preguntas sobre alojamiento, trámites legales, empleo, asistencia sanitaria y recursos esenciales.
    La pregunta del usuario es: {translated_input}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Eres un asistente experto en orientación para migrantes y refugiados."},
                      {"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content

        translated_answer = GoogleTranslator(source="en", target=lang_code).translate(answer)

        return translated_answer
    except Exception as e:
        return f"❌ Error en la API: {str(e)}"

# Función para convertir texto en voz
def text_to_speech(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

# Entrada de texto o voz
if input_method == audio_option:
    audio_file = st.file_uploader(translate_text("🎤 Sube un archivo de audio (MP3/WAV)", lang_code), type=["mp3", "wav"])
    if audio_file:
        st.audio(audio_file, format="audio/mp3")
        st.info(translate_text("🚀 La transcripción automática aún no está disponible en esta versión.", lang_code))
        user_input = "Transcripción no implementada"
else:
    user_input = st.chat_input(chat_input_placeholder)

# Procesar la entrada del usuario
if user_input and user_input != "Transcripción no implementada":
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = get_response(user_input, lang_code)
    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

    audio_path = text_to_speech(response, lang_code)
    st.audio(audio_path, format="audio/mp3")
