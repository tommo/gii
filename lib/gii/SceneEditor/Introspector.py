import os
##----------------------------------------------------------------##
from gii.core     import *
from gii.qt.controls.PropertyEditor import PropertyEditor

from PyQt4        import QtCore, QtGui

from SceneEditor  import SceneEditorModule
from IDPool       import IDPool

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
		signals.connect('selection.changed',self.onSelectionChanged)
		self.requestInstance()

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
				minSize = (200,200)
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
		self.objectEditorRegistry[ typeId ] = editorClas

	def getObjectEditor( self, typeId ):		
		while True:
			clas = self.objectEditorRegistry.get( typeId, None )
			if clas: return clas
			typeId = getSuperType( typeId )
			if not typeId: break
		return CommonObjectEditor

	def onSelectionChanged(self, s):
		if not self.activeInstance: return
		target = None
		if isinstance(s, list):
			target = s
		elif isinstance(s, tuple):
			(target) = s
		else:
			target=s
		#first selection only?
		self.activeInstance.setTarget(target)


##----------------------------------------------------------------##
class IntrospectorInstance(object):
	def __init__(self, id):
		self.id = id

		self.target    = None
		self.container = None
		self.editors   = []

	def createWidget(self, container):
		self.container=container
		self.header=container.addWidgetFromFile(
			getAppPath( 'data/ui/introspector.ui' ),
			expanding=False)
		self.header.hide()
	
	def getTarget(self):
		return self.target

	def setTarget(self, t):
		parent = app.getModule('introspector')
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

		typeId = ModelManager.get().getTypeId( self.target )
		if typeId:
			clas = parent.getObjectEditor( typeId )
			editor = clas()			
			self.editors.append( editor )
			widget = editor.initWidget( self.container )
			if widget: 
				self.container.addWidget( widget )
			editor.setTarget( self.target )

	def clear(self):		
		for editor in self.editors:
			editor.unload() #TODO: cache?
		#remove widgets
		layout = self.container.mainLayout
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

	def setTarget( self, target ):
		pass

	def unload( self ):
		pass

		
##----------------------------------------------------------------##
class CommonObjectEditor( ObjectEditor ): #a generic property grid 
	def initWidget( self, container ):
		self.grid = PropertyEditor(container)
		self.grid.propertyChanged.connect( self.onPropertyChanged )
		return self.grid

	def setTarget( self, target ):
		self.grid.setTarget( target )

	def onPropertyChanged( self, obj, id, value ):
		signals.emit( 'entity.modified', obj )

	def refresh( self ):
		self.grid.refreshAll()

	def unload( self ):
		pass


##----------------------------------------------------------------##
def registerObjectEditor( typeId, editorClas ):
	app.getModule('introspector').registerObjectEditor( typeId, editorClas )


##----------------------------------------------------------------##
SceneIntrospector().register()

