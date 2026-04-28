from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt, pyqtSignal
from ui.styles import C

class Knob(QWidget):
    valueChanged = pyqtSignal(float)
    def __init__(self, label, val, min_v, max_v, step, unit='', color=None, fmt=None):
        super().__init__()
        self.val = val
        self.min_v = min_v
        self.max_v = max_v
        self.step = step
        self.unit = unit
        self.color = color or C['blue']
        self.fmt = fmt or (lambda x: str(int(x)) if step >= 1 else f"{x:.3f}")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 13)
        layout.setSpacing(8)
        
        header = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 10px; color: {C['dim']};")
        self.val_lbl = QLabel(f"{self.fmt(self.val)}{self.unit}")
        self.val_lbl.setStyleSheet(f"font-size: 11px;  color: {self.color}; font-weight: bold;")
        
        header.addWidget(lbl)
        header.addStretch()
        header.addWidget(self.val_lbl)
        
        self.slider = QSlider(Qt.Horizontal)
        self.factor = 1.0 if step >= 1 else 1000.0
        self.slider.setMinimum(int(min_v * self.factor))
        self.slider.setMaximum(int(max_v * self.factor))
        self.slider.setSingleStep(int(step * self.factor))
        self.slider.setValue(int(val * self.factor))
        
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{ height: 3px; background: {C['border']}; border-radius: 1px; }}
            QSlider::handle:horizontal {{ background: {self.color}; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }}
        """)
        
        self.slider.valueChanged.connect(self.on_val_change)
        
        layout.addLayout(header)
        layout.addWidget(self.slider)
        
    def on_val_change(self, v):
        self.val = v / self.factor
        self.val_lbl.setText(f"{self.fmt(self.val)}{self.unit}")
        self.valueChanged.emit(self.val)
        
    def set_value(self, v):
        self.slider.blockSignals(True)
        self.slider.setValue(int(v * self.factor))
        self.slider.blockSignals(False)
        self.val = v
        self.val_lbl.setText(f"{self.fmt(self.val)}{self.unit}")
