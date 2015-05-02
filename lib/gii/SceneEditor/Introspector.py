import os
##----------------------------------------------------------------##
from gii.core     import *
from gii.qt.controls.PropertyEditor import PropertyEditor
from gii.qt.controls.Menu import MenuManager

from PyQt4        import QtCore, QtGui, uic
from PyQt4.QtCore import Qt, QEventLoop, QEvent, QObject, pyqtSignal, pyqtSlot

from SceneEditor  import SceneEditorModule
from IDPool       import IDPool

from gii.qt.controls.GLWidget import CommonGLWidget
from gii.qt.helpers           import addWidgetWithLayout, repolishWidget
from gii.qt.IconCache         import getIcon

##----------------------------------------------------------------##
def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path
##----------------------------------------------------------------##
ObjectContainerBase,BaseClass = uic.loadUiType(getModulePath('ObjectContainer.ui'))

##----------------------------------------------------------------##
class ObjectContainer( QtGui.QWidget ):
	foldChanged  = pyqtSignal( bool )
	def __init__( self, *args ):
		super( ObjectContainer, self ).__init__( *args )
		self.ui = ObjectContainerBase()
		self.ui.setupUi( self )

		self.setSizePolicy( 
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Fixed
			)

		self.mainLayout = QtGui.QVBoxLayout(self.getInnerContainer())
		self.mainLayout.setSpacing(0)
		self.mainLayout.setMargin(0)
		self.contextObject = None

		self.folded = False
		self.toggleFold( False, True )
		self.ui.buttonFold.clicked.connect( lambda x: self.toggleFold( None ) )
		self.ui.buttonContext.clicked.connect( lambda x: self.openContextMenu() )
		self.ui.buttonContext.setIcon( getIcon( 'menu' ) )
		self.ui.buttonKey.clicked.connect( lambda x: self.openKeyMenu() )
		self.ui.buttonKey.setIcon( getIcon( 'key' ) )
		self.ui.buttonKey.hide()

	def setContextObject( self, context ):
		self.contextObject = context

	def addWidget(self, widget, **layoutOption):
		if isinstance( widget, list):
			for w in widget:
				self.addWidget( w, **layoutOption )
			return
		# widget.setParent(self)		
		if layoutOption.get('fixed', False):
			widget.setSizePolicy(
				QtGui.QSizePolicy.Fixed,
				QtGui.QSizePolicy.Fixed
				)
		elif layoutOption.get('expanding', True):
			widget.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Expanding
				)		
		self.mainLayout.addWidget(widget)
		return widget

	def setContextMenu( self, menuName ):
		menu = menuName and MenuManager.get().find( menuName ) or None
		self.contextMenu = menu
		if not menu:
			self.ui.buttonContext.hide()
		else:
			self.ui.buttonContext.show()

	def setKeyMenu( self, menuName ):
		menu = menuName and MenuManager.get().find( menuName ) or None
		self.keyMenu = menu
		if not menu:
			self.ui.buttonKey.hide()
		else:
			self.ui.buttonKey.show()

	def getInnerContainer( self ):
		return self.ui.ObjectInnerContainer

	def getHeader( self ):
		return self.ui.ObjectHeader

	def repolish( self ):
		repolishWidget( self.ui.ObjectInnerContainer )
		repolishWidget( self.ui.ObjectHeader )
		repolishWidget( self.ui.buttonContext )
		repolishWidget( self.ui.buttonKey )
		repolishWidget( self.ui.buttonFold )

	def toggleFold( self, folded = None, notify = True ):
		if folded == None:
			folded = not self.folded
		self.folded = folded
		if folded:
			self.ui.buttonFold.setText( '+' )
			self.ui.ObjectInnerContainer.hide()
		else:
			self.ui.buttonFold.setText( '-' )
			self.ui.ObjectInnerContainer.show()
		if notify:
			self.foldChanged.emit( self.folded )

	def setTitle( self, title ):
		self.ui.labelName.setText( title )

	def openContextMenu( self ):
		if self.contextMenu:
			self.contextMenu.popUp( context = self.contextObject )

	def openKeyMenu( self ):
		if self.keyMenu:
			self.keyMenu.popUp( context = self.contextObject )

