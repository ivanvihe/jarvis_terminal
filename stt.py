# ===========================
# stt.py (versión mejorada, escucha natural, robusto)
# ===========================
import numpy as np
import wave
import os
import time
import torch
import pyaudio
from faster_whisper import WhisperModel
from config_loader import (
    SAMPLE_RATE, CHANNELS, VOLUME_THRESHOLD, WHISPER_MODEL_SIZE,
    USE_GPU, WHISPER_NO_SPEECH_THRESHOLD, WHISPER_TEMPERATURE,
    WHISPER_LOG_PROB_THRESHOLD, SILENCE_DURATION
)

DEBUG_STT = True  # Debug activado

# Carga modelo Whisper
whisper_device = "cuda" if torch.cuda.is_available() and USE_GPU else "cpu"
print(f"🔍 Cargando modelo Whisper ({WHISPER_MODEL_SIZE}) en {whisper_device}...")
whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device=whisper_device, compute_type="default")
print("✅ Whisper listo")

def rms_from_bytes(data_bytes):
    audio_data = np.frombuffer(data_bytes, dtype=np.int16)
    if len(audio_data) == 0:
        return 0.0
    rms = np.sqrt(np.mean(np.square(audio_data.astype(np.float32))))
    return rms / 32768.0

def record_audio_simple(max_duration=12, silence_threshold=None, silence_duration=None):
    if silence_threshold is None:
        silence_threshold = VOLUME_THRESHOLD
    if silence_duration is None:
        silence_duration = SILENCE_DURATION

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    RATE = SAMPLE_RATE

    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"❌ Error inicializando audio: {e}")
        return None

    if DEBUG_STT:
        print(f"[DEBUG STT] Grabando audio (máximo {max_duration}s)...")

    frames = []
    silence_counter = 0
    speech_detected = False
    start_time = time.time()

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

            volume = rms_from_bytes(data)
            if len(frames) % 10 == 0 and DEBUG_STT:
                print(f"[DEBUG STT] Volumen: {volume:.4f}, Habla detectada: {speech_detected}")

            speech_threshold = VOLUME_THRESHOLD * 1.2
            if volume > speech_threshold:
                speech_detected = True
                silence_counter = 0
            elif volume < silence_threshold:
                silence_counter += CHUNK / RATE
            else:
                silence_counter += (CHUNK / RATE) * 0.5

            elapsed = time.time() - start_time
            if elapsed >= max_duration:
                if DEBUG_STT:
                    print("[DEBUG STT] Tiempo máximo alcanzado.")
                break

            if speech_detected and silence_counter >= silence_duration:
                if DEBUG_STT:
                    print("[DEBUG STT] Silencio detectado tras habla, terminando grabación.")
                break

    except Exception as e:
        print(f"❌ Error durante grabación: {e}")
        return None
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    if len(frames) == 0:
        print("[DEBUG STT] No se grabó ningún frame.")
        return None

    # Guardar archivo WAV
    filename = "command.wav"
    try:
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        try:
            wf.setsampwidth(p.get_sample_size(FORMAT))
        except:
            wf.setsampwidth(2)  # Fallback por defecto
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        size = os.path.getsize(filename)
        if size < 1000:
            if DEBUG_STT:
                print(f"[DEBUG STT] Archivo muy pequeño ({size} bytes), descartando.")
            return None

        if DEBUG_STT:
            print(f"[DEBUG STT] Grabación guardada como {filename} ({size} bytes)")
        return filename

    except Exception as e:
        print(f"❌ Error guardando archivo WAV: {e}")
        return None

def record_audio(duration=12):
    return record_audio_simple(max_duration=duration)

def speech_to_text(filename):
    try:
        if DEBUG_STT:
            print(f"[DEBUG STT] Transcribiendo archivo: {filename}")

        segments, info = whisper_model.transcribe(
            filename,
            language="es",
            beam_size=5,
            temperature=WHISPER_TEMPERATURE,
            no_speech_threshold=WHISPER_NO_SPEECH_THRESHOLD,
            log_prob_threshold=WHISPER_LOG_PROB_THRESHOLD,
            compression_ratio_threshold=2.4
        )

        text = "".join([s.text for s in segments]).strip()

        if DEBUG_STT:
            print(f"[DEBUG STT] Confianza promedio: {info.language_probability:.2f}")
            print(f"[DEBUG STT] Texto transcrito: '{text}'")

        if len(text) < 3:
            if DEBUG_STT:
                print("[DEBUG STT] Texto muy corto, descartando.")
            return ""

        noise_patterns = [
            "subtítulos por la comunidad",
            "gracias por ver",
            "suscríbete",
            "amara.org"
        ]

        text_lower = text.lower()
        for pattern in noise_patterns:
            if pattern in text_lower:
                if DEBUG_STT:
                    print(f"[DEBUG STT] Texto filtrado como ruido: '{text}'")
                return ""

        return text

    except Exception as e:
        print(f"❌ STT error: {e}")
        return ""
