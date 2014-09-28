from gii.core        import app, signals
from gii.qt          import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.moai.MOAIRuntime import MOAILuaDelegate
from gii.DebugView      import DebugViewModule
from gii.qt.helpers       import addWidgetWithLayout, QColorF, unpackQColor

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt


class DebugInfo( DebugViewModule ):
	name = 'debug_info'
	dependency = ['debug_view']

	def onLoad( self ):
		self.windowTitle = 'DebugInfo'
		self.window = self.requestDockWindow( 'DebugInfo',
			title     = 'Debug Info',
			size      = (120,120),
			minSize   = (120,120),
			dock      = 'right'
			)
