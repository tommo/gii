from PropertyEditor import FieldEditor

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class ReferenceFieldEditor( FieldEditor ):
	def get( self ):
		return self.lineEdit.text()

	def set( self, value ):
		self.lineEdit.setText( value )

	def initEditor( self, container ):
		self.lineEdit = QtGui.QLineEdit( container )
		self.lineEdit.textEdited.connect( self.notifyChanged )
		return self.lineEdit