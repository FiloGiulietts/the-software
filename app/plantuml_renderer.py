from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, QTimer
import subprocess
from pathlib import Path
import os
import shutil
import re

class PlantUMLRendererWorkerSignals(QObject):
    finished = pyqtSignal(str)   # percorso immagine generato
    error = pyqtSignal(str, int) # messaggio, linea errore

class PlantUMLRendererWorker(QRunnable):
    ERROR_LINE_RE = re.compile(r"line\s+(\d+)", re.IGNORECASE)

    def __init__(self, jar_path: str, text: str):
        super().__init__()
        self.jar_path = os.path.abspath(jar_path)
        self.text = text
        self.signals = PlantUMLRendererWorkerSignals()
        self.java_cmd = shutil.which("java")
        self.cache_dir = Path.home() / ".cache" / "plantuml-editor"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        src = self.cache_dir / "diagram.puml"
        out = self.cache_dir / "diagram.png"
        src.write_text(self.text, encoding="utf-8")

        cmd = [self.java_cmd, "-jar", self.jar_path, str(src)]
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0 or not out.exists():
                err_msg = result.stderr.strip() or "Errore PlantUML"
                line = None
                match = self.ERROR_LINE_RE.search(err_msg)
                if match:
                    line = int(match.group(1))
                self.signals.error.emit(err_msg, line)
                return

            self.signals.finished.emit(str(out))

        except Exception as e:
            self.signals.error.emit(str(e), None)


class AsyncPlantUMLPreview:
    """Gestisce render asincrono e debounce per live preview"""
    def __init__(self, jar_path: str, preview_widget, editor_widget=None, debounce_ms=500):
        self.jar_path = jar_path
        self.preview_widget = preview_widget
        self.editor_widget = editor_widget
        self.threadpool = QThreadPool()
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._render_now)
        self.last_text = ""

        self.debounce_ms = debounce_ms

    def render(self, text: str):
        self.last_text = text
        self.debounce_timer.start(self.debounce_ms)

    def _render_now(self):
        worker = PlantUMLRendererWorker(self.jar_path, self.last_text)
        worker.signals.finished.connect(self.preview_widget.update_image)
        if self.editor_widget:
            worker.signals.error.connect(
                lambda msg, line: self.editor_widget.highlight_error_line(line) if line else None
            )
        self.threadpool.start(worker)
