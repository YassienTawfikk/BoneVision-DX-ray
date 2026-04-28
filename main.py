import sys
import os

# Ensure package imports work from the root directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from controllers.main_controller import MainController

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = MainController(window)
    window.showFullScreen()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
