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
git clone https://github.com/ivanvihe/jarvis_terminal.git
cd jarvis_terminal
```

### 2. Instalar Dependencias

Se recomienda crear un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

Luego, instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` debe contener:

```txt
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

### 3. Configuración de Archivos Necesarios

#### Archivo `config.json` (Obligatorio)

Debes crear un archivo llamado `config.json` en la raíz del proyecto. Este archivo controla el comportamiento de Jarvis. Ejemplo y explicación de cada parámetro:

```json
{
  "voice_input_enabled": true,           // Habilita/deshabilita entrada por voz
  "sample_rate": 16000,                  // Frecuencia de muestreo de audio (Hz)
  "volume_threshold": 0.08,              // Umbral de volumen para detectar voz
  "wake_words": ["oye jarvis", "hey jarvis", "jarvis"], // Palabras de activación
  "whisper_model_size": "small",        // Tamaño del modelo Whisper: "tiny", "base", "small", "medium", "large-v3"
  "use_gpu": true,                       // Usa GPU si está disponible
  "tts": "local",                       // "local" (pyttsx3) o "elevenlabs"
  "ai_provider": "groq",                // "groq", "openai", "gemini", "claude"
  "debug_ai": false,                     // Modo debug para IA
  "debug_tts": false,                    // Modo debug para TTS
  "debug_stt": false,                    // Modo debug para STT
  "silence_duration": 1.5,               // Segundos de silencio para finalizar grabación

  "elevenlabs": {
    "api_key": "TU_API_KEY_DE_ELEVENLABS", // Solo si usas ElevenLabs
    "voice_id": "ID_DE_LA_VOZ_QUE_QUIERES_USAR"
  },

  "local_tts": {
    "voice": "helena",                  // Nombre de la voz local (depende del sistema)
    "rate": 180                          // Velocidad de la voz
  },

  "groq_api_key": "TU_API_KEY_DE_GROQ",     // Solo si usas Groq
  "openai_api_key": "TU_API_KEY_DE_OPENAI", // Solo si usas OpenAI
  "gemini_api_key": "TU_API_KEY_DE_GEMINI", // Solo si usas Gemini
  "claude_api_key": "TU_API_KEY_DE_CLAUDE"  // Solo si usas Claude
}
```

**Notas importantes:**
- Rellena las claves API solo para los servicios que vayas a usar.
- Elige el proveedor de IA y TTS según tus preferencias.
- Puedes personalizar las palabras de activación y otros parámetros para adaptarlo a tu entorno.

#### Archivo `memory.json` (Obligatorio)

Este archivo almacena la memoria persistente de Jarvis (recuerdos, historial, etc). Si no existe, Jarvis lo creará automáticamente, pero puedes inicializarlo vacío:

```json
[]
```

#### Archivo `corrections.json` (Obligatorio)

Define correcciones personalizadas para mejorar la transcripción de voz. Si no existe, Jarvis lo creará automáticamente, pero puedes inicializarlo así:

```json
{
  "faster whisper": "faster-whisper",
  "textualais": "textualize",
  "grook": "groq"
}
```

Puedes añadir tantas correcciones como necesites. La clave es el texto incorrecto y el valor el texto correcto.

## ▶️ Uso

Una vez configurado, ejecuta el asistente desde la raíz del proyecto:

```bash
python jarvis.py
```

- **Para hablar**: Di la palabra de activación (p. ej., "Oye Jarvis") seguida de tu comando.
- **Para escribir**: Simplemente escribe tu comando en la parte inferior de la pantalla y presiona Enter.
- **Para salir**: Escribe `salir` o `adios`, o presiona `Ctrl+C`.

## 🏗️ Estructura del Proyecto

- `jarvis.py`: El punto de entrada principal. Orquesta la inicialización y los bucles de entrada.
- `ai.py`: Lógica para comunicarse con las diferentes APIs de los proveedores de IA.
- `stt.py`: Grabación de audio y transcripción con `faster-whisper`.
- `tts.py`: Síntesis de voz para el motor local o ElevenLabs.
- `jarvis_ui.py`: Interfaz de usuario con `textual`.
- `ui_bridge.py`: Puente entre backend (Jarvis) y frontend (TUI).
- `config_loader.py`: Carga y acceso a los valores de `config.json`.
- `memory.py`: Clase `Memory` para cargar y guardar el historial de la conversación.
- `corrections.py`: Carga y aplica las correcciones del archivo `corrections.json`.
- `integrations/`: Integraciones adicionales (ej. Gmail, Windows, etc).

---

**¡Listo! Jarvis Terminal está preparado para ser tu asistente personal en la terminal.**