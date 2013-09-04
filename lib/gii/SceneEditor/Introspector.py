import os
##----------------------------------------------------------------##
from gii.core     import *
from gii.qt.controls.PropertyEditor import PropertyEditor

from PyQt4        import QtCore, QtGui, uic
from PyQt4.QtCore import QEventLoop, QEvent, QObject

from SceneEditor  import SceneEditorModule
from IDPool       import IDPool


##----------------------------------------------------------------##
def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path
##----------------------------------------------------------------##
ObjectContainerBase,BaseClass = uic.loadUiType(getModulePath('ObjectContainer.ui'))

##----------------------------------------------------------------##
class ObjectContainer( QtGui.QWidget ):
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
		
		self.folded = False
		self.toggleFold( False )
		self.ui.buttonFold.clicked.connect( lambda x: self.toggleFold( None ) )
		self.ui.buttonContext.clicked.connect( lambda x: self.openContextMenu() )

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

	def getInnerContainer( self ):
		return self.ui.ObjectInnerContainer

	def toggleFold( self, folded = None ):
		if folded == None:
			folded = not self.folded
		self.folded = folded
		if folded:
			self.ui.buttonFold.setText( '+' )
			self.ui.ObjectInnerContainer.hide()
		else:
			self.ui.buttonFold.setText( '-' )
			self.ui.ObjectInnerContainer.show()

	def setTitle( self, title ):
		self.ui.labelName.setText( title )

	def openContextMenu( self ):
		if self.contextMenu:
			self.contextMenu.popUp()

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
		signals.connect( 'selection.changed', self.onSelectionChanged )
		self.requestInstance()
		signals.connect( 'component.added',   self.onComponentAdded )
		signals.connect( 'component.removed', self.onComponentRemoved )
		signals.connect( 'entity.modified',   self.onEntityModified ) 

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
			for ins in self.instances:
				if ins.target == entity:
					ins.refresh()


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
			getAppPath( 'data/ui/introspector.ui' ),
			expanding=False)
		self.scroll = scroll = container.addWidget( QtGui.QScrollArea( container ) )
		self.body   = body   = QtGui.QWidget( container )
		self.header.hide()

		scroll.setWidgetResizable(True)
		body.mainLayout = layout = QtGui.QVBoxLayout( body )
		layout.setSpacing(0)
		layout.setMargin(0)
		layout.addStretch()
		scroll.setWidget( body )
	
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

	
	def addObjectEditor( self, target ):
		self.body.hide()
		parent = app.getModule('introspector')
		typeId = ModelManager.get().getTypeId( target )
		if typeId:
			editorClas = parent.getObjectEditor( typeId )
			editor = editorClas()			
			self.editors.append( editor )
			container = ObjectContainer( self.body )
			widget = editor.initWidget( container.getInnerContainer() )
			editor.container = container
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
				menuName = editor.getContextMenu()
				container.setContextMenu( menuName )
			editor.setTarget( target, self )
			self.body.show()
			return editor
		self.body.show()
		return None

	def clear(self):		
		for editor in self.editors:
			editor.unload() #TODO: cache?
		#remove widgets
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


##----------------------------------------------------------------##
class ObjectEditor( object ):
	def initWidget( self, container ):
		pass

	def getContextMenu( self ):
		pass

	def setTarget( self, target, introspectorInstance ):
		pass

	def unload( self ):
		pass

		
##----------------------------------------------------------------##
class CommonObjectEditor( ObjectEditor ): #a generic property grid 
	def initWidget( self, container ):
		self.grid = PropertyEditor(container)
		self.grid.propertyChanged.connect( self.onPropertyChanged )
		return self.grid

	def setTarget( self, target, introspectorInstance ):
		self.grid.setTarget( target )

	def onPropertyChanged( self, obj, id, value ):
		signals.emit( 'entity.modified', obj, 'introspector' )

	def refresh( self ):
		self.grid.refreshAll()

	def unload( self ):
		self.grid.clear()


##----------------------------------------------------------------##
def registerObjectEditor( typeId, editorClas ):
	app.getModule('introspector').registerObjectEditor( typeId, editorClas )


##----------------------------------------------------------------##
SceneIntrospector().register()

