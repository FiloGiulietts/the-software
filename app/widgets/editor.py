from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget
from PyQt6.QtGui import QTextCursor, QColor, QFont, QPainter
from PyQt6.QtCore import Qt


class LineNumberArea(QWidget):
    """Widget laterale per i numeri di riga"""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return self.editor.line_number_area_width(), 0

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class EditorWidget(QPlainTextEdit):
    def __init__(self):
        super().__init__()

        self.current_file = None
        self.error_selection = None

        # =========================
        # FONT E STILE
        # =========================
        font = QFont("Fira Code")
        font.setPointSize(12)
        self.setFont(font)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                selection-background-color: #264f78;
            }
        """)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))

        # =========================
        # HIGHIGHTER PLANTUML PRIMA DI TUTTO
        # =========================
        from app.highlighter.plantuml_highlighter import PlantUMLHighlighter
        self.highlighter = PlantUMLHighlighter(self.document())

        # =========================
        # LINE NUMBER AREA DOPO HIGHIGHTER
        # =========================
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    # =========================
    # LINE NUMBERS
    # =========================
    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(0, cr.y(), self.line_number_area_width(), cr.height())

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2e2e2e"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        current_line = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                color = QColor("#ffffff") if block_number == current_line else QColor("#888888")
                painter.setPen(color)
                painter.drawText(0, int(top), self.line_number_area.width() - 2,
                                 int(self.fontMetrics().height()), Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    # =========================
    # LINEA CORRENTE
    # =========================
    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor("#2a2a2a"))  # linea corrente leggermente più chiara
            selection.cursor = self.textCursor()
            extra_selections.append(selection)

        if self.error_selection:
            extra_selections.append(self.error_selection)

        self.setExtraSelections(extra_selections)

    # =========================
    # FILE HANDLING
    # =========================
    def load_file(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print("Errore leggendo file:", e)
            text = ""
        self.setPlainText(text)
        self.current_file = path
        self.moveCursor(QTextCursor.MoveOperation.Start)

    def save(self):
        if not self.current_file:
            return
        with open(self.current_file, "w", encoding="utf-8") as f:
            f.write(self.toPlainText())

    # =========================
    # EVIDENZIAZIONE ERRORI
    # =========================
    def highlight_error_line(self, line: int):
        self.clear_error_highlight()
        cursor = QTextCursor(self.document())
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, line - 1)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)

        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor
        selection.format.setBackground(QColor("#ff5555"))

        self.error_selection = selection
        self.highlight_current_line()

    def clear_error_highlight(self):
        self.error_selection = None
        self.highlight_current_line()