##----------------------------------------------------------------##
class SceneIntrospector( SceneEditorModule ):
	"""docstring for SceneIntrospector"""
	def __init__(self):
		super(SceneIntrospector, self).__init__()
		self.instances      = []
		self.instanceCache  = []
		self.idPool         = IDPool()
		self.activeInstance = None
		self.objectEditorRegistry = {}

	def getName(self):
		return 'introspector'

	def getDependency(self):
		return ['qt', 'scene_editor']
	
	def onLoad(self):		
		self.requestInstance()
		signals.connect( 'selection.changed', self.onSelectionChanged )
		signals.connect( 'component.added',   self.onComponentAdded )
		signals.connect( 'component.removed', self.onComponentRemoved )
		signals.connect( 'entity.modified',   self.onEntityModified ) 
		self.widgetCacheHolder = QtGui.QWidget()
		
	def onStart( self ):
		pass

	def updateProp(self):
		if app.isDebugging():
			return

		if self.activeInstance:
			self.activeInstance.refresh()

	def requestInstance(self):
		#todo: pool
		id   = self.idPool.request()
		container = self.requestDockWindow('SceneIntrospector-%d'%id,
				title   = 'Introspector',
				dock    = 'right',
				minSize = (200,100)
		)
		instance = IntrospectorInstance(id)
		instance.createWidget( container )
		self.instances.append( instance )
		if not self.activeInstance: self.activeInstance=instance
		return instance

	def findInstances(self, target):
		res=[]
		for ins in self.instances:
			if ins.target==target:
				res.append(ins)
		return res

	def getInstances(self):
		return self.instances

	def registerObjectEditor( self, typeId, editorClas ):
		assert typeId, 'null typeid'
		self.objectEditorRegistry[ typeId ] = editorClas

	def getObjectEditor( self, typeId ):		
		while True:
			clas = self.objectEditorRegistry.get( typeId, None )
			if clas: return clas
			typeId = getSuperType( typeId )
			if not typeId: break
		return CommonObjectEditor

	def onSelectionChanged( self, selection, key ):
		if key != 'scene': return
		if not self.activeInstance: return
		target = None
		if isinstance( selection, list ):
			target = selection
		elif isinstance( selection, tuple ):
			(target) = selection
		else:
			target=selection
		#first selection only?
		self.activeInstance.setTarget(target)

	def onComponentAdded( self, com, entity ):
		if not self.activeInstance: return
		if self.activeInstance.target == entity:
			self.activeInstance.setTarget( [entity], True )

	def onComponentRemoved( self, com, entity ):
		if not self.activeInstance: return
		if self.activeInstance.target == entity:
			self.activeInstance.setTarget( [entity], True )

	def onEntityModified( self, entity, context=None ):
		if context != 'introspector' :
			self.refresh( entity, context )

	def refresh( self, target = None, context = None ):
		for ins in self.instances:
			if not target or ins.target == target:
				ins.scheduleUpdate()

##----------------------------------------------------------------##
_OBJECT_EDITOR_CACHE = {} 

def pushObjectEditorToCache( typeId, editor ):
	pool = _OBJECT_EDITOR_CACHE.get( typeId, None )
	if not pool:
		pool = []
		_OBJECT_EDITOR_CACHE[ typeId ] = pool
	editor.container.setUpdatesEnabled( False )
	pool.append( editor )
	return True

def popObjectEditorFromCache( typeId ):
	pool = _OBJECT_EDITOR_CACHE.get( typeId, None )
	if pool:
		editor = pool.pop()
		if editor:
			editor.container.setUpdatesEnabled( True )
		return editor

def clearObjectEditorCache( typeId ):
	if _OBJECT_EDITOR_CACHE.has_key( typeId ):
		del _OBJECT_EDITOR_CACHE[ typeId ]

