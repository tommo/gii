import logging
from gii.core.tmpfile import TempDir

from PyQt4 import QtGui,QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox

class StringDialog(QtGui.QDialog):
	def __init__(self, prompt, *args):
		super(StringDialog, self).__init__(*args)
		lineEdit=QtGui.QLineEdit(self)
		self.setWindowTitle(prompt)
		btnOK=QtGui.QPushButton('OK')
		btnCancel=QtGui.QPushButton('Cancel')
		
		buttonBox=QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)
		buttonBox.addButton(btnOK, QtGui.QDialogButtonBox.AcceptRole)
		buttonBox.addButton(btnCancel, QtGui.QDialogButtonBox.RejectRole)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		box=QtGui.QVBoxLayout()
		self.setLayout(box)

		box.addWidget(lineEdit)
		box.addWidget(buttonBox)

		self.lineEdit=lineEdit

	def getText(self):
		return self.lineEdit.text()
	
def confirmDialog(title, msg, level='normal'):
	f=None
	if level=='warning':
		f=QMessageBox.warning
	elif level=='critical':
		f=QMessageBox.critical
	else:
		f=QMessageBox.queston
	res=f(None, title, msg, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
	if ret==QMessageBox.Yes: return True
	if ret==QMessageBox.Cancel: return None
	if ret==QMessageBox.No: return False

def alertMessage(title, msg, level='warning'):
	f=None
	if level=='warning':
		f=QMessageBox.warning
		logging.warning( msg )

	elif level=='critical':
		f=QMessageBox.critical
		logging.error( msg )

	else:
		f=QMessageBox.queston
	print title
	print msg
	res=f(None, title, msg	)

def requestString(title, prompt):
	text, ok = QtGui.QInputDialog.getText(None, title, prompt)
	# dialog=StringDialog(prompt)
	# dialog.move(QtGui.QCursor.pos())
	# if dialog.exec_():
	# 	return dialog.getText()
	# else:
	# 	return None
	if ok:
		return text
	else:
		return None

def requestColor(prompt, initCol = None):
	col = None
	if initCol: 
		col = QtGui.QColor(initCol)
	else:
		col = QtCore.Qt.white
	col = QtGui.QColorDialog.getColor( 
		col, 
		None,
		prompt,
		QtGui.QColorDialog.ShowAlphaChannel
		)
	if col.isValid(): return col
	return None
