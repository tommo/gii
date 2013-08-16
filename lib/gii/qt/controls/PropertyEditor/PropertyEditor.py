from gii.core.model import *

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
		
_FieldEditorRegistry = {}
_ModelEditorRegistry = {}

def registerFieldEditor( dataType, clas ):
	_FieldEditorRegistry[ dataType ] = clas

def getFieldEditor( dataType ):
	while True:
		editor = _FieldEditorRegistry.get( dataType, None )
		if editor: return editor
		dataType = getSuperType( dataType )
		if not dataType: return None
	

def registerModelEditor( model, clas ):
	_ModelEditorRegistry[ model ] = clas

##----------------------------------------------------------------##
class PropertyEditor( QtGui.QWidget ):
	propertyChanged = QtCore.pyqtSignal( object, str, object )

	def __init__( self, parent ):
		super( PropertyEditor, self ).__init__( parent )
		layout = QtGui.QFormLayout( )
		self.setLayout( layout )
		self.layout = layout
		self.layout.setSpacing( 10 )
		self.layout.setVerticalSpacing( 3 )
		self.layout.setLabelAlignment( Qt.AlignLeft )
		self.layout.setFieldGrowthPolicy( QtGui.QFormLayout.ExpandingFieldsGrow )

		self.editors = {}
		self.target  = None
		self.refreshing = False
		self.clear()

	def _buildSubEditor( self, field, label, editorClas ):
		editor = editorClas( self, field )
		labelWidget  = editor.initLabel( label, self )
		editorWidget = editor.initEditor( self )
		self.layout.addRow ( labelWidget, editorWidget )

		self.editors[ field ] = editor
		return editor

	def clear( self ):
		layout = self.layout
		while layout.count() > 0:
			child = layout.takeAt( 0 )
			if child :
				w = child.widget()
				if w:
					w.setParent( None )
				else:
					print 'cannot remove obj:', child
			else:
				break
		self.editors.clear()
		self.target  = None

	def onPropertyChanged( self, field, value ):
		if self.refreshing : return
		self.model.setFieldValue( self.target, field.id, value )
		self.propertyChanged.emit( self.target, field.id, value )

	def setTarget( self, target, **kwargs ):
		oldtarget = self.target

		if target==self.target:
			return
		self.hide()
		self.clear()
		model = kwargs.get( 'model', None )
		if not model: model = ModelManager.get().getModel(target)
		if not model: 
			return

		self.model  = model
		self.target = target

		assert(model)
		#install field info
		for field in model.fieldList:
			label = field.label
			ft    = field._type
			editorClas  =  getFieldEditor( ft )
			if not editorClas: continue
			editor = self._buildSubEditor( field, label, editorClas )
		self.refreshAll()
		self.show()

	def refreshAll( self ):
		target=self.target
		if not target: return
		for field in self.model.fieldList: #todo: just use propMap to iter?
			self.refreshField( field )

	def refreshField( self, field ):
		target = self.target
		if not target: return
		editor = self.editors.get( field, None )
		if editor:			
			v = self.model.getFieldValue( target, field.id )
			self.refreshing = True #avoid duplicated update
			editor.set( v )
			self.refreshing = False


##----------------------------------------------------------------##
class FieldEditor( object ):
	def __init__( self, parent, field ):
		self.setTarget( parent, field )
		
	def setTarget( self, parent, field ):
		self.field   = field
		self.parent  = parent

	def getOption( self, key, v = None ):
		return self.field.option.get( key, v )

	def notifyChanged( self, value ):
		return self.parent.onPropertyChanged( self.field, value )

	def get( self ):
		pass

	def set( self, value ):
		pass

	def initLabel( self, label, container ):
		self.labelWidget = QtGui.QLabel( container )
		self.labelWidget.setText( label )
		self.labelWidget.setMinimumSize( 50, 16 )
		self.labelWidget.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		return self.labelWidget

	def initEditor( self, container ):
		return QtGui.QWidget( container )



