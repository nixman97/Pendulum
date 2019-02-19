import sys

from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
import MainWindow
ex = MainWindow.MainWindow(app)
sys.exit(app.exec_())
