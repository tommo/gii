from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

from gii.qt.controls.PropertyEditor  import PropertyEditor
from gii.qt.controls.CodeEditor import CodeEditor

from gii.core import *

from SQScriptEditorWidget import registerSQNodeEditor, SQNodeEditor


##----------------------------------------------------------------##
class SQNodeScriptLuaEditor( SQNodeEditor ):
	def __init__(self):
		super(SQNodeScriptLuaEditor, self).__init__()
		layout = QtGui.QVBoxLayout( self )
		layout.setSpacing( 0 )
		layout.setMargin( 0 )
		self.codeBox = CodeEditor( self )
		self.codeBox.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		layout.addWidget( self.codeBox )
		self.codeBox.textChanged.connect( self.onTextChanged )
		self.firstTouched = False

	def onTextChanged( self ):
		self.targetNode.text = self.codeBox.toPlainText()
		self.notifyChanged()

	def onRefresh( self, node ):
		self.codeBox.setPlainText( node.script or '', 'text/x-lua' )

	def onLoad( self, node ):
		self.firstTouched = False

	def setFocus( self ):
		self.codeBox.setFocus()
		if self.firstTouched: return
		self.firstTouched = True
		self.codeBox.selectAll()

##----------------------------------------------------------------##
registerSQNodeEditor( 'SQNodeScriptLua', SQNodeScriptLuaEditor )