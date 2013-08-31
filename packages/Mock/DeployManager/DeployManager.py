import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.qt          import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.moai.MOAIRuntime import MOAILuaDelegate
from gii.SceneEditor      import SceneEditorModule
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance
##----------------------------------------------------------------##

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
class DeployManager( SceneEditorModule ):
	def __init__(self):
		super( DeployManager, self ).__init__()

	def getName( self ):
		return 'deploy_manager'

	def getDependency( self ):
		return [ 'mock' ]

	def onLoad( self ):
		#UI
		self.container = self.requestSubWindow( 'DeployManager',
			title     = 'Deployment',
			allowDock = False
			)

		#Components
		# self.tree = self.container.addWidget( LayerTreeWidget( multiple_selection = False, sorting = False ) )
		toolbar = self.container.addWidget( QtGui.QToolBar() )
		self.tool = self.addToolBar( 'deploy_manager', toolbar )
		self.window = self.container.addWidgetFromFile( _getModulePath('DeployManager.ui') )
		
		self.addTool( 'deploy_manager/add',    label = '+')
		self.addTool( 'deploy_manager/remove', label = '-')
		self.addTool( 'deploy_manager/up',     label = 'up')
		self.addTool( 'deploy_manager/down',   label = 'down')
		
		# self.container.show()
		self.window.buttonCancel.clicked.connect( self.onButtonCancel )
		self.window.buttonOK.clicked.connect( self.onButtonOK )

	def onStart( self ):
		# self.tree.rebuild()
		pass	

	def onTool( self, tool ):
		name = tool.name

	def onSetFocus( self ):
		self.container.show()
		self.container.raise_()

	def saveConfig( self ):
		pass

	def onButtonCancel( self ):
		self.container.hide()

	def onButtonOK( self ):
		self.saveConfig()
		self.container.hide()

DeployManager().register()