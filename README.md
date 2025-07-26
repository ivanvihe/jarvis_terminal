# Jarvis Terminal

Un asistente de IA personal para tu terminal, inspirado en Jarvis. Combina una interfaz de usuario textual (TUI), reconocimiento de voz, síntesis de voz y la potencia de múltiples proveedores de IA para ofrecer una experiencia de asistente conversacional directamente en tu línea de comandos.

<!--  -->

## ✨ Características Principales

- **Interfaz de Usuario en Terminal (TUI)**: Una interfaz limpia y moderna construida con [Textual](https://github.com/Textualize/textual) que muestra la conversación, el estado del sistema y logs de depuración.
- **Entrada Dual (Voz y Texto)**: Interactúa con Jarvis hablando o escribiendo directamente en la terminal.
- **Detección de Palabra de Activación**: Activa a Jarvis con "Oye Jarvis" (configurable) para dar comandos por voz sin necesidad de tocar el teclado.
- **Reconocimiento de Voz (STT)**: Utiliza `faster-whisper` para una transcripción de voz a texto rápida y precisa, con soporte para ejecución en GPU.
- **Síntesis de Voz (TTS)**: Elige entre una voz local y rápida con `pyttsx3` o voces de alta calidad en la nube con `ElevenLabs`.
- **Soporte Multi-IA**: Conéctate a diferentes modelos de lenguaje grandes (LLMs) según tus preferencias y necesidades. Proveedores soportados:
    - Groq (Llama3)
    - OpenAI (GPT-3.5-Turbo, GPT-4, etc.)
    - Google (Gemini Pro)
    - Anthropic (Claude 3 Haiku)
- **Memoria Persistente**: Jarvis puede recordar información entre sesiones. Pídele que recuerde algo y lo guardará en `memory.json`.
- **Sistema de Correcciones**: Mejora la precisión del reconocimiento de voz añadiendo correcciones personalizadas en `corrections.json` para palabras o frases que Whisper no transcribe bien.
- **Altamente Configurable**: Personaliza casi todos los aspectos del asistente, desde las palabras de activación hasta los umbrales de audio, a través de un único archivo `config.json`.

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.8 o superior.
- `git` para clonar el repositorio.
- **`ffmpeg`**: Es necesario para el procesamiento de audio de Whisper.
    - **Windows**: `choco install ffmpeg` o descárgalo desde su web oficial y añádelo al PATH.
    - **macOS**: `brew install ffmpeg`
    - **Linux (Debian/Ubuntu)**: `sudo apt update && sudo apt install ffmpeg`

### 1. Clonar el Repositorio

```bash
git clone https://github.com/your-username/jarvis_terminal.git
cd jarvis_terminal
```

### 2. Instalar Dependencias

Se recomienda crear un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

Luego, instala las dependencias necesarias. Puedes crear un archivo `requirements.txt` con el siguiente contenido y ejecutar `pip install -r requirements.txt`:

```txt
# requirements.txt
requests
pyttsx3
faster-whisper
torch
pyaudio
numpy
textual
psutil
```

*Nota sobre `torch`*: Si tienes una GPU NVIDIA compatible, puedes instalar la versión con soporte CUDA para un rendimiento mucho mayor en el STT. Consulta las instrucciones oficiales de PyTorch.

*Nota sobre `pyaudio`*: En Linux, puede que necesites instalar `portaudio` primero: `sudo apt-get install portaudio19-dev`.

### 3. Crear el archivo `config.json`

Crea un archivo llamado `config.json` en la raíz del proyecto. Puedes usar este ejemplo como plantilla y modificarlo según tus necesidades.

```json
{
  "voice_input_enabled": true,
  "sample_rate": 16000,
  "volume_threshold": 0.08,
  "wake_words": ["oye jarvis", "hey jarvis", "jarvis"],
  "whisper_model_size": "small",
  "use_gpu": true,
  "tts": "local",
  "ai_provider": "groq",
  "debug_ai": false,
  "debug_tts": false,
  "debug_stt": false,
  "silence_duration": 1.5,

  "elevenlabs": {
    "api_key": "TU_API_KEY_DE_ELEVENLABS",
    "voice_id": "ID_DE_LA_VOZ_QUE_QUIERES_USAR"
  },

  "local_tts": {
    "voice": "helena",
    "rate": 180
  },

  "groq_api_key": "TU_API_KEY_DE_GROQ",
  "openai_api_key": "TU_API_KEY_DE_OPENAI",
  "gemini_api_key": "TU_API_KEY_DE_GEMINI",
  "claude_api_key": "TU_API_KEY_DE_CLAUDE"
}
```

**Explicación de claves importantes:**
- `ai_provider`: Elige entre `"groq"`, `"openai"`, `"gemini"`, `"claude"`.
- `tts`: Elige entre `"local"` o `"elevenlabs"`.
- `whisper_model_size`: Modelos disponibles: `"tiny"`, `"base"`, `"small"`, `"medium"`, `"large-v3"`. Modelos más grandes son más precisos pero más lentos y consumen más recursos.
- `use_gpu`: Ponlo en `true` si tienes una GPU NVIDIA compatible y has instalado la versión correcta de `torch`.
- Rellena las claves API (`..._api_key`) para los servicios que quieras usar.

### 4. (Opcional) Crear `corrections.json`

Si notas que el reconocimiento de voz falla consistentemente con ciertas palabras (por ejemplo, nombres propios o términos técnicos), puedes crear un archivo `corrections.json` para solucionarlo.

Ejemplo de `corrections.json`:

```json
{
  "faster whisper": "faster-whisper",
  "textualais": "textualize",
  "grook": "groq"
}
```
El sistema reemplazará automáticamente la clave (texto incorrecto) por el valor (texto correcto) en la transcripción.

## ▶️ Uso

Una vez configurado, ejecuta el asistente desde la raíz del proyecto:

```bash
python jarvis.py
```

- **Para hablar**: Di la palabra de activación (p. ej., "Oye Jarvis") seguida de tu comando.
- **Para escribir**: Simplemente escribe tu comando en el campo de entrada en la parte inferior de la pantalla y presiona Enter.
- **Para salir**: Escribe `salir` o `adios`, o presiona `Ctrl+C`.

## 🏗️ Estructura del Proyecto

- `jarvis.py`: El punto de entrada principal. Orquesta la inicialización y los bucles de entrada.
- `ai.py`: Contiene la lógica para comunicarse con las diferentes APIs de los proveedores de IA.
- `stt.py`: Gestiona la grabación de audio y la transcripción con `faster-whisper`.
- `tts.py`: Gestiona la síntesis de voz para el motor local o ElevenLabs.
- `jarvis_ui.py`: Define la interfaz de usuario con `textual`.
- `ui_bridge.py`: Actúa como un puente para comunicar de forma segura entre el backend (Jarvis) y el frontend (la TUI).
- `config_loader.py`: Carga y proporciona acceso a los valores de `config.json`.
- `memory.py`: Implementa la clase `Memory` para cargar y guardar el historial de la conversación.
- `corrections.py`: Carga y aplica las correcciones del archivo `corrections.json`.