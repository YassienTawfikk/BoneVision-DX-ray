import sys
from PyQt5.QtWidgets import QApplication
from view import MainWindow
from controller import MainController
from core import PhysicsEngine

def main():
    app = QApplication(sys.argv)
    
    # MVC Architecture Setup
    window = MainWindow()
    controller = MainController(window, PhysicsEngine)
    
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
