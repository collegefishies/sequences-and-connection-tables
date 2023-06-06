import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import numpy as np

def main():
    win = pg.GraphicsLayoutWidget(show=True)
    win.resize(800, 600)
    win.setWindowTitle('pyqtgraph example: Plotting')
    plt1 = win.addPlot(title="Plot1")
    plt2 = win.addPlot(title="Plot2")
    plt3 = win.addPlot(title="Plot3")
    pass

if __name__ == "__main__":
    try:
        main()
    except:
        pass