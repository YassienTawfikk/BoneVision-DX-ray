from PyQt5.QtCore import QTimer, QCoreApplication
from ui.styles import C
from core.phantom import PhantomGenerator
from core.physics import PhysicsModel
from core.metrics import MetricsCalculator
from utils.cleanup import SystemCleanup

class MainController:
    def __init__(self, view):
        self.view = view
        
        # State
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
        
        self.bind_signals()
        self.on_phantom_change(self.pType)
        
    def bind_signals(self):
        self.view.p_sel.valueChanged.connect(self.on_phantom_change)
        self.view.k_el.valueChanged.connect(self.on_el_change)
        self.view.k_eh.valueChanged.connect(self.on_eh_change)
        self.view.k_noise.valueChanged.connect(self.on_noise_change)
        self.view.k_scatter.valueChanged.connect(self.on_scatter_change)
        
        self.view.btn_sim.clicked.connect(self.run_sim)
        self.view.btn_dec.clicked.connect(self.run_dec)
        self.view.btn_rst.clicked.connect(self.reset_pipeline)
        
        self.view.on_close_callback = SystemCleanup.run

    def on_phantom_change(self, v):
        self.pType = v
        self.phantom = PhantomGenerator.generate(v)
        self.view.ic_b_gt.set_data(self.phantom['bone'])
        self.view.ic_t_gt.set_data(self.phantom['tissue'])
        self.reset_pipeline(silent=True)
        self.view.add_log(f"[+] Phantom loaded: {v}")
        self.update_status()

    def on_el_change(self, v):
        self.eL = v
        if self.eL >= self.eH - 5:
            min_v = min(150, self.eL + 5)
            self.view.k_eh.set_value(min_v)
            self.eH = min_v
        self.update_status()

    def on_eh_change(self, v):
        self.eH = v
        if self.eH <= self.eL + 5:
            min_v = min(90, self.eH - 5)
            self.view.k_el.set_value(min_v)
            self.eL = min_v
        self.update_status()
        
    def on_noise_change(self, v):
        self.noise = v
        
    def on_scatter_change(self, v):
        self.scatter = v

    def update_status(self):
        eSep = self.eH - self.eL
        eSepGood = True if eSep >= 45 else (None if eSep >= 25 else False)
        col = C['green'] if eSepGood is True else (C['red'] if eSepGood is False else C['orange'])
        
        self.view.status_e_sep.setText(f"<span style='font-size: 10px; color: {C['muted']}; font-family: 'Courier New', monospace;'>ΔE: <span style='color: {col}; font-weight: bold;'>{int(eSep)} keV</span></span>")
        
        s_text = 'COMPUTING' if self.running else ('COMPLETE' if self.step == 2 else ('SIM DONE — DECOMPOSE?' if self.step == 1 else 'READY'))
        s_col = C['orange'] if self.running else (C['green'] if self.step == 2 else (C['blue'] if self.step == 1 else C['dim']))
        self.view.status_lbl.setText(f"<span style='font-size: 10px; color: {C['muted']}; font-family: 'Courier New', monospace;'>STATUS: <span style='color: {s_col}; font-weight: bold;'>{s_text}</span></span>")
        
        self.view.mr_el.set_val(int(self.eL))
        self.view.mr_eh.set_val(int(self.eH))
        self.view.mr_esep.set_val(int(eSep), eSepGood)
        self.view.mr_ns.set_val(f"{self.noise:.3f}")
        self.view.mr_sc.set_val(f"{self.scatter:.3f}")
        
        self.view.chart.update_energies(self.eL, self.eH)
        self.view.ic_p_l.set_tag(f"{int(self.eL)} keV")
        self.view.ic_p_h.set_tag(f"{int(self.eH)} keV")
        
        self.view.ps_p.set_state(self.phantom is not None, False)
        self.view.ps_al.set_state(self.step >= 1, self.running and self.step == 0)
        self.view.ps_ah.set_state(self.step >= 1, self.running and self.step == 0)
        self.view.ps_md.set_state(self.step >= 2, self.running and self.step == 1)
        self.view.ps_mc.set_state(self.metrics is not None, False)
        
        self.view.btn_sim.setDisabled(self.running)
        self.view.btn_dec.setDisabled(self.projL is None or self.running)
        
        op1 = 0.55 if self.running else 1
        op2 = 0.45 if (self.projL is None or self.running) else 1
        
        self.view.btn_sim.setStyleSheet(f"padding: 9px 12px; margin: 2px 0; border-radius: 5px; border: 1px solid {C['blue']}; background: rgba(77, 168, 218, {int(0.18 * 255 * op1)}); color: {C['blue']}; text-align: left;")
        self.view.btn_dec.setStyleSheet(f"padding: 9px 12px; margin: 2px 0; border-radius: 5px; border: 1px solid {C['green']}; background: rgba(45, 212, 160, {int(0.16 * 255 * op2)}); color: rgba(45, 212, 160, {int(255 * op2)}); text-align: left;")

    def reset_pipeline(self, silent=False):
        self.projL = None
        self.projH = None
        self.boneMap = None
        self.tissueMap = None
        self.metrics = None
        self.dinfo = None
        self.step = 0
        
        self.view.ic_p_l.set_data(None)
        self.view.ic_p_h.set_data(None)
        self.view.ic_b_map.set_data(None)
        self.view.ic_t_map.set_data(None)
        
        self.view.mr_mubl.hide()
        self.view.mr_mubh.hide()
        self.view.mr_det.hide()
        
        self.view.qm_empty.show()
        for mr in [self.view.mr_mb, self.view.mr_mt, self.view.mr_cnr, self.view.mr_snr]:
            mr.hide()
            
        if not silent:
            self.view.add_log("[RST] Pipeline cleared.")
        self.update_status()

    def run_sim(self):
        if self.phantom is None or self.running: return
        self.running = True
        self.update_status()
        QCoreApplication.processEvents()
        
        QTimer.singleShot(50, self._do_sim)
        
    def _do_sim(self):
        self.projL = PhysicsModel.simulate_projection(self.phantom, self.eL, self.noise, self.scatter)
        self.projH = PhysicsModel.simulate_projection(self.phantom, self.eH, self.noise, self.scatter)
        
        self.view.ic_p_l.set_data(self.projL)
        self.view.ic_p_h.set_data(self.projH)
        
        self.boneMap = None
        self.tissueMap = None
        self.metrics = None
        self.dinfo = None
        self.step = 1
        
        mu_bl = PhysicsModel.mu(self.eL, 'bone')
        mu_tl = PhysicsModel.mu(self.eL, 'tissue')
        self.view.add_log(f"[SIM] EL={int(self.eL)} μB={mu_bl:.2f} μT={mu_tl:.2f}")
        
        mu_bh = PhysicsModel.mu(self.eH, 'bone')
        mu_th = PhysicsModel.mu(self.eH, 'tissue')
        self.view.add_log(f"[SIM] EH={int(self.eH)} μB={mu_bh:.2f} μT={mu_th:.2f}")
        
        self.running = False
        self.update_status()
        
    def run_dec(self):
        if self.projL is None or self.running: return
        self.running = True
        self.update_status()
        QCoreApplication.processEvents()
        
        QTimer.singleShot(50, self._do_dec)
        
    def _do_dec(self):
        self.dinfo = PhysicsModel.decompose(self.projL, self.projH, self.eL, self.eH)
        self.boneMap = self.dinfo['boneMap']
        self.tissueMap = self.dinfo['tissueMap']
        
        self.view.ic_b_map.set_data(self.boneMap)
        self.view.ic_t_map.set_data(self.tissueMap)
        
        self.view.mr_mubl.set_val(f"{self.dinfo['muBL']:.3f}")
        self.view.mr_mubh.set_val(f"{self.dinfo['muBH']:.3f}")
        self.view.mr_det.set_val(f"{self.dinfo['det']:.4f}")
        
        self.view.mr_mubl.show()
        self.view.mr_mubh.show()
        self.view.mr_det.show()
        
        self.view.add_log(f"[DEC] det(A)={self.dinfo['det']:.4f}")
        
        self.metrics = MetricsCalculator.compute(self.boneMap, self.tissueMap, self.phantom, self.projL)
        
        self.view.qm_empty.hide()
        self.view.mr_mb.set_val(self.metrics['maeBone'])
        self.view.mr_mt.set_val(self.metrics['maeTissue'])
        self.view.mr_cnr.set_val(self.metrics['cnr'])
        self.view.mr_snr.set_val(self.metrics['snr'])
        
        for mr in [self.view.mr_mb, self.view.mr_mt, self.view.mr_cnr, self.view.mr_snr]:
            mr.show()
            
        self.step = 2
        self.running = False
        self.update_status()
