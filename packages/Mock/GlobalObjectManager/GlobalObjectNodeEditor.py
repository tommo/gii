from gii.core import  *
from gii.SceneEditor.Introspector   import CommonObjectEditor, registerObjectEditor
from gii.qt.controls.PropertyEditor import PropertyEditor

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEventLoop, QEvent, QObject


from mock import _MOCK, isMockInstance, getMockClassName


##----------------------------------------------------------------##
def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path
		
class GlobalObjectEditor( CommonObjectEditor ): #a generic property grid 	
	def setTarget( self, target ):
		super( GlobalObjectEditor, self ).setTarget( target )
		if target.type == 'object':
			self.getIntrospector().addObjectEditor( target.object )
		
	def onPropertyChanged( self, obj, id, value ):
		if id == 'name':
			signals.emit( 'global_object.renamed', obj, value )

registerObjectEditor( _MOCK.GlobalObjectNode, GlobalObjectEditor )