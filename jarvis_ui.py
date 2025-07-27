from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input
from textual.containers import Container, Horizontal
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
        else:
            prefix = f"[bold]{sender}:[/bold] "

        self.log_content += f"{prefix}{msg}\n\n"
        self.update(self.log_content)
        
        # Auto-scroll hacia abajo
        if self.auto_scroll:
            self.scroll_end(animate=False)

class InfoPanel(Static):
    cpu = reactive(0.0)
    ram = reactive(0.0)
    tts_engine = reactive("Local")
    ai_engine = reactive("Local")
    memory_entries = reactive(0)
    corrections = reactive(0)
    mic_status = reactive(False)
    uptime = reactive("0s")
    integrations = reactive("")

    def render_info(self):
        mic_icon = "🎙️ ON" if self.mic_status else "🎙️ OFF"
        integrations_display = self.integrations if self.integrations else "Ninguna"
        return (
            f"[bold]Jarvis Stats[/bold]\n"
            f"CPU: {self.cpu:.1f}%\n"
            f"RAM: {self.ram:.1f}%\n"
            f"TTS: {self.tts_engine}\n"
            f"AI: {self.ai_engine}\n"
            f"Memory: {self.memory_entries}\n"
            f"Corrections: {self.corrections}\n"
            f"Uptime: {self.uptime}\n"
            f"{mic_icon}\n\n"
            f"[bold]Integraciones:[/bold]\n{integrations_display}\n"
        )

    def update_info(self):
        self.update(self.render_info())

    def watch_cpu(self, cpu): self.update_info()
    def watch_ram(self, ram): self.update_info()
    def watch_mic_status(self, mic_status): self.update_info()
    def watch_uptime(self, uptime): self.update_info()
    def watch_tts_engine(self, tts_engine): self.update_info()
    def watch_ai_engine(self, ai_engine): self.update_info()
    def watch_memory_entries(self, memory_entries): self.update_info()
    def watch_corrections(self, corrections): self.update_info()
    def watch_integrations(self, integrations): self.update_info()

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
        self.chat_log.append_message("Jarvis ready. Say 'Oye Jarvis' or type a command.", sender="System")
        self.set_focus(self.input_field)
        self._is_ready = True

    def on_integrations_event(self, event: IntegrationsEvent):
        self.info_panel.integrations = event.integrations


    def refresh_stats(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        uptime_seconds = int(time.time() - self.start_time)
        uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))

        self.info_panel.cpu = cpu
        self.info_panel.ram = ram
        self.info_panel.uptime = uptime_str

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
                # Forzar actualización de pantalla
                self.refresh()
        except Exception as e:
            # Fallback si falla
            if hasattr(self, 'chat_log'):
                self.chat_log.append_message(f"Error displaying message: {e}", "Error")

    def on_mic_status_event(self, event: MicStatusEvent):
        self.info_panel.mic_status = event.active

    def on_tts_engine_event(self, event: TTSEngineEvent):
        self.info_panel.tts_engine = event.name

    def on_ai_engine_event(self, event: AIEngineEvent):
        self.info_panel.ai_engine = event.name

    def on_memory_info_event(self, event: MemoryInfoEvent):
        self.info_panel.memory_entries = event.memory_entries
        self.info_panel.corrections = event.corrections

    # Métodos externos (mantenidos para compatibilidad)
    def append_message(self, msg, sender="Jarvis"):
        if self.chat_log:
            self.chat_log.append_message(msg, sender)

    def set_mic_status(self, active: bool):
        self.info_panel.mic_status = active

    def set_tts_engine(self, name: str):
        self.info_panel.tts_engine = name

    def set_ai_engine(self, name: str):
        self.info_panel.ai_engine = name

    def update_memory_info(self, memory_entries, corrections):
        self.info_panel.memory_entries = memory_entries
        self.info_panel.corrections = corrections

    def get_user_input(self):
        return None

if __name__ == "__main__":
    JarvisApp().run()