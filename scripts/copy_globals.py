from lyse import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from functools import partial #controller library
import sys
import json
from os.path import basename
import os
import pyperclip as pc
from lyse import *
import traceback
from pathlib import Path

def h(n,string):
	return f'<h{n}>' + string + f'</h{n}>'

class CopyGlobalsView(QMainWindow):
	def __init__(self,*args,**kwargs):
		super(CopyGlobalsView, self).__init__()
		self.dir = Path(kwargs['dir'])
		self.filename = None
		#define primitive variables

		#define primitive widgets
		self.updateTitle()
		self.setGeometry(100,100,400,300)
		self.mainPage = QWidget()
		self.mainLayout = QVBoxLayout()
		self.mainPage.setLayout(self.mainLayout)
		self.setCentralWidget(self.mainPage)
		self.setUpUI()
		self.addInfo()

	def setUpUI(self):
		#add toolbar
		self.menuBar = self.menuBar()
		fileMenu = self.menuBar.addMenu("&File")
		self.openAction = QAction("&Open Shot...", self)
		fileMenu.addAction(self.openAction)

		#set up input
		self.mainLayout.addWidget(
			QLabel(h(2,'Input Sequence to Copy')))
		self.input_h5_filepath = QLineEdit()
		self.input_h5_filepath.setEnabled(False)
		self.formLayout = QFormLayout()
		self.formLayout.addRow("Input .h5 Filepath: ", self.input_h5_filepath)
		self.buttonLayout = QHBoxLayout()
		self.openShot = QPushButton("Open Shot")
		self.buttonLayout.addWidget(self.openShot)
		self.mainLayout.addLayout(
			self.formLayout)
		self.mainLayout.addLayout(
			self.buttonLayout)

		#set up globals view
		self.mainLayout.addWidget(
			QLabel(h(2,'Different Globals:')))
		self.globals_view = QListWidget()
		self.mainLayout.addWidget(self.globals_view)

		#set up output view
		self.mainLayout.addWidget(
			QLabel(h(2,'Global Files to Edit.')))
		self.global_files_view = QListWidget()
		self.mainLayout.addWidget(
			self.global_files_view)
		self.update_globals = QPushButton("Update with New Globals")
		self.mainLayout.addWidget(self.update_globals)
	def addInfo(self):
		self.global_files_view.addItem(
			QListWidgetItem(f"Globals Directory:\n    {self.dir}"))



	def updateTitle(self):
		self.setWindowTitle(f"Copy Globals - YbClock Inc.")

	def openFile(self):
		filename, _ = QFileDialog.getOpenFileName(self, 'Open a Notes File...', 'C:/Experiments', 'All Files (*.*)')
		if filename:
			self.filename = Path(filename)
			self.filename = self.filename.resolve()
			self.input_h5_filepath.setText(str(self.filename))
class CopyGlobalsModel(CopyGlobalsView):
	global_files_to_update = []
	def __init__(self, *args, global_files=[], **kwargs):
		super(CopyGlobalsModel,self).__init__(*args,**kwargs)
		self.global_files_to_update = global_files
		self.globals = {}
		self.diff_globals = {}
		self.fix_pathnames()

	def get_globals(self):
		'saves globals from input'

		self.run = Run(str(self.filename), no_write=True)
		self.globals = self.run.get_globals()
		self.get_diff_globals()

	def fix_pathnames(self):
		#fix global path names
		global_paths = []
		for fname in self.global_files_to_update:
			fpath = self.dir / fname
			fpath = fpath.resolve()
			if fpath.exists():
				print(str(fpath))
				global_paths.append(str(fpath))
		self.global_paths = global_paths
	def set_globals(self):
		'sets globals to output files'
		
		pass
	def get_diff_globals(self):
		import pathlib

		#fix global path names
		global_paths = []
		for fname in self.global_files_to_update:
			fpath = self.dir / fname
			fpath = fpath.resolve()
			if fpath.exists():
				print(str(fpath))
				global_paths.append(str(fpath))

		#update all diffs.
		for fpath in global_paths:
			print(fpath)
			other = Run(fpath, no_write=True)
			diff_globals = self.run.globals_diff(other)
			self.diff_globals.update(
					diff_globals
				)

		#update all diffs in view
		self.globals_view.clear()
		for key, value in self.diff_globals.items():
			self.globals_view.addItem(
				QListWidgetItem(f"{key} :\n     {value}"))
			print(f"{key} :\n     {value}")
		if len(self.diff_globals) == 0:
			self.globals_view.addItem(
				QListWidgetItem("No difference."))


class CopyGlobalsController(CopyGlobalsModel):
	def __init__(self,*args,**kwargs):
		super(CopyGlobalsController,self).__init__(*args,**kwargs)
		#connect View to Model
		self.openShot.clicked.connect(self.get_globals)
		self.update_globals.clicked.connect(self.set_globals)
		self.openAction.triggered.connect(self.openFile)

def main():
	DIR = r'C:/Users/YbClockReloaded/labscript-suite/userlib/labscriptlib/ybclock'

	app = QApplication([])
	view = CopyGlobalsController(
			dir=DIR,
			global_files = [
				'optimization.h5',
				'globals.h5'
			]
		)
	view.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()

