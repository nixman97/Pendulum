from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import math

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.ax = self.figure.add_subplot(111,polar=True)
        self.ax.set_yticklabels([])
        self.ax.set_theta_zero_location('N')
        self.ax.set_theta_direction(-1)
        self.ax.grid(False)

        self.line1, = self.ax.plot([0, 0], [0, 50000], color='b', linewidth=1)
        self.line1b, = self.ax.plot([0, math.radians(180)], [0, 50000], color='b', linewidth=1)
        self.line2,=self.ax.plot([0, 0], [0, 50000], color='r', linewidth=1)
        self.line2b,= self.ax.plot([0, math.radians(180)], [0, 50000], color='r', linewidth=1)

        print(self.line1.get_data()[0][0])

        self.figure.canvas.draw()

    def spin(self,angle,app):
        if angle<0:
            step=1
        if angle<0:
            step=-1
        self.line2.set_data([self.line1.get_data()[0][0],self.line1.get_data()[0][1]],[0,50000])
        self.line2b.set_data([self.line1b.get_data()[0][0],self.line1b.get_data()[0][1]],[0,50000])
        for i in range(int(math.degrees(self.line1.get_data()[0][0])), int(math.degrees(self.line1.get_data()[0][0]))+angle+1,step):
            self.line1.set_data([math.radians(i), math.radians(i)], [0, 50000])
            self.line1b.set_data([math.radians((i + 180) % 360), math.radians((i + 180) % 360)], [0, 50000])
            self.figure.canvas.draw()
            app.processEvents()
        print(self.line1.get_data()[0][0])
