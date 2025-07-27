# config_display.py - Módulo para mostrar configuración de forma organizada

from config_loader import get_current_config

def format_config_display():
    """Formatea la configuración actual en formato compacto de una línea por característica"""
    config = get_current_config()
    
    lines = []
    lines.append("📋 **CONFIGURACIÓN ACTUAL:**")
    lines.append("=" * 50)
    
    # Wake Words - formato compacto
    wake_words = config.get('wake_words', ['jarvis', 'oye jarvis', 'hey jarvis'])
    wake_words_str = ', '.join([f'"{word}"' for word in wake_words])
    lines.append(f"🎯 Wake words: {wake_words_str}")
    
    # Audio - todo en una línea
    voice_status = "ON" if config.get('voice_input_enabled', True) else "OFF"
    sample_rate = config.get('sample_rate', 16000)
    channels = config.get('channels', 1)
    volume_threshold = config.get('volume_threshold', 0.08)
    vad_mode = config.get('vad_mode', 'simple')
    lines.append(f"🎤 Audio: voice {voice_status}, rate {sample_rate//1000}kHz, channels {channels}, threshold {volume_threshold}, VAD {vad_mode}")
    
    # STT (Speech-to-Text) - compacto
    whisper_model = config.get('whisper_model_size', 'small').upper()
    use_gpu = "GPU" if config.get('use_gpu', True) else "CPU"
    no_speech_threshold = config.get('whisper_no_speech_threshold', 0.6)
    temperature = config.get('whisper_temperature', 0.0)
    lines.append(f"🗣️ STT: Whisper {whisper_model}, {use_gpu}, threshold {no_speech_threshold}, temp {temperature}")
    
    # TTS - compacto
    tts_mode = config.get('tts', 'local').upper()
    if tts_mode == 'LOCAL':
        local_tts = config.get('local_tts', {})
        voice = local_tts.get('voice', 'default')
        rate = local_tts.get('rate', 180)
        lines.append(f"🔊 TTS: {tts_mode}, voice '{voice}', {rate} wpm")
    elif tts_mode == 'ELEVENLABS':
        elevenlabs = config.get('elevenlabs', {})
        api_status = "✅" if elevenlabs.get('api_key') else "❌"
        voice_status = "✅" if elevenlabs.get('voice_id') else "❌"
        lines.append(f"🔊 TTS: {tts_mode}, API {api_status}, Voice {voice_status}")
    else:
        lines.append(f"🔊 TTS: {tts_mode}")
    
    # IA - compacto
    ai_provider = config.get('ai_provider', 'groq').upper()
    ai_mode = config.get('ai', 'local')
    lines.append(f"🤖 IA: {ai_provider} ({ai_mode})")
    
    # API Keys - formato compacto
    api_keys = []
    if config.get('groq_api_key'): api_keys.append("✅Groq")
    else: api_keys.append("❌Groq")
    if config.get('openai_api_key'): api_keys.append("✅OpenAI") 
    else: api_keys.append("❌OpenAI")
    if config.get('gemini_api_key'): api_keys.append("✅Gemini")
    else: api_keys.append("❌Gemini")
    if config.get('claude_api_key'): api_keys.append("✅Claude")
    else: api_keys.append("❌Claude")
    lines.append(f"🔑 API Keys: {' | '.join(api_keys)}")
    
    # Duraciones - compacto
    wake_dur = config.get('wake_duration', 4)
    cmd_dur = config.get('command_duration', 8)
    silence_dur = config.get('silence_duration', 1.5)
    min_rec_dur = config.get('min_recording_duration', 1.0)
    lines.append(f"⏱️ Duraciones: wake {wake_dur}s, command {cmd_dur}s, silence {silence_dur}s, min_rec {min_rec_dur}s")
    
    # Configuración avanzada - compacto
    speech_mult = config.get('speech_threshold_multiplier', 1.5)
    min_file_size = config.get('min_file_size', 1000)
    whisper_log_prob = config.get('whisper_log_prob_threshold', -1.0)
    lines.append(f"⚙️ Avanzado: speech_mult {speech_mult}, min_file {min_file_size}b, log_prob {whisper_log_prob}")
    
    # Debug - compacto
    debug_flags = []
    if config.get('debug_ai', False): debug_flags.append("AI")
    if config.get('debug_tts', False): debug_flags.append("TTS") 
    if config.get('debug_stt', False): debug_flags.append("STT")
    debug_str = ', '.join(debug_flags) if debug_flags else "OFF"
    lines.append(f"🐛 Debug: {debug_str}")
    
    # Integraciones - compacto
    integrations_config = config.get('integrations', {})
    if integrations_config:
        integration_status = []
        for name, integration_config in integrations_config.items():
            enabled = integration_config.get('enabled', True)
            status = "✅" if enabled else "❌"
            integration_status.append(f"{status}{name}")
        lines.append(f"🧩 Integraciones: {' | '.join(integration_status)}")
    else:
        lines.append("🧩 Integraciones: ninguna")
    
    lines.append("=" * 50)
    
    return "\n".join(lines)

def get_config_summary():
    """Retorna un resumen compacto de la configuración"""
    config = get_current_config()
    
    # Información clave
    voice_enabled = "✅" if config.get('voice_input_enabled', True) else "❌"
    tts_mode = config.get('tts', 'local').upper()
    ai_provider = config.get('ai_provider', 'groq').upper()
    whisper_model = config.get('whisper_model_size', 'small').upper()
    
    # Contar API keys configuradas
    api_keys = []
    if config.get('groq_api_key'): api_keys.append('Groq')
    if config.get('openai_api_key'): api_keys.append('OpenAI')
    if config.get('gemini_api_key'): api_keys.append('Gemini')
    if config.get('claude_api_key'): api_keys.append('Claude')
    
    api_keys_str = f"{len(api_keys)}/4 APIs" if api_keys else "0/4 APIs"
    
    # Contar integraciones habilitadas
    integrations = config.get('integrations', {})
    enabled_integrations = [name for name, cfg in integrations.items() if cfg.get('enabled', True)]
    integrations_str = f"{len(enabled_integrations)} activas" if enabled_integrations else "Ninguna"
    
    return (
        f"🎤{voice_enabled} | 🔊{tts_mode} | 🤖{ai_provider} | "
        f"🗣️{whisper_model} | 🔑{api_keys_str} | 🧩{integrations_str}"
    )