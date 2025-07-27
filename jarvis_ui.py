from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.message import Message
import psutil
import time
import threading

class ChatLog(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_content = ""
        self.auto_scroll = True
        self.max_lines = 1000  # Límite de líneas para rendimiento

    def append_message(self, msg: str, sender="Jarvis"):
        sender_lower = sender.lower()
        if sender_lower == "jarvis":
            prefix = "[bold green]🤖 Jarvis:[/bold green] "
        elif sender_lower in ("user", "you"):
            prefix = "[bold cyan]🧑 You:[/bold cyan] "
        elif sender_lower == "system":
            prefix = "[bold yellow]⚙️ System:[/bold yellow] "
        elif sender_lower == "debug":
            prefix = "[bold magenta][DEBUG]:[/bold magenta] "
        elif sender_lower == "error":
            prefix = "[bold red][ERROR]:[/bold red] "
        elif sender_lower == "config":
            prefix = "[bold blue]📋 Config:[/bold blue] "
        else:
            prefix = f"[bold]{sender}:[/bold] "

        new_line = f"{prefix}{msg}\n"
        self.log_content += new_line
        
        # Mantener solo las últimas líneas para rendimiento
        lines = self.log_content.split('\n')
        if len(lines) > self.max_lines:
            self.log_content = '\n'.join(lines[-self.max_lines:])
        
        self.update(self.log_content)
        
        # Auto-scroll hacia abajo siempre
        if self.auto_scroll:
            self.call_after_refresh(self.scroll_end)

class SystemStatsWidget(Static):
    cpu = reactive(0.0)
    ram = reactive(0.0)
    uptime = reactive("0s")

    def render(self):
        return (
            f"[bold cyan]📊 SISTEMA[/bold cyan]\n"
            f"CPU: [bold]{self.cpu:.1f}%[/bold]\n"
            f"RAM: [bold]{self.ram:.1f}%[/bold]\n"
            f"Uptime: [bold]{self.uptime}[/bold]"
        )

    def watch_cpu(self, cpu): self.refresh()
    def watch_ram(self, ram): self.refresh()
    def watch_uptime(self, uptime): self.refresh()

class AudioStatusWidget(Static):
    mic_status = reactive(False)

    def render(self):
        mic_icon = "🎙️ ON" if self.mic_status else "🔇 OFF"
        mic_color = "green" if self.mic_status else "red"
        return (
            f"[bold cyan]🎤 AUDIO[/bold cyan]\n"
            f"Micrófono: [bold {mic_color}]{mic_icon}[/bold {mic_color}]"
        )

    def watch_mic_status(self, mic_status): self.refresh()

class EnginesWidget(Static):
    tts_engine = reactive("Local")
    ai_engine = reactive("Local")

    def render(self):
        return (
            f"[bold cyan]🤖 MOTORES[/bold cyan]\n"
            f"TTS: [bold green]{self.tts_engine}[/bold green]\n"
            f"AI: [bold green]{self.ai_engine}[/bold green]"
        )

    def watch_tts_engine(self, tts_engine): self.refresh()
    def watch_ai_engine(self, ai_engine): self.refresh()

class MemoryWidget(Static):
    memory_entries = reactive(0)
    corrections = reactive(0)

    def render(self):
        return (
            f"[bold cyan]🧠 MEMORIA[/bold cyan]\n"
            f"Entradas: [bold yellow]{self.memory_entries}[/bold yellow]\n"
            f"Correcciones: [bold yellow]{self.corrections}[/bold yellow]"
        )

    def watch_memory_entries(self, memory_entries): self.refresh()
    def watch_corrections(self, corrections): self.refresh()

class IntegrationsWidget(Static):
    integrations = reactive("")

    def render(self):
        integrations_display = self.integrations if self.integrations else "[dim]Ninguna activa[/dim]"
        return (
            f"[bold cyan]🧩 INTEGRACIONES[/bold cyan]\n"
            f"{integrations_display}"
        )

    def watch_integrations(self, integrations): self.refresh()

class InfoPanel(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.system_stats = SystemStatsWidget()
        self.audio_status = AudioStatusWidget()
        self.engines = EnginesWidget()
        self.memory = MemoryWidget()
        self.integrations = IntegrationsWidget()

    def compose(self) -> ComposeResult:
        yield self.system_stats
        yield self.audio_status
        yield self.engines
        yield self.memory
        yield self.integrations

    def update_stats(self, cpu, ram, uptime):
        self.system_stats.cpu = cpu
        self.system_stats.ram = ram
        self.system_stats.uptime = uptime

    def set_mic_status(self, active: bool):
        self.audio_status.mic_status = active

    def set_tts_engine(self, name: str):
        self.engines.tts_engine = name

    def set_ai_engine(self, name: str):
        self.engines.ai_engine = name

    def update_memory_info(self, memory_entries, corrections):
        self.memory.memory_entries = memory_entries
        self.memory.corrections = corrections

    def set_integrations(self, integrations: str):
        self.integrations.integrations = integrations

class JarvisApp(App):
    CSS = """
    #main-container {
        height: 1fr;
        width: 100%;
    }
    #chatlog {
        width: 70%;
        height: 1fr;
        overflow-y: auto;
        padding: 1;
        border: round white;
        background: black;
        color: white;
        scrollbar-background: #333;
        scrollbar-color: #666;
    }
    #info-panel {
        width: 30%;
        height: 1fr;
        padding: 1;
        border: round green;
        background: #111;
        color: white;
    }
    #input-bar {
        border: round green;
        height: 3;
        width: 100%;
        background: #222;
        color: white;
    }
    SystemStatsWidget {
        margin: 1;
        padding: 1;
        border: round blue;
        background: #1a1a2e;
        height: auto;
    }
    AudioStatusWidget {
        margin: 1;
        padding: 1;
        border: round purple;
        background: #16213e;
        height: auto;
    }
    EnginesWidget {
        margin: 1;
        padding: 1;
        border: round yellow;
        background: #0f3460;
        height: auto;
    }
    MemoryWidget {
        margin: 1;
        padding: 1;
        border: round orange;
        background: #533483;
        height: auto;
    }
    IntegrationsWidget {
        margin: 1;
        padding: 1;
        border: round cyan;
        background: #2d4a22;
        height: auto;
    }
    """

    BINDINGS = [("ctrl+c", "quit", "Quit")]

    # Definir eventos personalizados
    class MessageEvent(Message):
        def __init__(self, text: str, sender: str = "Jarvis"):
            super().__init__()
            self.text = text
            self.sender = sender

    class MicStatusEvent(Message):
        def __init__(self, active: bool):
            super().__init__()
            self.active = active

    class TTSEngineEvent(Message):
        def __init__(self, name: str):
            super().__init__()
            self.name = name

    class AIEngineEvent(Message):
        def __init__(self, name: str):
            super().__init__()
            self.name = name

    class MemoryInfoEvent(Message):
        def __init__(self, memory_entries: int, corrections: int):
            super().__init__()
            self.memory_entries = memory_entries
            self.corrections = corrections

    class IntegrationsEvent(Message):
        def __init__(self, integrations: str):
            super().__init__()
            self.integrations = integrations

    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        self._is_ready = False
        self.on_user_input_callback = None
        self.chat_log = None

    @property
    def is_ready(self):
        return self._is_ready

    def compose(self) -> ComposeResult:
        self.chat_log = ChatLog(id="chatlog")
        self.input_field = Input(placeholder="Type your message...", id="input-bar")
        self.info_panel = InfoPanel(id="info-panel")

        yield Header()
        yield Container(
            Horizontal(
                self.chat_log,
                self.info_panel,
                id="main-container",
            ),
            self.input_field,
        )
        yield Footer()

    def on_mount(self):
        self.set_interval(1, self.refresh_stats)
        self.chat_log.append_message("🚀 Jarvis listo. Di 'Oye Jarvis' o escribe un comando.", sender="System")
        self.set_focus(self.input_field)
        self._is_ready = True

    def refresh_stats(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        uptime_seconds = int(time.time() - self.start_time)
        uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))

        self.info_panel.update_stats(cpu, ram, uptime_str)

    def on_input_submitted(self, event: Input.Submitted):
        user_msg = event.value.strip()
        if user_msg:
            self.chat_log.append_message(user_msg, sender="User")
            self.input_field.value = ""
            if self.on_user_input_callback:
                threading.Thread(target=self.on_user_input_callback, args=(user_msg,), daemon=True).start()
            else:
                self.chat_log.append_message("⚠️ No handler for input!", sender="System")

    # Manejar eventos personalizados
    def on_message_event(self, event: MessageEvent):
        """Maneja eventos de mensajes desde hilos externos"""
        try:
            if self.chat_log:
                self.chat_log.append_message(event.text, event.sender)
                # Forzar scroll hacia abajo
                self.call_after_refresh(self.chat_log.scroll_end)
        except Exception as e:
            # Fallback si falla
            if hasattr(self, 'chat_log'):
                self.chat_log.append_message(f"Error displaying message: {e}", "Error")

    def on_mic_status_event(self, event: MicStatusEvent):
        self.info_panel.set_mic_status(event.active)

    def on_tts_engine_event(self, event: TTSEngineEvent):
        self.info_panel.set_tts_engine(event.name)

    def on_ai_engine_event(self, event: AIEngineEvent):
        self.info_panel.set_ai_engine(event.name)

    def on_memory_info_event(self, event: MemoryInfoEvent):
        self.info_panel.update_memory_info(event.memory_entries, event.corrections)

    def on_integrations_event(self, event: IntegrationsEvent):
        self.info_panel.set_integrations(event.integrations)

    # Métodos externos (mantenidos para compatibilidad)
    def append_message(self, msg, sender="Jarvis"):
        if self.chat_log:
            self.chat_log.append_message(msg, sender)

    def set_mic_status(self, active: bool):
        self.info_panel.set_mic_status(active)

    def set_tts_engine(self, name: str):
        self.info_panel.set_tts_engine(name)

    def set_ai_engine(self, name: str):
        self.info_panel.set_ai_engine(name)

    def update_memory_info(self, memory_entries, corrections):
        self.info_panel.update_memory_info(memory_entries, corrections)

    def get_user_input(self):
        return None

if __name__ == "__main__":
    JarvisApp().run()