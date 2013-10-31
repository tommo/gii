from gii.core.model import *

from PropertyEditor import FieldEditor, registerFieldEditor
from gii.SearchView import requestSearchView

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class ActionFieldButton( QtGui.QToolButton ):
	def sizeHint( self ):
		return QtCore.QSize( 20, 20)

##----------------------------------------------------------------##
class ActionFieldEditor( FieldEditor ):
	def setTarget( self, parent, field ):
		super( ActionFieldEditor, self ).setTarget( parent, field )
		t = field.getType()
		self.actionName    = t.actionName

	def get( self ):
		pass
		
	def set( self, value ):
		pass
		
	def setValue( self, value ):		
		pass

	def initLabel( self, label, container ):
		self.label = label
		return ''

	def initEditor( self, container ):
		self.button = ActionFieldButton( container )
		self.button.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		self.button.setText( self.label )		
		self.button.clicked.connect( self.doAction )
		return self.button

	def doAction( self ):
		print 'action!!!', self.actionName

	def setFocus( self ):
		self.button.setFocus()

registerFieldEditor( ActionType, ActionFieldEditor )

