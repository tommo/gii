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

	def getName(self):
		return 'introspector'

	def getDependency(self):
		return ['qt', 'scene_editor']
	
	def onLoad(self):
		signals.connect('selection.changed',self.onSelectionChanged)

	def onStart( self ):
		self.requestInstance()
		# self.testObj=makeTestObject()
		# SelectionManager.get().changeSelection(self.testObj)
		# self.updateTimer=App.get().startTimer(1000/2, self.updateProp)

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
		self.grid      = None
		self.container = None

	def createWidget(self, container):
		self.container=container
		self.header=container.addWidgetFromFile(
			getAppPath( 'data/ui/introspector.ui' ),
			expanding=False)
		self.grid = container.addWidget(PropertyEditor(container))
		self.header.hide()
		self.grid.propertyChanged.connect( self.onPropertyChanged )

	def getTarget(self):
		return self.target

	def setTarget(self, t):
		if self.target:
			self.clear()
		
		if not t: 
			self.target=None
			return

		if len(t)>1:
			self.header.textInfo.setText('Multiple object selected...')
			self.header.buttonApply.hide()
			self.header.show()
			self.target=t[0] #TODO: use a multiple selection proxy as target
		else:
			self.target=t[0]

		if self.grid:
			self.grid.setTarget(self.target)
		

	def clear(self):
		self.target=None
		self.header.hide()
		self.grid.clear()
		#TODO

	def refresh(self):
		if not self.target:
			return
		self.grid.refreshAll()
		pass #TODO


	def onPropertyChanged( self, obj, id, value ):
		signals.emit( 'entity.modified', obj )


		
SceneIntrospector().register()
