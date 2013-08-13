from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class FieldEditorLineEdit(QtGui.QLineEdit):
	def __init__(self, *arg):
		super(FieldEditorLineEdit, self).__init__( *arg )

	def focusInEvent( self, ev ):
		self.selectAll()
		super(FieldEditorLineEdit, self).focusInEvent( ev )
		

##----------------------------------------------------------------##
class FieldEditorSpinBox(QtGui.QSpinBox):
	def __init__(self, *arg):
		super(FieldEditorSpinBox, self).__init__( *arg )

	def focusInEvent( self, ev ):
		self.selectAll()
		super(FieldEditorSpinBox, self).focusInEvent( ev )
		
##----------------------------------------------------------------##
class FieldEditorDoubleSpinBox(QtGui.QDoubleSpinBox):
	def __init__(self, *arg):
		super(FieldEditorDoubleSpinBox, self).__init__( *arg )

	def focusInEvent( self, ev ):
		self.selectAll()
		super(FieldEditorDoubleSpinBox, self).focusInEvent( ev )
		
