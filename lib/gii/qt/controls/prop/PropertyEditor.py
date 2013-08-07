from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

'''
	planned control:
		- text
		- number
			+ spin   [later]
			+ slider [later]		
		- boolean
		- subobject
'''
##----------------------------------------------------------------##
		
def registerFieldEditor( dataType, clas ):
	pass

def registerModelEditor( model, clas ):
	pass

##----------------------------------------------------------------##
class PropertyEditor( QtGui.QWidget ):
	def __init__( self, parent ):
		super( PropertyEditor, self ).__init__( parent )
		self.layout = QtGui.QFormLayout( self )
		self.layout.setSpacing( 10 )
		self.layout.setVerticalSpacing( 3 )
		self.layout.setLabelAlignment( Qt.AlignLeft )
		self.layout.setFieldGrowthPolicy( QtGui.QFormLayout.ExpandingFieldsGrow )
		
		self.editors = []

	def _buildSubEditor( self, label, editorClas ):
		editor = editorClas( self, label )
		labelWidget  = editor.initLabel( label, self )
		editorWidget = editor.initEditor( self )
		self.layout.addRow ( labelWidget, editorWidget )
		self.editors.append( editor )

		return editor

	def onPropertyChanged( self, field, value ):
		print field, value

	def setTarget( self, obj ):
		self.target = obj

	def refresh( self ):
		pass


##----------------------------------------------------------------##
class FieldEditor( object ):
	def __init__( self, parent, fieldId ):
		self.setTarget( parent, fieldId )
		
	def setTarget( self, parent, fieldId ):
		self.fieldId = fieldId
		self.parent  = parent

	def notifyChanged( self, value ):
		return self.parent.onPropertyChanged( self, value )

	def get( self ):
		pass

	def set( self, value ):
		pass

	def initLabel( self, label, container ):
		self.labelWidget = QtGui.QLabel( container )
		self.labelWidget.setText( label )
		self.labelWidget.setMinimumSize( 80, 16 )
		self.labelWidget.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		return self.labelWidget

	def initEditor( self, container ):
		return QtGui.QWidget( container )



