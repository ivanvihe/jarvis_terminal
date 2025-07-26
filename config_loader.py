# config_loader.py

import json

try:
    with open("config.json", "r", encoding="utf-8") as cfg_file:
        config = json.load(cfg_file)
except Exception as e:
    print(f"❌ No se pudo cargar config.json: {e}")
    config = {}

# Configuración general
VOICE_INPUT_ENABLED = config.get("voice_input_enabled", True)
SAMPLE_RATE = config.get("sample_rate", 16000)
CHANNELS = config.get("channels", 1)
VOLUME_THRESHOLD = config.get("volume_threshold", 0.08)
VAD_MODE = config.get("vad_mode", "simple")  # "simple" o "webrtcvad"
WAKE_WORDS = config.get("wake_words", ["jarvis", "oye jarvis", "hey jarvis"])
WAKE_DURATION = config.get("wake_duration", 4)
COMMAND_DURATION = config.get("command_duration", 8)
WHISPER_MODEL_SIZE = config.get("whisper_model_size", "small")
USE_GPU = config.get("use_gpu", True)
TTS_MODE = config.get("tts", "local")
AI_PROVIDER = config.get("ai_provider", "groq")
DEBUG_AI = config.get("debug_ai", False)
DEBUG_TTS = config.get("debug_tts", False)
DEBUG_STT = config.get("debug_stt", False)

AI_MODE = config.get("ai", "local")

# Configuración avanzada de audio (nuevos parámetros)
SPEECH_THRESHOLD_MULTIPLIER = config.get("speech_threshold_multiplier", 1.5)
SILENCE_DURATION = config.get("silence_duration", 1.5)
MIN_RECORDING_DURATION = config.get("min_recording_duration", 1.0)
MIN_FILE_SIZE = config.get("min_file_size", 1000)

# Configuración avanzada de Whisper (nuevos parámetros)
WHISPER_NO_SPEECH_THRESHOLD = config.get("whisper_no_speech_threshold", 0.6)
WHISPER_TEMPERATURE = config.get("whisper_temperature", 0.0)
WHISPER_LOG_PROB_THRESHOLD = config.get("whisper_log_prob_threshold", -1.0)

# Configuración ElevenLabs
eleven_config = config.get("elevenlabs", {})
ELEVEN_KEY = eleven_config.get("api_key")
VOICE_ID = eleven_config.get("voice_id")

# Configuración TTS local
local_tts_config = config.get("local_tts", {})
LOCAL_TTS_VOICE = local_tts_config.get("voice", None)
LOCAL_TTS_RATE = local_tts_config.get("rate", 180)

# Claves API para otros proveedores AI
groq_key = config.get("groq_api_key")
openai_key = config.get("openai_api_key")
gemini_key = config.get("gemini_api_key")
claude_key = config.get("claude_api_key")