import qgmap
qgmap.use("PyQt5")

from qgmap.common import QGoogleMap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from Calculations import Calculations
from PlotCanvas import PlotCanvas


# noinspection PyArgumentList


class MainWindow(QWidget):

    def _callable(self,l):
        print(l)
    def __init__(self,app):
        super().__init__()
        self.app=app
        # Create layout
        self.a=QGoogleMap()
        print(self.a.page().toHtml(self._callable))
        self.calc_btn = QPushButton("Calculate")
        self.canvas = PlotCanvas(self, width=5, height=4)
        self.hours_line = QLineEdit()
        self.latitude_line = QLineEdit()
        self.latitude_line.setPlaceholderText("Latitude")
        self.hours_line.setPlaceholderText("Hours")
        line_widget = QHBoxLayout()
        line_widget.addWidget(self.hours_line)
        line_widget.addWidget(self.latitude_line)
        main_layout = QVBoxLayout()


        main_layout.addWidget(self.canvas)
        main_layout.addWidget(self.a)

        main_layout.addLayout(line_widget)
        main_layout.addWidget(self.calc_btn)
        self.calc_btn.clicked.connect(self.spin_button_callback)
        self.setLayout(main_layout)
        self.title = 'Pendulum'
        self.setWindowTitle(self.title)
        self.show()


    def spin_button_callback(self):


        self.calc_btn.setEnabled(False)
        try:
            hours=float(self.hours_line.text())
            lat=float(self.latitude_line.text())
            self.canvas.spin(int(Calculations().getAngle(lat,hours)), self.app)
        except AssertionError:
            QMessageBox.critical(self,"Error","Invalid Input")
        self.calc_btn.setEnabled(True)
