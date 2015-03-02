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
		
_FieldEditorFactories = []
_FieldEditorRegistry = {}
_ModelEditorRegistry = {}

##----------------------------------------------------------------##
class FieldEditorFactory():
	def getPriority( self ):
		return 0

	def build( self, parentEditor, field, context = None ):
		return None

##----------------------------------------------------------------##
class SimpleFieldEditorFactory( FieldEditorFactory ):
	def __init__( self, typeId, clas, priority = -1 ):
		self.targetTypeId = typeId
		self.clas = clas
		self.priority = priority

	def getPriority( self ):
		return self.priority

	def build( self,parentEditor, field, context = None ):
		dataType  = field._type
		if field.getOption( 'objtype', None) == 'ref' :
			dataType    = ReferenceType
		while True:
			if dataType == self.targetTypeId: 
				return self.clas( parentEditor, field )
			dataType = getSuperType( dataType )
			if not dataType: return None

##----------------------------------------------------------------##
def registerFieldEditorFactory( factory ):
	assert isinstance( factory, FieldEditorFactory )
	p = factory.getPriority()
	for i, fe in enumerate( _FieldEditorFactories ):
		if p >= fe.getPriority():
			_FieldEditorFactories.insert( i, factory )
			return
	_FieldEditorFactories.append( factory )

def registerSimpleFieldEditorFactory( dataType, clas, priority = -1 ):
	factory = SimpleFieldEditorFactory( dataType, clas, priority )
	registerFieldEditorFactory( factory )

##----------------------------------------------------------------##
def buildFieldEditor( parentEditor, field ):
	for factory in _FieldEditorFactories:
		editor = factory.build( parentEditor, field )
		if editor : return editor
	return None

##----------------------------------------------------------------##
class PropertyEditor( QtGui.QWidget ):
	propertyChanged = QtCore.pyqtSignal( object, str, object )
	
	_fieldEditorCacheWidget = None
	_fieldEditorCache = {}

	def __init__( self, parent ):	
		super( PropertyEditor, self ).__init__( parent )
		if not PropertyEditor._fieldEditorCacheWidget:
			PropertyEditor._fieldEditorCacheWidget = QtGui.QWidget()
		self.setObjectName( 'PropertyEditor' )
		layout = QtGui.QFormLayout( )
		self.setLayout( layout )
		self.layout = layout
		self.layout.setHorizontalSpacing( 4 )
		self.layout.setVerticalSpacing( 1 )
		self.layout.setLabelAlignment( Qt.AlignLeft )
		self.layout.setFieldGrowthPolicy( QtGui.QFormLayout.ExpandingFieldsGrow )
		self.setSizePolicy( 
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
		)
		self.editors    = {}
		self.target     = None
		self.refreshing = False
		self.context    = None
		self.clear()
		
	def addFieldEditor( self, field ):
		label = field.label
		editor  =  buildFieldEditor( self, field )
		labelWidget  = editor.initLabel( label, self )
		editorWidget = editor.initEditor( self )
		if labelWidget in (None, False):
			self.layout.addRow ( editorWidget )
		else:
			self.layout.addRow ( labelWidget, editorWidget )
		self.editors[ field ] = editor
		return editor

	def addSeparator( self ):
		line = QtGui.QFrame( self )
		line.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Fixed
		)
		# line.setStyleSheet('background:none; border:none; ')
		line.setStyleSheet('background:none; border-top:1px solid #292929; margin: 2px 0 4px 0;')
		line.setMinimumSize( 30, 7 )
		self.layout.addRow( line )

	def clear( self ):
		for editor in self.editors.values():
			editor.clear()
			
		layout = self.layout
		while layout.count() > 0:
			child = layout.takeAt( 0 )
			if child :
				w = child.widget()
				if w:
					w.setParent( None )
			else:
				break
		self.editors.clear()
		self.target  = None

	def setContext( self, context ):
		self.context = context

	def onPropertyChanged( self, field, value ):
		if self.refreshing : return
		self.model.setFieldValue( self.target, field.id, value )
		self.propertyChanged.emit( self.target, field.id, value )

	def getTarget( self ):
		return self.target
		
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

		self.refreshing = True
		#install field info
		currentId = None
		for field in model.fieldList:
			lastId = currentId
			currentId = field.id
			if field.getOption('no_edit'):
				if field.id == '----' and lastId != '----':
					self.addSeparator()
				continue
			self.addFieldEditor( field )			
		assert self.refreshing
		self.refreshing = False
		
		self.refreshAll()
		self.show()

	def refreshAll( self ):
		target=self.target
		if not target: return
		for field in self.model.fieldList: #todo: just use propMap to iter?
			self._refreshField( field )

	def refreshField( self, fieldId ):
		for field in self.model.fieldList: #todo: just use propMap to iter?
			if field.id == fieldId:
				self._refreshField( field )
				return True
		return False

	def _refreshField( self, field ):
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
	def __init__( self, parent, field, fieldType = None ):
		self.setTarget( parent, field )
		self.fieldType = fieldType or field._type
		
	def setTarget( self, parent, field ):
		self.field   = field
		self.parent  = parent

	def getTarget( self ):
		return self.parent.getTarget()

	def getFieldType( self ):
		return self.fieldType

	def getContext( self ):
		return self.parent.context

	def getOption( self, key, v = None ):
		return self.field.option.get( key, v )

	def notifyChanged( self, value ):
		return self.parent.onPropertyChanged( self.field, value )

	def notifyObjectChanged( self ):
		return self.parent.refreshAll()

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

	def clear( self ):
		pass



