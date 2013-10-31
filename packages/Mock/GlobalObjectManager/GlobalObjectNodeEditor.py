from gii.core import  *
from gii.SceneEditor.Introspector   import ObjectEditor, registerObjectEditor
from gii.qt.controls.PropertyEditor import PropertyEditor

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEventLoop, QEvent, QObject


from mock import _MOCK, isMockInstance, getMockClassName


##----------------------------------------------------------------##
def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path
		
class EntityEditor( ObjectEditor ): #a generic property grid 
	# def initWidget( self, container ):		
	# 	self.grid = PropertyEditor( container )
	# 	self.grid.setContext( 'scene_editor' )
	# 	return self.grid

	def setTarget( self, target, introspectorInstance ):
		if target.type == 'object':
			introspectorInstance.addObjectEditor( target.object )
		
	# def refresh( self ):
	# 	self.grid.refreshAll()

	# def unload( self ):
	# 	self.grid.clear()

registerObjectEditor( _MOCK.GlobalObjectNode, EntityEditor )