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

EntityHeaderBase, BaseClass = uic.loadUiType(getModulePath('EntityHeader.ui'))

class EntityHeader( EntityHeaderBase, QtGui.QWidget ):
	def __init__(self, *args ):
		super(EntityHeader, self).__init__( *args )
		self.setupUi( self )
		
class EntityEditor( ObjectEditor ): #a generic property grid 
	def initWidget( self, container ):		
		self.grid = PropertyEditor( container )
		self.grid.propertyChanged.connect( self.onPropertyChanged )		
		self.grid.setContext( 'scene_editor' )
		return self.grid

	def setTarget( self, target, introspectorInstance ):
		self.grid.setTarget( target )
		for com in target.components:
			editor = introspectorInstance.addObjectEditor( com )

	def onPropertyChanged( self, obj, id, value ):		
		if id == 'name':
			signals.emit( 'entity.renamed', obj, value )
		elif id == 'layer':
			signals.emit( 'entity.renamed', obj, value )
		signals.emit( 'entity.modified', obj, 'introspector' )

	def refresh( self ):
		self.grid.refreshAll()

	def unload( self ):
		self.grid.clear()

registerObjectEditor( _MOCK.Entity, EntityEditor )