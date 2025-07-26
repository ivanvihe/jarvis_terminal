import pyttsx3
import requests
import os
from config_loader import TTS_MODE, ELEVEN_KEY, VOICE_ID, LOCAL_TTS_RATE, LOCAL_TTS_VOICE, DEBUG_TTS

def init_tts():
    if TTS_MODE == "local":
        engine = pyttsx3.init()
        engine.setProperty('rate', LOCAL_TTS_RATE)
        if LOCAL_TTS_VOICE:
            voices = engine.getProperty('voices')
            for v in voices:
                if LOCAL_TTS_VOICE.lower() in v.name.lower():
                    engine.setProperty('voice', v.id)
                    if DEBUG_TTS:
                        print(f"[DEBUG TTS] Voz local seleccionada: {v.name}")
                    break
        if DEBUG_TTS:
            print("[DEBUG TTS] Motor local iniciado")
        print("🗣️ TTS local listo")
        return engine
    else:
        print("🗣️ Usando ElevenLabs como TTS")
        return None

def speak_response(text, engine):
    if DEBUG_TTS:
        print(f"[DEBUG TTS] Texto recibido para hablar: {text}")

    if TTS_MODE == "elevenlabs":
        try:
            headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
            data = {"text": text, "model_id": "eleven_monolingual_v1"}
            r = requests.post(url, headers=headers, json=data)
            if r.status_code == 200:
                with open("response.mp3", "wb") as f:
                    f.write(r.content)
                os.system(f"start response.mp3" if os.name == "nt" else "mpg123 response.mp3")
            else:
                print(f"❌ TTS ElevenLabs error: Status {r.status_code}")
        except Exception as e:
            print(f"❌ TTS ElevenLabs error: {e}")
    else:
        try:
            if len(text) > 200:
                parts = text.split('. ')
                for part in parts:
                    engine.say(part.strip())
                    engine.runAndWait()
            else:
                engine.say(text)
                engine.runAndWait()
            engine.stop()
            if DEBUG_TTS:
                print("[DEBUG TTS] Texto hablado con motor local")
        except Exception as e:
            print(f"❌ TTS local error: {e}")
