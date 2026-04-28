from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from ui.styles import C

class PhantomSelector(QWidget):
    valueChanged = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,14)
        layout.setSpacing(6)
        
        self.opts = [
            ('ribcage', '⊞', 'Ribcage'),
            ('simple', '◎', 'Cylinder'),
            ('layers', '≡', 'Layers'),
        ]
        self.btns = {}
        self.val = 'ribcage'
        
        for id, icon, label in self.opts:
            btn = QPushButton(f"{icon}\n{label}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=id: self.select(i))
            layout.addWidget(btn)
            self.btns[id] = btn
            
        self.update_btns()
        
    def select(self, i):
        self.val = i
        self.update_btns()
        self.valueChanged.emit(i)
        
    def update_btns(self):
        for id, btn in self.btns.items():
            if id == self.val:
                btn.setStyleSheet(f"""
                    background-color: {C['blue']}20;
                    border: 1px solid {C['blue']};
                    border-radius: 5px;
                    color: {C['blue']};
                    font-size: 10px;
                    
                    padding: 7px 4px;
                """)
            else:
                btn.setStyleSheet(f"""
                    background-color: {C['panel']};
                    border: 1px solid {C['border']};
                    border-radius: 5px;
                    color: {C['dim']};
                    font-size: 10px;
                    
                    padding: 7px 4px;
                """)
