from gii.core import  *
from gii.SceneEditor.Introspector   import ObjectEditor, CommonObjectEditor, registerObjectEditor
from gii.qt.controls.PropertyEditor import PropertyEditor
from gii.qt.helpers import addWidgetWithLayout, repolishWidget
from gii.qt.IconCache               import getIcon

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt, pyqtSlot
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

##----------------------------------------------------------------##
class SceneObjectEditorMixin():
	#field proto state
	def initFieldContextMenu( self, propertyEditor ):
		self.propertyEditor = propertyEditor
		propertyEditor.contextMenuRequested.connect( self.onFieldContextMenuRequested )
	
	def onFieldResetDefault( self ):
		print 'reset default', self.currentFieldContext

	def onFieldResetProto( self ):
		target, fieldId = self.currentFieldContext
		_MOCK.resetProtoInstanceOverridedField( target, fieldId )
		self.propertyEditor.refreshField( fieldId )
		self.currentFieldContext = None
		self.onPropertyReset( target, fieldId )

	def onFieldAddKey( self ):
		target, fieldId = self.currentFieldContext
		animator = app.getModule( 'animator' )
		animator.addKeyForField( target, fieldId )

	def onFieldContextMenuRequested( self, target, fieldId ):
		menu = QMenu("Field Context")
		itemTitle = menu.addAction( '[ %s ]' % fieldId )
		itemTitle.setEnabled( False )
		menu.addSeparator()

		animator = app.getModule( 'animator' )
		if animator:
			itemAddKey = menu.addAction( 'Add key' )
			itemAddKey.setIcon( getIcon('key') )
			itemAddKey.triggered.connect( self.onFieldAddKey )
			menu.addSeparator()

		# itemDefault = menu.addAction( 'Set Default' )
		# itemDefault.triggered.connect( self.onFieldResetDefault )

		if _MOCK.isProtoInstanceOverrided( target, fieldId ):
			menu.addSeparator()
			itemProtoReset = menu.addAction( 'Reset To Proto Value' )
			itemProtoReset.triggered.connect( self.onFieldResetProto )
			itemProtoReset.setIcon( getIcon('reset') )

		self.currentFieldContext = ( target, fieldId )
		menu.exec_(QtGui.QCursor.pos())

	#foldstate
	def initFoldState( self ):
		self.getContainer().foldChanged.connect( self.onFoldChanged )
	
	def restoreFoldState( self ):
		folded = self.getTarget()['__foldState'] or False
		self.getContainer().toggleFold( folded, False )

	def onFoldChanged( self, folded ):
		self.getTarget()['__foldState'] = folded

	#animtor track button
	def initAnimatorButton( self ):
		#check if there is animator track
		button = self.container.getButtonKey()
		button.clicked.connect( self.onCustomTrackMenuRequested )
		button.hide()

	def updateAnimatorButton( self ):
		animator = app.getModule( 'animator' )
		if not animator:
			return
		target = self.getTarget()
		button = self.container.getButtonKey()
		if target and _MOCK.objectHasAnimatorTrack( self.getTarget() ):
			button.show()
		else:
			button.hide()

	def onCustomTrackMenuRequested( self ):
		menu = QMenu("Animator Track Context")
		itemTitle = menu.addAction( 'Create Custom Animator Track' )
		itemTitle.setEnabled( False )
		menu.addSeparator()
		trackTypes = _MOCK.getCustomAnimatorTrackTypesForObject( self.getTarget() )
		if not trackTypes: return
		for id, clas in trackTypes.items():
			action = menu.addAction( id )
			action.triggered.connect( lambda x: self.addCustomAnimatorTrack( id ) )
			action.setIcon( getIcon('object_track') )
		menu.exec_(QtGui.QCursor.pos())

	def addCustomAnimatorTrack( self, id ):
		animator = app.getModule( 'animator' )
		animator.addCustomAnimatorTrack( self.getTarget(), id )

##----------------------------------------------------------------##
class EntityHeader( EntityHeaderBase, QtGui.QWidget ):
	def __init__(self, *args ):
		super(EntityHeader, self).__init__( *args )
		self.setupUi( self )

##----------------------------------------------------------------##
class ComponentEditor( CommonObjectEditor, SceneObjectEditorMixin ): #a generic property grid 
	def onPropertyChanged( self, obj, id, value ):
		if _MOCK.markProtoInstanceOverrided( obj, id ):
			self.grid.refershFieldState( id )
		signals.emit( 'entity.modified', obj._entity, 'introspector' )

	def onPropertyReset( self, obj, id ):
		self.grid.refershFieldState( id )
		signals.emit( 'entity.modified', obj._entity, 'introspector' )

	def initWidget( self, container, objectContainer ):
		self.grid = super( ComponentEditor, self ).initWidget( container, objectContainer )
		
		self.initFieldContextMenu( self.grid )
		self.initFoldState()
		self.initAnimatorButton()
		return self.grid

	def setTarget( self, target ):
		super( ComponentEditor, self ).setTarget( target )
		if target['__proto_history']:
			self.container.setProperty( 'proto', True )
		else:
			self.container.setProperty( 'proto', False )
		self.container.repolish()
		self.restoreFoldState()
		self.updateAnimatorButton()
		#recording check
		# for field, editor in self.grid.editors.items():
		# 	pass
		

##----------------------------------------------------------------##
class EntityEditor( ObjectEditor, SceneObjectEditorMixin ): #a generic property grid 
	def initWidget( self, container, objectContainer ):
		self.header = EntityHeader( container )
		self.grid = PropertyEditor( self.header )
		self.header.layout().addWidget( self.grid )
		self.grid.setContext( 'scene_editor' )		

		self.grid.propertyChanged.connect( self.onPropertyChanged )		
		self.header.buttonEdit   .clicked .connect ( self.onEditPrefab )
		self.header.buttonGoto   .clicked .connect ( self.onGotoPrefab )
		self.header.buttonUnlink .clicked .connect ( self.onUnlinkPrefab )
		
		self.initFieldContextMenu( self.grid )
		self.initFoldState()
		self.initAnimatorButton()

		return self.header

	def setTarget( self, target ):
		if not target.components: return
		introspector = self.getIntrospector()
		self.target = target
		self.grid.setTarget( target )		
		if isMockInstance( target, 'Entity' ):
			if target['__proto_history']:				
				self.container.setProperty( 'proto', True )
			else:
				self.container.setProperty( 'proto', False )
			self.container.repolish()
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
		self.restoreFoldState()
		self.updateAnimatorButton()

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

	def refresh( self ):
		self.grid.refreshAll()

	def unload( self ):
		self.target = None
		self.grid.clear()

registerObjectEditor( _MOCK.Entity, EntityEditor )