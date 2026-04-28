import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import physics

C = {
    'bg': '#0c1018', 'panel': '#101724', 'card': '#141f30',
    'border': '#1e2d44', 'border2': '#253550',
    'muted': '#3a5070', 'dim': '#6a7e9a', 'text': '#c8d8ee', 'textBr': '#e4eef8',
    'blue': '#4da8da', 'green': '#2dd4a0', 'orange': '#e8a95c', 'red': '#e87060', 'purple': '#b48af5',
}

CMAP_SETS = {
    'bone': {'default': 'bone', 'options': ['bone', 'gray', 'hot', 'viridis']},
    'tissue': {'default': 'tissue', 'options': ['tissue', 'gray', 'hot', 'viridis']},
    'xray': {'default': 'xray', 'options': ['xray', 'gray', 'hot', 'viridis']},
}

class ImageCard(QFrame):
    def __init__(self, label, cmap_group, tag=None, tag_color=None, empty_msg="Not computed"):
        super().__init__()
        self.data = None
        self.cmap_group = cmap_group
        self.cmap = CMAP_SETS[cmap_group]['default']
        self.empty_msg = empty_msg
        
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
        lbl.setStyleSheet(f"color: {C['dim']}; font-size: 10px; font-family: 'Courier New', monospace; letter-spacing: 1px;")
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
                font-family: 'Courier New', monospace;
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
        
        self.empty_label = QLabel(f"<div style='text-align: center; color: {C['muted']};'><div style='font-size: 22px; margin-bottom: 6px;'>◻</div><div style='font-size: 9px; font-family: 'Courier New', monospace;'>{empty_msg}</div></div>")
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
                    padding: 2px 6px; border-radius: 3px; font-size: 9px; font-family: 'Courier New', monospace;
                """)
            else:
                btn.setStyleSheet(f"""
                    background-color: transparent;
                    border: 1px solid transparent;
                    color: {C['muted']};
                    padding: 2px 6px; border-radius: 3px; font-size: 9px; font-family: 'Courier New', monospace;
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
            
            self._current_rgb = physics.apply_colormap(self.data, self.cmap)
            h, w, c = self._current_rgb.shape
            qimg = QImage(self._current_rgb.data, w, h, 3 * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.FastTransformation
            )
            self.image_label.setPixmap(pixmap)
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image()

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
        self.val_lbl.setStyleSheet(f"font-size: 11px; font-family: 'Courier New', monospace; color: {self.color}; font-weight: bold;")
        
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
        self.valueChanged.emit(self.val)

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
        lbl.setStyleSheet(f"font-size: 9px; font-family: 'Courier New', monospace; color: {C['muted']}; font-weight: bold; letter-spacing: 1px;")
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
        self.val_lbl.setStyleSheet(f"font-size: 11px; font-family: 'Courier New', monospace; color: {col}; font-weight: bold;")

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
                    font-family: 'Courier New', monospace;
                    padding: 7px 4px;
                """)
            else:
                btn.setStyleSheet(f"""
                    background-color: {C['panel']};
                    border: 1px solid {C['border']};
                    border-radius: 5px;
                    color: {C['dim']};
                    font-size: 10px;
                    font-family: 'Courier New', monospace;
                    padding: 7px 4px;
                """)

class AttenChart(FigureCanvasQTAgg):
    def __init__(self):
        fig = Figure(figsize=(2.3, 0.9), facecolor='none')
        super().__init__(fig)
        self.ax = fig.add_axes([0, 0, 1, 1])
        self.ax.axis('off')
        
        self.eL = 40
        self.eH = 100
        self.draw_chart()
        self.setStyleSheet("background: transparent;")
        
    def update_energies(self, eL, eH):
        self.eL = eL
        self.eH = eH
        self.draw_chart()
        
    def draw_chart(self):
        self.ax.clear()
        self.ax.axis('off')
        self.ax.set_xlim(-6, 224)
        self.ax.set_ylim(-14, 90)
        self.ax.invert_yaxis()
        
        energies = np.array([20, 40, 60, 80, 100, 120, 140])
        max_mu = physics.mu(20, 'bone')
        
        mu_b = np.array([physics.mu(e, 'bone') for e in energies])
        x = ((energies - 20) / 120) * 210
        y_b = 68 - (mu_b / max_mu) * 64
        self.ax.plot(x, y_b, color=C['orange'], linewidth=1.8)
        
        mu_t = np.array([physics.mu(e, 'tissue') for e in energies])
        y_t = 68 - (mu_t / max_mu) * 64
        self.ax.plot(x, y_t, color=C['blue'], linewidth=1.8)
        
        for idx, e in enumerate([self.eL, self.eH]):
            mx = ((e - 20) / 120) * 210
            col = C['red'] if idx == 0 else C['green']
            self.ax.plot([mx, mx], [-10, 70], color=col, linewidth=1, linestyle='--', alpha=0.65)
            self.ax.text(mx, -6, str(int(e)), color=col, fontsize=7, ha='center', va='bottom', fontfamily='Courier New')
            
        self.ax.plot(5, 3, marker='o', markersize=3, color=C['orange'])
        self.ax.text(11, 5, 'Bone', color=C['dim'], fontsize=7, va='center', fontfamily='Courier New')
        self.ax.plot(48, 3, marker='o', markersize=3, color=C['blue'])
        self.ax.text(54, 5, 'Tissue', color=C['dim'], fontsize=7, va='center', fontfamily='Courier New')
        
        self.ax.text(0, 74, '20', color=C['muted'], fontsize=7, ha='left', va='top', fontfamily='Courier New')
        self.ax.text(207, 74, '140 keV', color=C['muted'], fontsize=7, ha='right', va='top', fontfamily='Courier New')
        
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BoneVision DX-Ray")
        self.resize(1100, 700)
        self.setStyleSheet(f"background-color: {C['bg']}; color: {C['text']}; font-family: Arial, Helvetica, sans-serif;")
        
        self.pType = 'ribcage'
        self.eL = 40.0
        self.eH = 100.0
        self.noise = 0.025
        self.scatter = 0.012
        
        self.phantom = None
        self.projL = None
        self.projH = None
        self.boneMap = None
        self.tissueMap = None
        self.metrics = None
        self.dinfo = None
        
        self.step = 0
        self.running = False
        self.log = []
        
        self.init_ui()
        self.on_phantom_change(self.pType)
        

        
    def add_log(self, msg):
        self.log.append(msg)
        if len(self.log) > 8:
            self.log = self.log[-8:]
            
        html = ""
        for l in self.log:
            col = f"{C['blue']}bb" if l.startswith('[SIM]') else (
                  f"{C['green']}bb" if l.startswith('[DEC]') else (
                  f"{C['orange']}99" if l.startswith('[RST]') else '#3a5575'))
            html += f"<div style='color: {col}; line-height: 1.5;'>{l}</div>"
        self.log_widget.setHtml(html)
        self.log_widget.verticalScrollBar().setValue(self.log_widget.verticalScrollBar().maximum())
        
    def init_ui(self):
        cen = QWidget()
        self.setCentralWidget(cen)
        main_layout = QVBoxLayout(cen)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        
        header = QWidget()
        header.setFixedHeight(46)
        header.setStyleSheet(f"background-color: {C['panel']}; border-bottom: 1px solid {C['border']};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(18,0,18,0)
        
        logo_lay = QHBoxLayout()
        d1 = QLabel("●")
        d1.setStyleSheet(f"color: {C['blue']}; font-size: 14px;")
        d2 = QLabel("●")
        d2.setStyleSheet(f"color: {C['orange']}; font-size: 14px;")
        title = QLabel("BoneVision <span style='color:"+C['blue']+"'>DX-Ray</span>")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        sub = QLabel("Dual-Energy X-Ray Material Decomposition")
        sub.setStyleSheet(f"font-size: 9px; color: {C['muted']}; font-family: 'Courier New', monospace; border-left: 1px solid {C['border']}; padding-left: 12px;")
        
        logo_lay.addWidget(d1)
        logo_lay.addWidget(d2)
        logo_lay.addWidget(title)
        logo_lay.addWidget(sub)
        
        self.status_e_sep = QLabel()
        self.status_lbl = QLabel()
        
        stat_lay = QHBoxLayout()
        stat_lay.setSpacing(20)
        stat_lay.addWidget(self.status_e_sep)
        stat_lay.addWidget(self.status_lbl)
        
        exit_btn = QPushButton("✕")
        exit_btn.setFixedSize(28, 28)
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.setStyleSheet(f"""
            QPushButton {{ border: 1px solid {C['border2']}; border-radius: 5px; background: transparent; color: {C['dim']}; }}
            QPushButton:hover {{ background: {C['red']}22; border-color: {C['red']}; color: {C['red']}; }}
        """)
        exit_btn.clicked.connect(self.close)
        
        h_layout.addLayout(logo_lay)
        h_layout.addStretch()
        h_layout.addLayout(stat_lay)
        h_layout.addSpacing(20)
        h_layout.addWidget(exit_btn)
        
        main_layout.addWidget(header)
        
        body = QWidget()
        b_layout = QHBoxLayout(body)
        b_layout.setContentsMargins(0,0,0,0)
        b_layout.setSpacing(0)
        
        left = QWidget()
        left.setFixedWidth(238)
        left.setStyleSheet(f"background-color: {C['panel']}; border-right: 1px solid {C['border']};")
        l_layout = QVBoxLayout(left)
        l_layout.setContentsMargins(14,14,14,14)
        
        s1 = Sec("Phantom")
        self.p_sel = PhantomSelector()
        self.p_sel.valueChanged.connect(self.on_phantom_change)
        s1.addWidget(self.p_sel)
        l_layout.addWidget(s1)
        
        s2 = Sec("Acquisition")
        self.k_el = Knob("Low Energy E_L", self.eL, 20, 90, 1, " keV", C['red'])
        self.k_eh = Knob("High Energy E_H", self.eH, 25, 150, 1, " keV", C['green'])
        
        self.k_el.valueChanged.connect(self.on_el_change)
        self.k_eh.valueChanged.connect(self.on_eh_change)
        s2.addWidget(self.k_el)
        s2.addWidget(self.k_eh)
        l_layout.addWidget(s2)
        
        s3 = Sec("Realism")
        self.k_noise = Knob("Noise  σ", self.noise, 0, 0.2, 0.005, "", C['purple'])
        self.k_scatter = Knob("Scatter  β", self.scatter, 0, 0.15, 0.005, "", C['orange'])
        self.k_noise.valueChanged.connect(lambda v: setattr(self, 'noise', v))
        self.k_scatter.valueChanged.connect(lambda v: setattr(self, 'scatter', v))
        s3.addWidget(self.k_noise)
        s3.addWidget(self.k_scatter)
        l_layout.addWidget(s3)
        
        s4 = Sec("Actions")
        s4.content_layout.setSpacing(7)
        self.btn_sim = QPushButton("▶  Run Acquisition")
        self.btn_dec = QPushButton("◈  Decompose Materials")
        self.btn_rst = QPushButton("↺  Reset Pipeline")
        
        self.btn_sim.setMinimumHeight(34)
        self.btn_dec.setMinimumHeight(34)
        self.btn_rst.setMinimumHeight(34)
        
        self.btn_rst.setStyleSheet(f"padding: 7px 12px; margin: 2px 0; border-radius: 5px; border: 1px solid {C['border2']}; background: transparent; color: {C['muted']}; text-align: left;")
        
        self.btn_sim.setCursor(Qt.PointingHandCursor)
        self.btn_dec.setCursor(Qt.PointingHandCursor)
        self.btn_rst.setCursor(Qt.PointingHandCursor)
        
        self.btn_sim.clicked.connect(self.run_sim)
        self.btn_dec.clicked.connect(self.run_dec)
        self.btn_rst.clicked.connect(self.reset_pipeline_action)
        
        s4.addWidget(self.btn_sim)
        s4.addWidget(self.btn_dec)
        s4.addWidget(self.btn_rst)
        l_layout.addWidget(s4)
        
        l_layout.addStretch()
        
        log_lbl = QLabel("OUTPUT LOG")
        log_lbl.setStyleSheet(f"font-size: 9px; color: {C['muted']}; font-family: 'Courier New', monospace; letter-spacing: 1px; margin-bottom: 5px;")
        l_layout.addWidget(log_lbl)
        
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setFixedHeight(100)
        self.log_widget.setStyleSheet(f"background-color: #080e16; border: 1px solid {C['border']}; border-radius: 4px; padding: 4px; font-size: 9px; font-family: 'Courier New', monospace;")
        l_layout.addWidget(self.log_widget)
        
        b_layout.addWidget(left)
        
        center = QWidget()
        center.setStyleSheet("background-color: #0b1320;")
        c_layout = QGridLayout(center)
        c_layout.setContentsMargins(12,12,12,12)
        c_layout.setSpacing(10)
        
        self.ic_b_gt = ImageCard("Ground Truth — Bone", "bone", "PHANTOM", C['orange'])
        self.ic_t_gt = ImageCard("Ground Truth — Soft Tissue", "tissue", "PHANTOM", C['blue'])
        self.ic_p_l = ImageCard("Low-Energy Projection", "xray", f"{int(self.eL)} keV", C['red'], "Run Acquisition first")
        self.ic_p_h = ImageCard("High-Energy Projection", "xray", f"{int(self.eH)} keV", C['green'], "Run Acquisition first")
        self.ic_b_map = ImageCard("Decomposed — Bone Map", "bone", "RECONSTRUCTED", C['orange'], "Run Decomposition first")
        self.ic_t_map = ImageCard("Decomposed — Soft Tissue Map", "tissue", "RECONSTRUCTED", C['blue'], "Run Decomposition first")
        
        c_layout.addWidget(self.ic_b_gt, 0, 0)
        c_layout.addWidget(self.ic_p_l, 0, 1)
        c_layout.addWidget(self.ic_b_map, 0, 2)
        c_layout.addWidget(self.ic_t_gt, 1, 0)
        c_layout.addWidget(self.ic_p_h, 1, 1)
        c_layout.addWidget(self.ic_t_map, 1, 2)
        
        b_layout.addWidget(center, 1)
        
        right = QWidget()
        right.setFixedWidth(242)
        right.setStyleSheet(f"background-color: {C['panel']}; border-left: 1px solid {C['border']};")
        
        r_layout = QVBoxLayout(right)
        r_layout.setContentsMargins(14,14,14,14)
        
        s5 = Sec("Pipeline")
        self.ps_p = PipeStep("Phantom loaded")
        self.ps_al = PipeStep("Low-E acquisition")
        self.ps_ah = PipeStep("High-E acquisition")
        self.ps_md = PipeStep("Material decomposition")
        self.ps_mc = PipeStep("Metrics computed")
        for ps in [self.ps_p, self.ps_al, self.ps_ah, self.ps_md, self.ps_mc]:
            s5.addWidget(ps)
        r_layout.addWidget(s5)
        
        s6 = Sec("System Parameters")
        self.mr_el = MRow("E_L (low)", unit="keV")
        self.mr_eh = MRow("E_H (high)", unit="keV")
        self.mr_esep = MRow("ΔE separation", unit="keV")
        self.mr_ns = MRow("Noise  σ")
        self.mr_sc = MRow("Scatter  β")
        self.mr_mubl = MRow("μ_bone @ E_L", unit="cm⁻¹")
        self.mr_mubh = MRow("μ_bone @ E_H", unit="cm⁻¹")
        self.mr_det = MRow("det(A)")
        
        for mr in [self.mr_el, self.mr_eh, self.mr_esep, self.mr_ns, self.mr_sc, self.mr_mubl, self.mr_mubh, self.mr_det]:
            s6.addWidget(mr)
        
        self.mr_mubl.hide()
        self.mr_mubh.hide()
        self.mr_det.hide()
        r_layout.addWidget(s6)
        
        s7 = Sec("Quality Metrics")
        self.qm_empty = QLabel("Run decomposition\nto compute metrics.")
        self.qm_empty.setStyleSheet(f"font-size: 10px; color: {C['muted']}; font-family: 'Courier New', monospace; line-height: 1.7;")
        s7.addWidget(self.qm_empty)
        
        self.mr_mb = MRow("MAE — bone", unit="cm")
        self.mr_mt = MRow("MAE — tissue", unit="cm")
        self.mr_cnr = MRow("CNR bone/bg")
        self.mr_snr = MRow("SNR proj-L")
        for mr in [self.mr_mb, self.mr_mt, self.mr_cnr, self.mr_snr]:
            s7.addWidget(mr)
            mr.hide()
        r_layout.addWidget(s7)
        
        s8 = Sec("Attenuation Model")
        lbl = QLabel("μ(E) CURVES — BONE / TISSUE")
        lbl.setStyleSheet(f"font-size: 9px; color: {C['muted']}; font-family: 'Courier New', monospace; letter-spacing: 1px; margin-bottom: 8px;")
        s8.addWidget(lbl)
        
        self.chart = AttenChart()
        self.chart.setFixedHeight(120)
        s8.addWidget(self.chart)
        r_layout.addWidget(s8)
        
        r_layout.addStretch()
        b_layout.addWidget(right)
        
        main_layout.addWidget(body, 1)
        
        self.add_log("System ready.")
        self.update_status()
        
    def on_phantom_change(self, v):
        self.pType = v
        self.phantom = physics.generate_phantom(v)
        self.ic_b_gt.set_data(self.phantom['bone'])
        self.ic_t_gt.set_data(self.phantom['tissue'])
        self.reset_pipeline(silent=True)
        self.add_log(f"[+] Phantom loaded: {v}")
        self.update_status()
        
    def on_el_change(self, v):
        self.eL = v
        if self.eL >= self.eH:
            self.k_eh.set_value(min(150, self.eL + 5))
        self.update_status()
        
    def on_eh_change(self, v):
        self.eH = v
        if self.eH <= self.eL:
            self.k_el.set_value(max(20, self.eH - 5))
        self.update_status()
        
    def update_status(self):
        eSep = self.eH - self.eL
        eSepGood = True if eSep >= 45 else (None if eSep >= 25 else False)
        col = C['green'] if eSepGood is True else (C['red'] if eSepGood is False else C['orange'])
        
        self.status_e_sep.setText(f"<span style='font-size: 10px; color: {C['muted']}; font-family: 'Courier New', monospace;'>ΔE: <span style='color: {col}; font-weight: bold;'>{int(eSep)} keV</span></span>")
        
        s_text = 'COMPUTING' if self.running else ('COMPLETE' if self.step == 2 else ('SIM DONE — DECOMPOSE?' if self.step == 1 else 'READY'))
        s_col = C['orange'] if self.running else (C['green'] if self.step == 2 else (C['blue'] if self.step == 1 else C['dim']))
        self.status_lbl.setText(f"<span style='font-size: 10px; color: {C['muted']}; font-family: 'Courier New', monospace;'>STATUS: <span style='color: {s_col}; font-weight: bold;'>{s_text}</span></span>")
        
        self.mr_el.set_val(int(self.eL))
        self.mr_eh.set_val(int(self.eH))
        self.mr_esep.set_val(int(eSep), eSepGood)
        self.mr_ns.set_val(f"{self.noise:.3f}")
        self.mr_sc.set_val(f"{self.scatter:.3f}")
        
        self.chart.update_energies(self.eL, self.eH)
        self.ic_p_l.set_tag(f"{int(self.eL)} keV")
        self.ic_p_h.set_tag(f"{int(self.eH)} keV")
        
        self.ps_p.set_state(self.phantom is not None, False)
        self.ps_al.set_state(self.step >= 1, self.running and self.step == 0)
        self.ps_ah.set_state(self.step >= 1, self.running and self.step == 0)
        self.ps_md.set_state(self.step >= 2, self.running and self.step == 1)
        self.ps_mc.set_state(self.metrics is not None, False)
        
        self.btn_sim.setDisabled(self.running)
        self.btn_dec.setDisabled(self.projL is None or self.running)
        
        op1 = 0.55 if self.running else 1
        op2 = 0.45 if (self.projL is None or self.running) else 1
        
        self.btn_sim.setStyleSheet(f"padding: 9px 12px; margin: 2px 0; border-radius: 5px; border: 1px solid {C['blue']}; background: rgba(77, 168, 218, {int(0.18 * 255 * op1)}); color: {C['blue']}; text-align: left;")
        self.btn_dec.setStyleSheet(f"padding: 9px 12px; margin: 2px 0; border-radius: 5px; border: 1px solid {C['green']}; background: rgba(45, 212, 160, {int(0.16 * 255 * op2)}); color: rgba(45, 212, 160, {int(255 * op2)}); text-align: left;")
        
    def reset_pipeline_action(self):
        self.reset_pipeline(silent=False)
        
    def reset_pipeline(self, silent=False):
        self.projL = None
        self.projH = None
        self.boneMap = None
        self.tissueMap = None
        self.metrics = None
        self.dinfo = None
        self.step = 0
        
        self.ic_p_l.set_data(None)
        self.ic_p_h.set_data(None)
        self.ic_b_map.set_data(None)
        self.ic_t_map.set_data(None)
        
        self.mr_mubl.hide()
        self.mr_mubh.hide()
        self.mr_det.hide()
        
        self.qm_empty.show()
        for mr in [self.mr_mb, self.mr_mt, self.mr_cnr, self.mr_snr]:
            mr.hide()
            
        if not silent:
            self.add_log("[RST] Pipeline cleared.")
        self.update_status()

    def run_sim(self):
        if self.phantom is None or self.running: return
        self.running = True
        self.update_status()
        QCoreApplication.processEvents()
        
        QTimer.singleShot(50, self._do_sim)
        
    def _do_sim(self):
        self.projL = physics.simulate_projection(self.phantom, self.eL, self.noise, self.scatter)
        self.projH = physics.simulate_projection(self.phantom, self.eH, self.noise, self.scatter)
        
        self.ic_p_l.set_data(self.projL)
        self.ic_p_h.set_data(self.projH)
        
        self.boneMap = None
        self.tissueMap = None
        self.metrics = None
        self.dinfo = None
        self.step = 1
        
        mu_bl = physics.mu(self.eL, 'bone')
        mu_tl = physics.mu(self.eL, 'tissue')
        self.add_log(f"[SIM] E_L={int(self.eL)}keV  μ_b={mu_bl:.3f}  μ_t={mu_tl:.3f}")
        
        mu_bh = physics.mu(self.eH, 'bone')
        mu_th = physics.mu(self.eH, 'tissue')
        self.add_log(f"[SIM] E_H={int(self.eH)}keV  μ_b={mu_bh:.3f}  μ_t={mu_th:.3f}")
        
        self.running = False
        self.update_status()
        
    def run_dec(self):
        if self.projL is None or self.running: return
        self.running = True
        self.update_status()
        QCoreApplication.processEvents()
        
        QTimer.singleShot(50, self._do_dec)
        
    def _do_dec(self):
        self.dinfo = physics.decompose(self.projL, self.projH, self.eL, self.eH)
        self.boneMap = self.dinfo['boneMap']
        self.tissueMap = self.dinfo['tissueMap']
        
        self.ic_b_map.set_data(self.boneMap)
        self.ic_t_map.set_data(self.tissueMap)
        
        self.metrics = physics.compute_metrics(self.boneMap, self.tissueMap, self.phantom, self.projL)
        self.step = 2
        
        self.mr_mubl.set_val(f"{self.dinfo['muBL']:.4f}")
        self.mr_mubl.show()
        self.mr_mubh.set_val(f"{self.dinfo['muBH']:.4f}")
        self.mr_mubh.show()
        self.mr_det.set_val(f"{self.dinfo['det']:.4f}", good=abs(self.dinfo['det']) > 0.06)
        self.mr_det.show()
        
        self.qm_empty.hide()
        
        mb = float(self.metrics['maeBone'])
        self.mr_mb.set_val(self.metrics['maeBone'], good=True if mb<0.05 else (None if mb<0.15 else False))
        self.mr_mb.show()
        
        mt = float(self.metrics['maeTissue'])
        self.mr_mt.set_val(self.metrics['maeTissue'], good=True if mt<0.05 else (None if mt<0.15 else False))
        self.mr_mt.show()
        
        cnr = float(self.metrics['cnr'])
        self.mr_cnr.set_val(self.metrics['cnr'], good=True if cnr>5 else (None if cnr>2 else False))
        self.mr_cnr.show()
        
        snr = float(self.metrics['snr'])
        self.mr_snr.set_val(self.metrics['snr'], good=True if snr>10 else (None if snr>4 else False))
        self.mr_snr.show()
        
        self.add_log(f"[DEC] det(A)={self.dinfo['det']:.4f}  MAE_b={self.metrics['maeBone']}  CNR={self.metrics['cnr']}")
        
        self.running = False
        self.update_status()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec_())
