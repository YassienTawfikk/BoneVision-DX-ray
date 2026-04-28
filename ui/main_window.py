from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QGridLayout
from PyQt5.QtCore import Qt
from ui.styles import C
from ui.components.image_card import ImageCard
from ui.components.knob import Knob
from ui.components.layout import Sec, PipeStep, MRow
from ui.components.selectors import PhantomSelector
from ui.components.charts import AttenChart

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BoneVision DX-Ray")
        self.resize(1100, 700)
        self.setStyleSheet(f"background-color: {C['bg']}; color: {C['text']};")
        self.log = []
        self.on_close_callback = None
        self.init_ui()
        
    def add_log(self, msg):
        self.log.append(msg)
        if len(self.log) > 8:
            self.log = self.log[-8:]
            
        html = ""
        for l in self.log:
            col = f"{C['blue']}bb" if l.startswith('[SIM]') else (
                  f"{C['green']}bb" if l.startswith('[DEC]') else (
                  f"{C['orange']}99" if l.startswith('[RST]') else '#3a5575'))
            html += f"<div style='color: {col}; line-height: 1.5; margin-right: 18px; word-wrap: break-word;'>{l}</div>"
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
        sub.setStyleSheet(f"font-size: 9px; color: {C['muted']}; border-left: 1px solid {C['border']}; padding-left: 12px;")
        
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
        
        self.exit_btn = QPushButton("✕")
        self.exit_btn.setFixedSize(28, 28)
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.setStyleSheet(f"""
            QPushButton {{ border: 1px solid {C['border2']}; border-radius: 5px; background: transparent; color: {C['dim']}; }}
            QPushButton:hover {{ background: {C['red']}22; border-color: {C['red']}; color: {C['red']}; }}
        """)
        self.exit_btn.clicked.connect(self.close)
        
        h_layout.addLayout(logo_lay)
        h_layout.addStretch()
        h_layout.addLayout(stat_lay)
        h_layout.addSpacing(20)
        h_layout.addWidget(self.exit_btn)
        
        main_layout.addWidget(header)
        
        body = QWidget()
        b_layout = QHBoxLayout(body)
        b_layout.setContentsMargins(0,0,0,0)
        b_layout.setSpacing(0)
        
        left = QWidget()
        left.setObjectName("LeftPanel")
        left.setFixedWidth(238)
        left.setStyleSheet(f"#LeftPanel {{ background-color: {C['panel']}; border-right: 1px solid {C['border']}; }}")
        l_layout = QVBoxLayout(left)
        l_layout.setContentsMargins(14,14,14,14)
        
        s1 = Sec("Phantom")
        self.p_sel = PhantomSelector()
        s1.addWidget(self.p_sel)
        l_layout.addWidget(s1)
        
        s2 = Sec("Acquisition")
        self.k_el = Knob("Low Energy", 40.0, 20, 90, 1, " keV", C['red'])
        self.k_eh = Knob("High Energy", 100.0, 25, 140, 1, " keV", C['green'])
        
        s2.addWidget(self.k_el)
        s2.addWidget(self.k_eh)
        l_layout.addWidget(s2)
        
        s3 = Sec("Realism")
        self.k_noise = Knob("Noise Level (σ)", 0.025, 0, 0.2, 0.005, "", C['purple'])
        self.k_scatter = Knob("Scatter Level (β)", 0.012, 0, 0.15, 0.005, "", C['orange'])
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
        
        s4.addWidget(self.btn_sim)
        s4.addWidget(self.btn_dec)
        s4.addWidget(self.btn_rst)
        l_layout.addWidget(s4)
        
        l_layout.addStretch()
        
        log_lbl = QLabel("OUTPUT LOG")
        log_lbl.setStyleSheet(f"font-size: 9px; color: {C['muted']};  letter-spacing: 1px; margin-bottom: 5px;")
        l_layout.addWidget(log_lbl)
        
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setFixedHeight(100)
        self.log_widget.setStyleSheet(f"background-color: #080e16; border: 1px solid {C['border']}; border-radius: 4px; padding: 4px; padding-right: 14px; font-size: 9px; font-family: 'Courier New', monospace;")
        l_layout.addWidget(self.log_widget)
        
        b_layout.addWidget(left)
        
        center = QWidget()
        center.setObjectName("CenterPanel")
        center.setStyleSheet("#CenterPanel { background-color: #0b1320; }")
        c_layout = QGridLayout(center)
        c_layout.setContentsMargins(12,12,12,12)
        c_layout.setSpacing(10)
        
        self.ic_b_gt = ImageCard("Ground Truth — Bone", "bone", "PHANTOM", C['orange'])
        self.ic_t_gt = ImageCard("Ground Truth — Soft Tissue", "tissue", "PHANTOM", C['blue'])
        self.ic_p_l = ImageCard("Low-Energy Projection", "xray", "40 keV", C['red'], "Run Acquisition first")
        self.ic_p_h = ImageCard("High-Energy Projection", "xray", "100 keV", C['green'], "Run Acquisition first")
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
        right.setObjectName("RightPanel")
        right.setFixedWidth(242)
        right.setStyleSheet(f"#RightPanel {{ background-color: {C['panel']}; border-left: 1px solid {C['border']}; }}")
        
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
        self.mr_el = MRow("Low Energy", unit="keV")
        self.mr_eh = MRow("High Energy", unit="keV")
        self.mr_esep = MRow("Energy Separation", unit="keV")
        self.mr_ns = MRow("Noise Level (σ)")
        self.mr_sc = MRow("Scatter Level (β)")
        self.mr_mubl = MRow("Bone Atten. (Low)", unit="cm⁻¹")
        self.mr_mubh = MRow("Bone Atten. (High)", unit="cm⁻¹")
        self.mr_det = MRow("Matrix Determinant")
        
        for mr in [self.mr_el, self.mr_eh, self.mr_esep, self.mr_ns, self.mr_sc, self.mr_mubl, self.mr_mubh, self.mr_det]:
            s6.addWidget(mr)
        
        self.mr_mubl.hide()
        self.mr_mubh.hide()
        self.mr_det.hide()
        r_layout.addWidget(s6)
        
        s7 = Sec("Quality Metrics")
        self.qm_empty = QLabel("Run decomposition\nto compute metrics.")
        self.qm_empty.setStyleSheet(f"font-size: 10px; color: {C['muted']};  line-height: 1.7;")
        s7.addWidget(self.qm_empty)
        
        self.mr_mb = MRow("MAE (Bone)", unit="cm")
        self.mr_mt = MRow("MAE (Tissue)", unit="cm")
        self.mr_cnr = MRow("Contrast-to-Noise Ratio")
        self.mr_snr = MRow("Signal-to-Noise Ratio")
        for mr in [self.mr_mb, self.mr_mt, self.mr_cnr, self.mr_snr]:
            s7.addWidget(mr)
            mr.hide()
        r_layout.addWidget(s7)
        
        s8 = Sec("Attenuation Model")
        lbl = QLabel("ATTENUATION CURVES")
        lbl.setStyleSheet(f"font-size: 9px; color: {C['muted']};  letter-spacing: 1px; margin-bottom: 8px;")
        s8.addWidget(lbl)
        
        self.chart = AttenChart()
        self.chart.setFixedHeight(120)
        s8.addWidget(self.chart)
        r_layout.addWidget(s8)
        
        r_layout.addStretch()
        b_layout.addWidget(right)
        
        main_layout.addWidget(body, 1)
        self.add_log("System ready.")

    def closeEvent(self, event):
        if self.on_close_callback:
            self.on_close_callback()
        event.accept()
