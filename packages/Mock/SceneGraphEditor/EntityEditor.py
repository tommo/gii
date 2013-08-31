from gii.core import  *
from gii.SceneEditor.Introspector   import ObjectEditor, registerObjectEditor
from gii.qt.controls.PropertyEditor import PropertyEditor

from mock import _MOCK, isMockInstance, getMockClassName

class EntityEditor( ObjectEditor ): #a generic property grid 
	def initWidget( self, container ):		
		self.grid = PropertyEditor(container)
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
		signals.emit( 'entity.modified', obj, 'introspector' )

	def refresh( self ):
		self.grid.refreshAll()

	def unload( self ):
		self.grid.clear()

registerObjectEditor( _MOCK.Entity, EntityEditor )