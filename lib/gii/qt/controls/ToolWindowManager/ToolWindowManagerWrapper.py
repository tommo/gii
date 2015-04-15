from PyQt4        import QtCore, QtGui, uic
from PyQt4.QtCore import qWarning, Qt

from ToolWindowManagerArea import ToolWindowManagerArea

class ToolWindowManagerWrapper( QtGui.QWidget ) :
	def __init__( self, manager ):
		super( ToolWindowManagerWrapper, self ).__init__( manager )
		self.manager = manager
		self.setWindowFlags( self.windowFlags() | Qt.Tool )
		self.setWindowTitle( '' )

		mainLayout = QtGui.QVBoxLayout( self )
		mainLayout.setContentsMargins( 0, 0, 0, 0 )
		self.manager.wrappers.append( self )

	def closeEvent( self, event ):
		from ToolWindowManager import ToolWindowManager
		toolWindows = []
		for widget in self.findChildren( ToolWindowManagerArea ):
			toolWindows += widget.toolWindows()
		self.manager.moveToolWindows( toolWindows, ToolWindowManager.NoArea )

	def saveState( self ):
		result = {}
		if self.layout().count() > 1:
			qWarning('too many children for wrapper')
			return result

		if self.isWindow() and self.layout().count() == 0:
			qWarning('empty top level wrapper')
			return result

		result[ 'geometry' ] = str( self.saveGeometry() )
		splitter = self.findChild( QtGui.QSplitter )
		if splitter:
			result[ 'splitter' ] = self.manager.saveSplitterState( splitter )
		else:
			area = self.findChild( ToolWindowManagerArea )
			if area:
				result[ 'area' ] = area.saveState()
			elif self.layout().count() > 0:
				qWarning('unknown child')
				return {}
		return result

	def restoreState( self, data ):
		if data.has_key( 'geometry' ):
			self.restoreGeometry( data['geometry'] )
		if self.layout().count() > 0:
			qWarning('wrapper is not empty')
			return
		if data.has_key( 'splitter' ):
			self.layout().addWidget(
				self.manager.restoreSplitterState(data['splitter'].toMap())
				)
		elif data.has_key( 'area' ):
			area = self.manager.createArea()
			area.restoreState( data['area'] )
			self.layout().addWidget( area )

	def isOccupied( self ):
		return self.layout().count() > 0