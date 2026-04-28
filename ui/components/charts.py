import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from ui.styles import C
from core.physics import PhysicsModel

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
        max_mu = PhysicsModel.mu(20, 'bone')
        
        mu_b = np.array([PhysicsModel.mu(e, 'bone') for e in energies])
        x = ((energies - 20) / 120) * 210
        y_b = 68 - (mu_b / max_mu) * 64
        self.ax.plot(x, y_b, color=C['orange'], linewidth=1.8)
        
        mu_t = np.array([PhysicsModel.mu(e, 'tissue') for e in energies])
        y_t = 68 - (mu_t / max_mu) * 64
        self.ax.plot(x, y_t, color=C['blue'], linewidth=1.8)
        
        for idx, e in enumerate([self.eL, self.eH]):
            mx = ((e - 20) / 120) * 210
            col = C['red'] if idx == 0 else C['green']
            self.ax.plot([mx, mx], [-4, 70], color=col, linewidth=1, linestyle='--', alpha=0.65)
            self.ax.text(mx, -8, str(int(e)), color=col, fontsize=7, ha='center', va='bottom', fontfamily='Courier New')
            
        self.ax.plot(80, 85, marker='o', markersize=3, color=C['orange'])
        self.ax.text(88, 85, 'Bone', color=C['dim'], fontsize=7, va='center', fontfamily='Courier New')
        self.ax.plot(135, 85, marker='o', markersize=3, color=C['blue'])
        self.ax.text(143, 85, 'Tissue', color=C['dim'], fontsize=7, va='center', fontfamily='Courier New')
        
        self.ax.text(0, 74, '20', color=C['muted'], fontsize=7, ha='left', va='top', fontfamily='Courier New')
        self.ax.text(207, 74, '140 keV', color=C['muted'], fontsize=7, ha='right', va='top', fontfamily='Courier New')
        
        self.draw()
