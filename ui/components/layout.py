from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt
from ui.styles import C

class Sec(QWidget):
    def __init__(self, label):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 18)
        layout.setSpacing(12)
        
        header = QHBoxLayout()
        header.setContentsMargins(0,0,0,0)
        header.setSpacing(7)
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"font-size: 9px;  color: {C['muted']}; font-weight: bold; letter-spacing: 1px;")
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {C['border']};")
        line.setFixedHeight(1)
        
        header.addWidget(lbl)
        header.addWidget(line, 1)
        
        layout.addLayout(header)
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(0)
        layout.addLayout(self.content_layout)
        
    def addWidget(self, widget):
        self.content_layout.addWidget(widget)

class PipeStep(QWidget):
    def __init__(self, label):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,7)
        layout.setSpacing(8)
        
        self.icon = QLabel("·")
        self.icon.setFixedSize(16, 16)
        self.icon.setAlignment(Qt.AlignCenter)
        
        self.lbl = QLabel(label)
        self.lbl.setStyleSheet(f"font-size: 11px;")
        
        layout.addWidget(self.icon)
        layout.addWidget(self.lbl)
        
        self.set_state(False, False)
        
    def set_state(self, done, active):
        col = C['green'] if done else (C['blue'] if active else C['muted'])
        text = "✓" if done else ("…" if active else "·")
        
        self.icon.setText(text)
        self.icon.setStyleSheet(f"""
            background-color: {col}22;
            border: 1px solid {col};
            border-radius: 8px;
            color: {col};
            font-size: 9px;
            font-weight: bold;
        """)
        self.lbl.setStyleSheet(f"font-size: 11px; color: {col};")
        
        op = QGraphicsOpacityEffect(self)
        op.setOpacity(1.0 if (done or active) else 0.4)
        self.setGraphicsEffect(op)

class MRow(QWidget):
    def __init__(self, label, val_text="", unit="", good=None):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        self.setObjectName("MRow")
        self.setStyleSheet(f"#MRow {{ border-bottom: 1px solid {C['border']}; }}")
        
        self.lbl = QLabel(label)
        self.lbl.setStyleSheet(f"font-size: 10px; color: {C['dim']};")
        
        self.val_lbl = QLabel()
        self.unit = unit
        layout.addWidget(self.lbl)
        layout.addStretch()
        layout.addWidget(self.val_lbl)
        
        self.set_val(val_text, good)
        
    def set_val(self, val_text, good=None):
        col = C['green'] if good is True else (C['red'] if good is False else C['text'])
        self.val_lbl.setText(f"{val_text} <span style='font-size: 9px; color: {C['muted']}'>{self.unit}</span>")
        self.val_lbl.setStyleSheet(f"font-size: 11px;  color: {col}; font-weight: bold;")