##----------------------------------------------------------------##
class IntrospectorInstance(object):
	def __init__(self, id):
		self.id = id

		self.target    = None
		self.container = None
		self.body      = None
		self.editors   = []

	def createWidget(self, container):
		self.container = container
		self.header = container.addWidgetFromFile(
			getModulePath( 'introspector.ui' ),
			expanding=False)
		self.scroll = scroll = container.addWidget( QtGui.QScrollArea( container ) )
		self.body   = body   = QtGui.QWidget( container )
		self.header.hide()
		self.scroll.verticalScrollBar().setStyleSheet('width:4px')
		scroll.setWidgetResizable( True )
		body.mainLayout = layout = QtGui.QVBoxLayout( body )
		layout.setSpacing(0)
		layout.setMargin(0)
		layout.addStretch()
		scroll.setWidget( body )

		self.updateTimer = self.container.startTimer( 10, self.onUpdateTimer )
		self.updatePending = False
	
	def getTarget(self):
		return self.target

	def setTarget(self, t, forceRefresh = False ):
		if self.target == t and not forceRefresh: return

		if self.target:
			self.clear()
		
		if not t: 
			self.target=None
			return

		if len(t)>1:
			self.header.textInfo.setText('Multiple object selected...')
			self.header.buttonApply.hide()
			self.header.show()
			self.target = t[0] #TODO: use a multiple selection proxy as target
		else:
			self.target = t[0]

		self.addObjectEditor( self.target )

	
	def addObjectEditor( self, target, **option ):
		self.scroll.hide()
		parent = app.getModule('introspector')
		typeId = ModelManager.get().getTypeId( target )
		if not typeId:
			self.scroll.show()
			return

		#create or use cached editor
		cachedEditor = popObjectEditorFromCache( typeId )
		if cachedEditor:
			editor = cachedEditor
			container = editor.container
			count = self.body.mainLayout.count()
			assert count>0
			self.body.mainLayout.insertWidget( count - 1, container )
			container.show()
			container.setContextObject( target )
			self.editors.append( editor )

		else:
			editorClas = option.get( 'editor_class', None )
			if not editorClas: #get default object editors
				editorClas = parent.getObjectEditor( typeId )

			editor = editorClas()
			editor.targetTypeId = typeId
			self.editors.append( editor )
			container = ObjectContainer( self.body )
			editor.container = container
			widget = editor.initWidget( container.getInnerContainer(), container )
			container.setContextObject( target )
			if widget:
				container.addWidget( widget )				
				model = ModelManager.get().getModelFromTypeId( typeId )
				if model:
					container.setTitle( model.getShortName() )
				else:
					container.setTitle( repr( typeId ) )
					#ERROR
				count = self.body.mainLayout.count()
				assert count>0
				self.body.mainLayout.insertWidget( count - 1, container )
				menuName = option.get( 'context_menu', editor.getContextMenu() )
				container.setContextMenu( menuName )
				container.ownerEditor = editor
			else:
				container.hide()

		editor.parentIntrospector = self
		editor.setTarget( target )
		size = self.body.sizeHint()
		size.setWidth( self.scroll.width() )
		self.body.resize( size )
		self.scroll.show()
		return editor


	def clear(self):		
		for editor in self.editors:
			editor.container.setContextObject( None )
			cached = False
			if editor.needCache():
				cached = pushObjectEditorToCache( editor.targetTypeId, editor )
			if not cached:
				editor.unload()
			editor.target = None

		#remove containers
		layout = self.body.mainLayout
		for count in reversed( range(layout.count()) ):
			child = layout.takeAt( count )
			w = child.widget()
			if w:
				w.setParent( None )
		layout.addStretch()
		
		self.target = None
		self.header.hide()
		self.editors = []

	def refresh(self):
		if not self.target:
			return
		for editor in self.editors:
			editor.refresh()

	def onUpdateTimer( self ):
		if self.updatePending == True:
			self.updatePending = False
			self.refresh()

	def scheduleUpdate( self ):
		self.updatePending = True
	

##----------------------------------------------------------------##
class ObjectEditor( object ):	
	def __init__( self ):
		self.parentIntrospector = None

	def getContainer( self ):
		return self.container

	def getInnerContainer( self ):
		return self.container.ObjectInnerContainer()

	def getIntrospector( self ):
		return self.parentIntrospector
		
	def initWidget( self, container, objectContainer ):
		pass

	def getContextMenu( self ):
		pass

	def setTarget( self, target ):
		self.target = target

	def getTarget( self ):
		return self.target

	def unload( self ):
		pass

	def needCache( self ):
		return True

		
##----------------------------------------------------------------##
class CommonObjectEditor( ObjectEditor ): #a generic property grid 
	def initWidget( self, container, objectContainer ):
		self.grid = PropertyEditor(container)
		self.grid.propertyChanged.connect( self.onPropertyChanged )
		return self.grid

	def setTarget( self, target ):
		self.target = target
		self.grid.setTarget( target )

	def refresh( self ):
		self.grid.refreshAll()

	def unload( self ):
		self.grid.clear()
		self.target = None

	def onPropertyChanged( self, obj, id, value ):
		pass

##----------------------------------------------------------------##
def registerObjectEditor( typeId, editorClas ):
	app.getModule('introspector').registerObjectEditor( typeId, editorClas )


##----------------------------------------------------------------##
SceneIntrospector().register()

