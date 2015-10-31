from gii.qt.QtEditorModule  import QtEditorModule

class EditorLayoutManager( QtEditorModule ):
	name = 'editor_layout_manager'
	dependency = [ 'qt' ]

	def onLoad( self ):
		self.currentLayoutId = 'default'
		pass

	def saveLayout( self, id ):
		pass

	def loadLayout( self, id ):
		pass
