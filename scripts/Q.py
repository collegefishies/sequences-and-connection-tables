'''

    This is an application for queuing up shots to be run on the Runmanager.
    Shot's will be written to a file and then read and parsed here to be sent to the runmanager.

    The GUI will consist of a display of the shots in the queue, 
        a button to run a shot, 
        a button to delete a shot,
        a button to clear the queue,
    
'''

from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Q - The Queueing System for Labscript')
        self.setGeometry(300, 300, 300, 300)
        self.show()

        # Create a central widget
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        # Create a layout for the central widget
        self.layout = QtWidgets.QVBoxLayout(self.centralWidget)

        #create the menu
        self.menu = self.menuBar()
        self.fileMenu = self.menu.addMenu('File')

        #add a form layout
        self.formLayout = QtWidgets.QFormLayout()
        self.layout.addLayout(self.formLayout)
        #add an experiment entry to the form
        self.experimentEntry = QtWidgets.QLineEdit()
        self.formLayout.addRow('Experiment', self.experimentEntry)



        #add a table for displaying the Queue
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(['Experiment', 'Shot Description', 'Shot Path'])
        self.layout.addWidget(self.table)

        #add a horizontal layout for the buttons
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.buttonLayout)

        #add a button to run a shot
        self.runButton = QtWidgets.QPushButton('Run Shot', self)
        self.runButton.clicked.connect(self.runShot)
        self.buttonLayout.addWidget(self.runButton)

        #add a button to delete a shot
        self.deleteButton = QtWidgets.QPushButton('Delete Shot', self)
        self.deleteButton.clicked.connect(self.deleteShot)
        self.buttonLayout.addWidget(self.deleteButton)

        #add a button to clear the queue
        self.clearButton = QtWidgets.QPushButton('Clear Queue', self)
        self.clearButton.clicked.connect(self.clearQueue)
        self.buttonLayout.addWidget(self.clearButton)

        #add another horizontal layout for the buttons
        self.buttonLayout2 = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.buttonLayout2)

        #add a button to add a shot to the queue
        self.addButton = QtWidgets.QPushButton('Add Shot to Queue', self)
        self.addButton.clicked.connect(self.addShot)
        self.buttonLayout2.addWidget(self.addButton)


    def runShot(self):
        print('Run Top Shot')
    def deleteShot(self):
        print('Delete Top Shot')
    def clearQueue(self):
        print('Clear Queue')
    def addShot(self):
        print('Add Shot')


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

# Run the main function
if __name__ == '__main__':
    main()

    