'''
	Opens GUI for saving notes. Run this GUI outside of lyse.

	This application is designed using the View-Model-Controller paradigm. The
	view is the GUI, the Model: the functions you would write without a
	GUI , the controller which connects the two.

	#Data Structure

	* Assumes a .prefs file in `PREFSFILE`.
	* Preferences are stored/used as a dictionary.
'''

from lyse import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QEvent
from functools import partial #controller library
import sys
import json
from os.path import basename
import os
import pyperclip as pc

PREFSFILE = r"C:\Users\YbClockReloaded\labscript-suite\userlib\labscriptlib\ybclock\analysis\scripts\meta\save_notes.prefs"

def h(n,string):
	return f'<h{n}>' + string + f'</h{n}>'

def functionWindow():
	'''
		Crashes lyse often. Practice for making a simple pyqt window.
	'''

	app = QApplication([])

	window = QWidget()
	window.setWindowTitle("save_notes.py -- YbClock")
	window.setGeometry(100,100,280,80)
	window.move(60,15)
	layout = QVBoxLayout()
	buttonLayout = QHBoxLayout()
	layout.addWidget(QLabel(h(1,'Notes')))
	layout.addWidget(QListWidget())
	layout.addWidget(QLabel(h(1,'Notes to Save')))
	formLayout = QFormLayout()
	formLayout.addRow('Experiment:', QComboBox())
	formLayout.addRow('Title:', QLineEdit())
	formLayout.addRow('Details:', QLineEdit())
	layout.addLayout(formLayout)
	layout.addLayout(buttonLayout)
	buttonLayout.addWidget(QPushButton("Save Current Shots"))
	buttonLayout.addWidget(QPushButton("Pull Selected Line"))
	buttonLayout.addWidget(QPushButton("Modify Selected Line"))
	window.setLayout(layout)
	window.show()
	sys.exit(app.exec_())

class InfoWindow(QMessageBox):
	def __init__(self,text, title="Warning!"):
		super(InfoWindow, self).__init__()
		self.setWindowTitle(title)
		self.setText(text)
		self.setIcon(QMessageBox.Information)
		self.exec_()

