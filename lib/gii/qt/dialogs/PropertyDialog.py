import logging
from gii.core.tmpfile import TempDir

from PyQt4 import QtGui,QtCore
from PyQt4.QtCore import Qt

from gii.qt.controls.PropertyEditor import PropertyEditor

##----------------------------------------------------------------##
class PropertyDialog( QtGui.QDialog ):
	def __init__(self, prompt, *args):
		super(PropertyDialog, self).__init__(*args)
		self.setWindowTitle( prompt )
		btnOK     = QtGui.QPushButton('OK')
		btnCancel = QtGui.QPushButton('Cancel')
		
		buttonBox=QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)
		buttonBox.addButton(btnOK, QtGui.QDialogButtonBox.AcceptRole)
		buttonBox.addButton(btnCancel, QtGui.QDialogButtonBox.RejectRole)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		box = QtGui.QVBoxLayout( self )
		box.setMargin( 10 )
		box.setSpacing( 5 )

		propertyEditor = PropertyEditor( self )
		box.addWidget(propertyEditor)
		box.addWidget(buttonBox)

		self.propertyEditor = propertyEditor

	def setTarget( self, target ):
		self.propertyEditor.setTarget( target )


##----------------------------------------------------------------##		
def requestProperty( prompt, target ):
	dialog = PropertyDialog( prompt )
	dialog.setTarget( target )
	dialog.move( QtGui.QCursor.pos() )

	if dialog.exec_():
		return True
	else:
		return False

