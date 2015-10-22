from gii.core.model import *
from gii.qt.helpers import repolishWidget

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

from FieldEditorControls import *

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
_FieldEditorRegistry  = {}
_ModelEditorRegistry  = {}

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
		self.pool = []

	def getPriority( self ):
		return self.priority

	def createEditor( self, parentEditor, field ):
		# cached = self.pool.pop()
		return self.clas( parentEditor, field )

	def build( self,parentEditor, field, context = None ):
		dataType  = field._type
		if field.getOption( 'objtype', None) == 'ref' :
			dataType    = ReferenceType
		while True:
			if dataType == self.targetTypeId:
				return self.createEditor( parentEditor, field )
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
class PropertyEditor( QtGui.QFrame ):
	propertyChanged = QtCore.pyqtSignal( object, str, object )
	objectChanged   = QtCore.pyqtSignal( object )
	contextMenuRequested = QtCore.pyqtSignal( object, str )
	
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
		self.layout.setMargin( 4 )
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
		self.model      = False
		self.clear()
		
	def addFieldEditor( self, field ):
		label = field.label
		editor  =  buildFieldEditor( self, field )
		labelWidget  = editor.initLabel( label, self )
		editorWidget = editor.initEditor( self )
		editorWidget.setObjectName( 'FieldEditor' )
		labelWidget.setObjectName( 'FieldLabel' )
		editor.initState()
		if labelWidget in (None, False):
			self.layout.addRow ( editorWidget )
		else:
			self.layout.addRow ( labelWidget, editorWidget )
		self.editors[ field ] = editor
		return editor

	def getFieldEditor( self, field ):
		return self.editors.get( field, None )

	def addSeparator( self ):
		line = QtGui.QFrame( self )
		line.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Fixed
		)
		# line.setStyleSheet('background:none; border:none; ')
		line.setStyleSheet('background:none; border-top:1px solid #353535; margin: 2px 0 2px 0;')
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

	def onObjectChanged( self ):
		if self.refreshing: return
		self.objectChanged.emit( self.target )
		return self.refreshAll()

	def onPropertyChanged( self, field, value ):
		if self.refreshing : return
		self.model.setFieldValue( self.target, field.id, value )
		self.propertyChanged.emit( self.target, field.id, value )
		self.objectChanged.emit( self.target )
		
	def onContextMenuRequested( self, field ):
		self.contextMenuRequested.emit( self.target, field.id )

	def getTarget( self ):
		return self.target
		
	def setTarget( self, target, **kwargs ):
		oldtarget = self.target
		self.hide()
		model = kwargs.get( 'model', None )
		if not model: model = ModelManager.get().getModel(target)
		if not model:
			self.model = None
			self.clear()
			return

		rebuildFields = model != self.model
		assert(model)
		if rebuildFields:
			self.clear()
			
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
			
		self.model  = model
		self.target = target
		self.refreshAll()
		self.show()

	def refreshFor( self, target ):
		if target == self.target:
			return self.refreshAll()
			
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
			editor.refreshing = True
			editor.set( v )
			editor.refreshing = False
			self.refreshing = False
			editor.setOverrided( self.model.isFieldOverrided( target, field.id ) )

	def refershFieldState( self, fieldId ):
		target = self.target
		if not target: return
		for field in self.model.fieldList: #todo: just use propMap to iter?
			if field.id == fieldId:
				editor = self.editors.get( field, None )
				if not editor: return
				editor.setOverrided( self.model.isFieldOverrided( target, field.id ) )

##----------------------------------------------------------------##
class FieldEditor( object ):
	def __init__( self, parent, field, fieldType = None ):
		self.setTarget( parent, field )
		self.fieldType = fieldType or field._type
		self.overrided = False

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

	def notifyContextMenuRequested( self ):
		return self.parent.onContextMenuRequested( self.field )

	def notifyObjectChanged( self ):
		return self.parent.onObjectChanged()
		
	def get( self ):
		pass

	def set( self, value ):
		pass

	def setReadonly( self, readonly = True ):
		pass

	def setOverrided( self, overrided = True ):
		if overrided == self.overrided: return
		self.overrided = overrided
		self.labelWidget.setProperty( 'overrided', overrided )
		repolishWidget( self.labelWidget )

	def setRecording( self, recording = True ):
		self.labelWidget.setProperty( 'recording', recording )
		repolishWidget( self.labelWidget )

	def initLabel( self, label, container ):
		self.labelWidget = FieldEditorLabel( container )
		self.labelWidget.setEditor( self )
		self.labelWidget.setText( label )
		return self.labelWidget

	def initEditor( self, container ):
		return QtGui.QWidget( container )

	def initState( self ):
		self.setReadonly( self.getOption( 'readonly', False ) )
		
	def clear( self ):
		pass

