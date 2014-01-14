from gii.core import  *
from gii.SceneEditor.Introspector   import ObjectEditor, registerObjectEditor
from gii.qt.controls.PropertyEditor import PropertyEditor
from gii.qt.helpers import addWidgetWithLayout

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEventLoop, QEvent, QObject


from mock import _MOCK, isMockInstance, getMockClassName


##----------------------------------------------------------------##
def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

EntityHeaderBase, BaseClass = uic.loadUiType(getModulePath('EntityHeader.ui'))

class EntityHeader( EntityHeaderBase, QtGui.QWidget ):
	def __init__(self, *args ):
		super(EntityHeader, self).__init__( *args )
		self.setupUi( self )		
		
class EntityEditor( ObjectEditor ): #a generic property grid 
	def initWidget( self, container ):
		self.header = EntityHeader( container )
		self.grid = PropertyEditor( self.header )
		self.header.layout().addWidget( self.grid )
		self.grid.propertyChanged.connect( self.onPropertyChanged )		
		self.grid.setContext( 'scene_editor' )
		self.header.buttonGoto   .clicked .connect ( self.onGotoPrefab   )
		self.header.buttonUnlink .clicked .connect ( self.onUnlinkPrefab )
		self.header.buttonPush   .clicked .connect ( self.onPushPrefab   )
		self.header.buttonPull   .clicked .connect ( self.onPullPrefab   )
		return self.header

	def setTarget( self, target, introspectorInstance ):
		if not target.components: return
		self.target = target
		self.grid.setTarget( target )		
		if isMockInstance( target, 'Entity' ):
			prefabPath = target['__prefabId']
			if prefabPath:
				self.header.containerPrefab.show()
				self.header.labelPrefabPath.setText( prefabPath )
			else:
				self.header.containerPrefab.hide()
			for com in target.components:
				if com.FLAG_INTERNAL: continue
				editor = introspectorInstance.addObjectEditor( com, context_menu = 'component_context' )

	def onPropertyChanged( self, obj, id, value ):		
		if id == 'name':
			signals.emit( 'entity.renamed', obj, value )
		elif id == 'layer':
			signals.emit( 'entity.renamed', obj, value )
		signals.emit( 'entity.modified', obj, 'introspector' )

	def onGotoPrefab( self ):
		assetBrowser = app.getModule( 'asset_browser' )
		if assetBrowser:
			assetBrowser.locateAsset( self.target['__prefabId'] )

	def onUnlinkPrefab( self ):
		app.doCommand(
			'scene_editor/unlink_prefab',
			entity = self.target	
		)

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
		self.grid.clear()

registerObjectEditor( _MOCK.Entity, EntityEditor )