class SaveNotes(QMainWindow):
	'''
		The SaveNotes application. It uses the class structure to seperate the
		definition of GUI elements.
	'''
	#VIEW
	#VIEW
	#VIEW
	#VIEW
	#VIEW
	def __init__(self):
		super(SaveNotes, self).__init__()
		#define primitive variables
		self.PREFERENCES 	= {} #dictionary
		self.NOTES       	= [] #list of dictionaries
		self.NOTES_TO_ADD	= {} #dictionary of widgets
		self.buttons     	= {} #dictionary
		self.notes_file  	= "Untitled.json"
		self.saved       	= '*'
		self.df          	= {} #dataframe

		#define primitive widgets
		self.updateTitle()
		self.setGeometry(100,100,400,300)
		self.mainPage = QWidget()
		self.mainLayout = QVBoxLayout()
		self.mainPage.setLayout(self.mainLayout)
		self.setCentralWidget(self.mainPage)

		#fill with content
		self.__addToolBar__()
		self.__NotesSavedDisplay__()
		self.__NotesToSave___()

		#connect model to view
		self.__connect__()

		#start up program
		self.LoadPreferences()
		pass

	def updateTitle(self):
		self.setWindowTitle(f"save_notes.py - {basename(self.notes_file)}{self.saved} - YbClock Inc.")

	def __add_Button__(self, buttonName):
		self.buttons[buttonName] = QPushButton(buttonName)
		return self.buttons[buttonName]
	def __addToolBar__(self):
		self.menuBar = self.menuBar()
		self.__createActions__()
		fileMenu = self.menuBar.addMenu("&File")
		fileMenu.addAction(self.newAction)
		fileMenu.addAction(self.openAction)
		fileMenu.addAction(self.saveAction)
		fileMenu = self.menuBar.addMenu("&Edit")
		fileMenu.addAction(self.preferencesAction)
		pass
	def __NotesSavedDisplay__(self):
		self.mainLayout.addWidget(QLabel(h(1,'Saved Notes')))
		self.notes_view = QListWidget()
		self.notes_view.setWordWrap(True)
		self.notes_view.installEventFilter(self)
		self.mainLayout.addWidget(self.notes_view)
	def __NotesToSave___(self):
		formLayout = QFormLayout()
		buttonLayout = QHBoxLayout()
		self.mainLayout.addWidget(QLabel(h(1,'Notes to Save')))
		self.mainLayout.addLayout(formLayout)
		self.mainLayout.addLayout(buttonLayout)

		# self.NOTES_TO_ADD['previous_title'] = QComboBox()
		self.NOTES_TO_ADD['title'] = QLineEdit()
		self.NOTES_TO_ADD['comments'] = QLineEdit()
		# formLayout.addRow('Use a Previous Title:',	self.NOTES_TO_ADD['previous_title'])
		formLayout.addRow('Title:',                 	self.NOTES_TO_ADD['title'])
		formLayout.addRow('Comments:',              	self.NOTES_TO_ADD['comments'])

		buttonLayout.addWidget(self.__add_Button__("Add Current Shots to Notes"))
		# buttonLayout.addWidget(self.__add_Button__("Pull Selected Line from Notes"))
		# buttonLayout.addWidget(self.__add_Button__("Modify Selected Line from Notes"))
		# buttonLayout.addWidget(self.__add_Button__("Push Shots to Lyse"))
	
	#CONTROLLER
	#CONTROLLER
	def __createActions__(self):
		self.newAction = QAction("&New Note File...", self)
		self.openAction = QAction("&Open Note File...", self)
		self.saveAction = QAction("&Save Note File...", self)
		self.preferencesAction = QAction("&Preferences...", self)
	def __connect__(self):
		self.openAction.triggered.connect(self.openNotesFile)
		self.newAction.triggered.connect(self.newNotesFile)
		self.saveAction.triggered.connect(self.saveNotes)

		self.buttons['Add Current Shots to Notes'].clicked.connect(self.addNoteToNotes)
	def eventFilter(self,source,event):
		if event.type() == QEvent.ContextMenu and source is self.notes_view:
			menu = QMenu()
			push = menu.addAction("Copy Sequence Files to Clipboard")
			copy = menu.addAction("Copy Notes to Editor")
			# modify = menu.addAction("Modify Notes")
			action = menu.exec_(event.globalPos())
			if action: #create the menu at the event position (i.e., click position) 
				item = source.itemAt(event.pos())
				if item:
					item_position = item.data(1)
				else:
					item_position = None
					return True
				if action == push:
					note = self.NOTES[item_position]
					files = note['files']
					clean_notes = ['"'+p.replace(os.sep, '\\')+'"' for p in files]
					clean_notes_string = ' '.join(clean_notes)
					pc.copy(clean_notes_string)
				elif action == copy:
					note = self.NOTES[item_position]
					self.NOTES_TO_ADD['title'].setText(note['title'])
					self.NOTES_TO_ADD['comments'].setText(note['comments'])
					print("copy notes to editor")
				elif action == modify:
					print("Modify notes")
				else:
					print("unknown action")

			return True
		return super().eventFilter(source, event)

	#MODEL
	#MODEL
	#MODEL
	#MODEL
	#MODEL
	#MODEL
	def LoadPreferences(self):
		'''
			Loads or creates default preferences if preferences doesn't exist.
		'''
		from os.path import exists

		#create PREFSFILE if it doesn't exist.
		if not exists(PREFSFILE):
			print("PRESFILE not exist.")
			InfoWindow(text=f"PREFSFILE does not exist at {PREFSFILE}\n\n Creating file there...")
			with open(PREFSFILE, 'w') as f:
				pass

		#load PREFSFILE
		# self.PREFERENCES = json.load(PREFSFILE)
	def SavePreferences(self):
		with open(PREFSFILE, 'w') as f:
			json.dump(
					self.PREFERENCES,
					f,
					indent=2
				)
		pass
	def saveNotes(self):
		with open(self.notes_file, 'w') as f:
			json.dump(self.NOTES, f, indent=2)
			self.saved = ''
			self.updateTitle()
	def newNotesFile(self):
		filename, _ = QFileDialog.getSaveFileName(self, 'New File',self.notes_file,'Json Files (*.json)')
		if filename:
			self.clearEverything()
			with open(filename, 'w') as f:
				self.notes_file = filename
				self.saved = ''
			self.updateTitle()
			self.updateNotesView()
	def openNotesFile(self):
		filename, _ = QFileDialog.getOpenFileName(self, 'Open a Notes File...', '', 'Json Files (*.json)')
		if filename:
			self.notes_file = filename
			self.saved = ''
			self.updateTitle()
			with open(filename, 'r') as f:
				self.NOTES = json.load(f)
				self.updateNotesView()
	def addNoteToNotes(self):
		self.df = data()
		title = self.NOTES_TO_ADD['title'].text()
		comments = self.NOTES_TO_ADD['comments'].text()
		filepaths = list(self.df['filepath'])
		seq_index = list(self.df['sequence_index'])

		if title:
			note = {}
			note['title'] = title
			note['comments'] = comments
			note['number_of_shots'] = len(filepaths)
			note['range'] = (seq_index[0], seq_index[-1])
			note['files'] = filepaths

			self.NOTES.append(note)
			self.updateNotesView()
			self.clearNotesToSave()
			self.noteChange()
	def copyNoteToEditor(self, note_dict):
		print(note_dict)
		for key in self.NOTES_TO_ADD:
			self.NOTES_TO_ADD[key] = note_dict[key]
	def modifyNote(self):
		pass
	def updateNotesView(self):
		self.notes_view.clear()
		for i in range(len(self.NOTES)):
			note = self.NOTES[i]
			item = QListWidgetItem(
				f"{i} : " + note['title'] + " : " + note['comments']
				)
			item.setData(1,i) #save position
			self.notes_view.addItem(item)
	def clearEverything(self):
		#clear notes
		self.notes_view.clear()
		self.NOTES = []

		#clear notes to add
		for key, widget in self.NOTES_TO_ADD.items():
			widget.clear()
		self.noteChange()
	def clearNotesToSave(self):
		#clear notes to add
		for key, widget in self.NOTES_TO_ADD.items():
			widget.clear()
	def noteChange(self):
		self.saved = '*'
		self.updateTitle()
class SaveNotesController():
	def __init__(self, model, view):
		self._view = view
		self._connectSignals()

	def _connectSignals(self):
		pass

class SaveNotesModel():
	'''
		Model for our program, which is really nothing more than calling a
		whole bunch of functions to either save or move data.
	'''

	def retreiveSelectedLineComments(self):
		''' Takes Data from selected line in Saved_notes view and populates the editor '''
		pass
	def modifySelectedLineComments(self):
		''' Updates selected line in notes_view with editor data.'''
		pass
	def pushSelectedLineShots(self):
		''' Pushes the selected line shots to lyse '''
		pass
	pass

def lyseScript():
	print("In Lyse")
	pass


def main():
	app = QApplication([])

	#create the view
	view = SaveNotes()
	view.show()
	#create the model 
	model = SaveNotesModel()
	#create the controller
	SaveNotesController(view=view, model=model)



	# for i in range(10):
	#	view.notes_view.addItem(f"jsdafkl{i}")
	# print("Added Notes")

	sys.exit(app.exec_())

if __name__ == "__main__":
	main()

