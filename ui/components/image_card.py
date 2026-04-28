from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from ui.styles import C, CMAP_SETS
from ui.colormap import apply_colormap

class ImageCard(QFrame):
    def __init__(self, label, cmap_group, tag=None, tag_color=None, empty_msg="Not computed"):
        super().__init__()
        self.data = None
        self.cmap_group = cmap_group
        self.cmap = CMAP_SETS[cmap_group]['default']
        self.empty_msg = empty_msg
        self._current_rgb = None
        
        self.setObjectName("ImageCard")
        self.setStyleSheet(f"""
            #ImageCard {{
                background-color: {C['card']};
                border: 1px solid {C['border']};
                border-radius: 6px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = QWidget()
        header.setStyleSheet(f"background-color: #0e1828; border-bottom: 1px solid {C['border']}; border-top-left-radius: 6px; border-top-right-radius: 6px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 5, 8, 5)
        header_layout.setSpacing(6)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {C['dim']}; font-size: 10px;  letter-spacing: 1px;")
        header_layout.addWidget(lbl, 1)
        
        if tag:
            tag_lbl = QLabel(tag)
            tc = tag_color or C['blue']
            tag_lbl.setStyleSheet(f"""
                color: {tc};
                background-color: {tc}18;
                border: 1px solid {tc}30;
                border-radius: 3px;
                padding: 1px 5px;
                font-size: 9px;
            """)
            header_layout.addWidget(tag_lbl)
            self.tag_lbl = tag_lbl
        else:
            self.tag_lbl = None
            
        layout.addWidget(header)
        
        cmap_bar = QWidget()
        cmap_bar.setStyleSheet(f"background-color: #0c1520; border-bottom: 1px solid {C['border']};")
        cmap_layout = QHBoxLayout(cmap_bar)
        cmap_layout.setContentsMargins(6, 3, 6, 3)
        cmap_layout.setSpacing(2)
        cmap_layout.setAlignment(Qt.AlignLeft)
        
        self.cmap_btns = []
        for opt in CMAP_SETS[cmap_group]['options']:
            btn = QPushButton(opt)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, o=opt: self.set_cmap(o))
            self.cmap_btns.append(btn)
            cmap_layout.addWidget(btn)
            
        layout.addWidget(cmap_bar)
        
        self.canvas_container = QWidget()
        canvas_layout = QVBoxLayout(self.canvas_container)
        canvas_layout.setContentsMargins(8, 8, 8, 8)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(128, 128)
        canvas_layout.addWidget(self.image_label)
        
        self.empty_label = QLabel(f"<div style='text-align: center; color: {C['muted']};'><div style='font-size: 22px; margin-bottom: 6px;'>◻</div><div style='font-size: 9px; '>{empty_msg}</div></div>")
        self.empty_label.setAlignment(Qt.AlignCenter)
        canvas_layout.addWidget(self.empty_label)
        
        layout.addWidget(self.canvas_container, 1)
        
        self.update_cmap_btns()
        self.update_image()
        
    def set_cmap(self, cmap):
        self.cmap = cmap
        self.update_cmap_btns()
        self.update_image()
        
    def update_cmap_btns(self):
        for btn in self.cmap_btns:
            opt = btn.text()
            if opt == self.cmap:
                btn.setStyleSheet(f"""
                    background-color: {C['blue']}18;
                    border: 1px solid {C['blue']}44;
                    color: {C['blue']};
                    padding: 2px 6px; border-radius: 3px; font-size: 9px; 
                """)
            else:
                btn.setStyleSheet(f"""
                    background-color: transparent;
                    border: 1px solid transparent;
                    color: {C['muted']};
                    padding: 2px 6px; border-radius: 3px; font-size: 9px; 
                """)
                
    def set_data(self, data):
        self.data = data
        self.cmap = CMAP_SETS[self.cmap_group]['default']
        self.update_cmap_btns()
        self.update_image()
        
    def set_tag(self, text):
        if self.tag_lbl:
            self.tag_lbl.setText(text)
            
    def update_image(self):
        if self.data is None:
            self.image_label.hide()
            self.empty_label.show()
        else:
            self.empty_label.hide()
            self.image_label.show()
            
            self._current_rgb = apply_colormap(self.data, self.cmap)
            h, w, c = self._current_rgb.shape
            qimg = QImage(self._current_rgb.data, w, h, 3 * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image()
