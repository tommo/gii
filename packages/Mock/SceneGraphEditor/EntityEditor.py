from gii.core import  *
from gii.SceneEditor.Introspector   import ObjectEditor, CommonObjectEditor, registerObjectEditor
from gii.qt.controls.PropertyEditor import PropertyEditor
from gii.qt.helpers import addWidgetWithLayout, repolishWidget

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEventLoop, QEvent, QObject
from PyQt4.QtGui  import QMenu

from mock import _MOCK, isMockInstance, getMockClassName


##----------------------------------------------------------------##
def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

EntityHeaderBase, BaseClass = uic.loadUiType(getModulePath('EntityHeader.ui'))

def getProtoPath( obj ):
	state = obj['PROTO_INSTANCE_STATE']
	return state['proto'] or state['sub_proto']

class ProtoFieldResetMenuMixin():
	def initContextMenu( self, propertyEditor ):
		self.propertyEditor = propertyEditor
		propertyEditor.contextMenuRequested.connect( self.onContextMenuRequested )
	
	def onContextMenuRequested( self, target, fieldId ):
		menu = QMenu("Field Context")
		itemTitle = menu.addAction( '[ %s ]' % fieldId )
		itemTitle.setEnabled( False )
		menu.addSeparator()
		itemDefault = menu.addAction( 'Set Default Value' )
		itemDefault.triggered.connect( self.onFieldResetDefault )

		if _MOCK.isProtoInstanceOverrided( target, fieldId ):
			menu.addSeparator()
			itemProto = menu.addAction( 'Reset To Proto Value' )
			itemProto.triggered.connect( self.onFieldResetProto )

		self.currentFieldContext = ( target, fieldId )
		menu.exec_(QtGui.QCursor.pos())

	def onFieldResetDefault( self ):
		print 'reset default', self.currentFieldContext

	def onFieldResetProto( self ):
		target, fieldId = self.currentFieldContext
		_MOCK.resetProtoInstanceOverridedField( target, fieldId )
		self.propertyEditor.refreshField( fieldId )
		self.currentFieldContext = None
		self.onPropertyReset( target, fieldId )

##----------------------------------------------------------------##
class EntityHeader( EntityHeaderBase, QtGui.QWidget ):
	def __init__(self, *args ):
		super(EntityHeader, self).__init__( *args )
		self.setupUi( self )		

##----------------------------------------------------------------##
class ComponentEditor( CommonObjectEditor, ProtoFieldResetMenuMixin ): #a generic property grid 
	def onPropertyChanged( self, obj, id, value ):
		if _MOCK.markProtoInstanceOverrided( obj, id ):
			self.grid.refershFieldState( id )
		signals.emit( 'entity.modified', obj._entity, 'introspector' )

	def onPropertyReset( self, obj, id ):
		self.grid.refershFieldState( id )
		signals.emit( 'entity.modified', obj._entity, 'introspector' )

	def initWidget( self, container ):
		self.grid = super( ComponentEditor, self ).initWidget( container )
		self.initContextMenu( self.grid )
		return self.grid

	def setTarget( self, target ):
		super( ComponentEditor, self ).setTarget( target )
		if target['__proto_history']:
			self.container.setProperty( 'proto', True )
			repolishWidget( self.container )
			repolishWidget( self.container.getInnerContainer() )

##----------------------------------------------------------------##
class EntityEditor( ObjectEditor, ProtoFieldResetMenuMixin ): #a generic property grid 
	def initWidget( self, container ):
		self.header = EntityHeader( container )
		self.grid = PropertyEditor( self.header )
		self.header.layout().addWidget( self.grid )
		self.grid.propertyChanged.connect( self.onPropertyChanged )		
		self.grid.setContext( 'scene_editor' )
		self.header.buttonEdit   .clicked .connect ( self.onEditPrefab   )
		self.header.buttonGoto   .clicked .connect ( self.onGotoPrefab   )
		self.header.buttonUnlink .clicked .connect ( self.onUnlinkPrefab )
		
		self.initContextMenu( self.grid )

		return self.header

	def setTarget( self, target ):
		if not target.components: return
		introspector = self.getIntrospector()
		self.target = target
		self.grid.setTarget( target )		
		if isMockInstance( target, 'Entity' ):
			if target['__proto_history']:				
				self.container.setProperty( 'proto', True )
				repolishWidget( self.container )
				repolishWidget( self.container.getInnerContainer() )

			#setup prefab tool
			protoState = target['PROTO_INSTANCE_STATE']
			if protoState:
				self.header.containerPrefab.show()
				protoPath = getProtoPath( target )
				self.header.labelPrefabPath.setText( protoPath )
			else:
				self.header.containerPrefab.hide()
			#add component editors
			for com in target.getSortedComponentList( target ).values():
				if com.FLAG_INTERNAL: continue
				editor = introspector.addObjectEditor(
						com,
						context_menu = 'component_context',
						editor_class = ComponentEditor
					)
				container = editor.getContainer()
				container.foldChanged.connect ( self.onComponentFold )

	def onPropertyChanged( self, obj, id, value ):
		if _MOCK.markProtoInstanceOverrided( obj, id ):
			self.grid.refershFieldState( id )
		if id == 'name':
			signals.emit( 'entity.renamed', obj, value )
		elif id == 'layer':
			signals.emit( 'entity.renamed', obj, value )
		signals.emit( 'entity.modified', obj, 'introspector' )

	def onPropertyReset( self, obj, id ):
		self.grid.refershFieldState( id )
		if id == 'name':
			signals.emit( 'entity.renamed', obj, obj.getName( obj ) )
		elif id == 'layer':
			signals.emit( 'entity.renamed', obj, obj.getName( obj ) )
		signals.emit( 'entity.modified', obj, 'introspector' )
		signals.emit( 'entity.modified', obj, 'introspector' )

	def onGotoPrefab( self ):
		assetBrowser = app.getModule( 'asset_browser' )
		if assetBrowser:
			assetBrowser.locateAsset( getProtoPath(self.target) )

	def onEditPrefab( self ):
		path = getProtoPath( self.target )
		assetNode = app.getAssetLibrary().getAssetNode( path )
		if assetNode:
			assetNode.edit()

	def onUnlinkPrefab( self ):
		app.doCommand(
			'scene_editor/unlink_prefab',
			entity = self.target	
		)
		self.header.containerPrefab.hide()
		
	def onPushPrefab( self ):
		app.doCommand(
			'scene_editor/push_prefab',
			entity = self.target	
		)

	def onPullPrefab( self ):
		app.doCommand(
			'scene_editor/pull_prefab',
			entity = self.target	
		)

	def onComponentFold( self, folded ):
		#TODO:store fold state
		pass

	def refresh( self ):
		self.grid.refreshAll()

	def unload( self ):
		self.target = None
		self.grid.clear()

registerObjectEditor( _MOCK.Entity, EntityEditor )