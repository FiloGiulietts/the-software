from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import re

class PlantUMLHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.rules = []

        # ========================
        # Formati base
        # ========================
        def fmt(color, bold=False, italic=False):
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if bold:
                f.setFontWeight(QFont.Weight.Bold)
            if italic:
                f.setFontItalic(True)
            return f

        # Colori
        self.keyword_format = fmt("#569CD6", bold=True)
        self.comment_format = fmt("#6A9955", italic=True)
        self.string_format = fmt("#CE9178")
        self.arrow_format = fmt("#DCDCAA")
        self.class_format = fmt("#4EC9B0", bold=True)
        self.method_format = fmt("#9CDCFE")
        self.attribute_format = fmt("#B5CEA8")
        self.note_format = fmt("#C586C0", italic=True)
        self.package_format = fmt("#D7BA7D", bold=True)

        # ========================
        # Regole regex
        # ========================
        self.rules += [
            # Parole chiave principali
            (re.compile(r"\b(@startuml|@enduml|class|interface|enum|abstract|package|note|skinparam)\b"), self.keyword_format),
            # Commenti
            (re.compile(r"//.*|'.*"), self.comment_format),
            # Stringhe tra ""
            (re.compile(r'"[^"]*"'), self.string_format),
            # Relazioni
            (re.compile(r"(-->|--\||\.\.>|<-+|<\|--|<\.\.|->|<->)"), self.arrow_format),
            # Classi e interfacce (nome subito dopo class|interface)
            (re.compile(r"\b(class|interface|enum|abstract)\s+(\w+)"), self.class_format),
            # Metodi e attributi dentro {}
            (re.compile(r"(\w+)\s*:\s*[\w<>]+"), self.attribute_format),
            (re.compile(r"(\w+)\s*\(.*\)"), self.method_format),
            # Note
            (re.compile(r"note\s+(left|right|top|bottom)?\s*:.*"), self.note_format),
            # Package
            (re.compile(r"\bpackage\s+(\w+)\b"), self.package_format),
        ]

    # ========================
    # Evidenziazione
    # ========================
    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)
