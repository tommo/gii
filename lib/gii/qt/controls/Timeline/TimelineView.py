from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform

from TimelineComponents import TimelineRulerView,TimelineTrackView, _RULER_SIZE, _TRACK_SIZE, _TRACK_MARGIN
from CurveView import CurveView

import sys
import math

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

TimelineForm,BaseClass = uic.loadUiType( _getModulePath('timeline2.ui') )

##----------------------------------------------------------------##
#
##----------------------------------------------------------------##
class TimelineTrack( QObject ):
	def __init__( self, view, node ):
		QObject.__init__( self )
		self.trackViewItem  = False
		self.trackType  = 'normal' # group / object / property
		self.node = node
		self.view = view
		self.folded  = False
		self.visible = True

		self.buildViewItems()
		self.parent   = None
		self.keys     = []
		self.children = []

	def getView( self ):
		return self.view

	def sortKeys( self ):
		#TODO
		pass

	def isVisible( self ):
		if not self.visible: return False
		if self.parent:
			if not self.parent.isVisible(): return False
			if self.parent.folded: return False
		return True

	def addKey( self, keyNode ):
		key = TimelineKey( self, keyNode )
		self.keys.append( key )
		return key

	def removeKey( self, key ):
		self.keys.remove( key )

	def getView( self ):
		return self.view

	def buildViewItems( self ):
		view = self.getView()
		self.trackViewItem = view.trackView.addTrackItem( self )

	def getKeyByNode( self, keyNode ):
		for key in self.keys:
			if key.node == keyNode:
				return key
		return None

	def getTrackItem( self ):
		return self.trackViewItem

	def setY( self, y ):
		self.trackViewItem.setPos( 0, y )

	def setViewItemVisible( self, visible ):
		if visible:
			self.trackViewItem.show()
			self.trackViewItem.show()
		else:
			self.trackViewItem.hide()
			self.trackViewItem.hide()

	def onFoldToggle( self ):
		self.folded = not self.folded
		self.view.updateTrackLayout()

##----------------------------------------------------------------##
class TimelineKey( QObject ):
	def __init__( self, track, node ):
		QObject.__init__( self )
		self.timePos    = 0.0
		self.timeLength = 0.0
		self.track      = track
		self.node       = node
		self.viewItem = None
		self.buildViewItems()

	def setTimePos( self, pos ):
		self.timePos = pos
		self.getView().keyPosChanged.emit( self, self.timePos )
		self.viewItem.updateFromData( self )

	def setTimeLength( self, length ):
		self.timeLength = length
		self.getView().keyLengthChanged.emit( self, self.timeLength )
		self.viewItem.updateFromData( self )

	def getTimePos( self ):
		return self.timePos

	def getTimeLength( self ):
		return self.timeLength

	def getTrack( self ):
		return self.track

	def getView( self ):
		return self.track.getView()

	def __repr__( self ):
		return 'key( %f, %f )' % ( self.timePos, self.timeLength )

	def buildViewItems( self ):
		view = self.getView()
		self.viewItem = self.track.trackViewItem.addKeyItem( self )

##----------------------------------------------------------------##	
class TimelineView( QtGui.QFrame ):
	keySelectionChanged   = pyqtSignal( object )
	trackSelectionChanged = pyqtSignal( object )
	keyPosChanged         = pyqtSignal( object, float )
	keyLengthChanged      = pyqtSignal( object, float )
	trackDClicked         = pyqtSignal( object, float )
	cursorPosChanged      = pyqtSignal( float )
	zoomChanged           = pyqtSignal( float )

	def __init__( self, *args, **kwargs ):
		super( TimelineView, self ).__init__( *args, **kwargs )
		#start up
		self.rebuilding = False
		self.updating   = False
		self.shiftMode  = False

		self.initData()
		self.initUI()

	def initData( self ):
		self.tracks      = []
		self.nodeToTrack = {}

	def initUI( self ):
		self.setObjectName( 'Timeline' )
		self.ui = TimelineForm()
		self.ui.setupUi( self )
		
		self.trackView  = TimelineTrackView( parent = self )
		self.rulerView  = TimelineRulerView( parent = self )
		self.curveView  = CurveView( parent = self )
		self.curveView.setAxisShown( False, True )
		self.ui.containerRuler.setFixedHeight( _RULER_SIZE )
		
		trackLayout = QtGui.QVBoxLayout( self.ui.containerTrack )
		trackLayout.setSpacing( 0)
		trackLayout.setMargin( 0 )
		trackLayout.addWidget( self.trackView )

		curveLayout = QtGui.QVBoxLayout( self.ui.containerCurve )
		curveLayout.setSpacing( 0)
		curveLayout.setMargin( 0 )
		curveLayout.addWidget( self.curveView )

		rulerLayout = QtGui.QVBoxLayout( self.ui.containerRuler )
		rulerLayout.setSpacing( 0)
		rulerLayout.setMargin( 0 )
		rulerLayout.addWidget( self.rulerView )

		# self.rulerView.cursorPosChanged
		self.trackView.zoomChanged.connect( self.onZoomChanged )
		self.rulerView.zoomChanged.connect( self.onZoomChanged )

		self.trackView.scrollPosChanged.connect( self.onScrollPosChanged )
		self.rulerView.scrollPosChanged.connect( self.onScrollPosChanged )

		self.trackView.cursorPosChanged.connect( self.onCursorPosChanged )
		self.rulerView.cursorPosChanged.connect( self.onCursorPosChanged )

		self.tabBar = QtGui.QTabBar()		
		bottomLayout = QtGui.QHBoxLayout( self.ui.containerBottom )
		bottomLayout.addWidget( self.tabBar )
		bottomLayout.setSpacing( 0 )
		bottomLayout.setMargin( 0 )
		self.tabBar.addTab( 'Dope Sheet')
		self.tabBar.addTab( 'Curve View' )
		self.tabBar.currentChanged.connect( self.onTabChanged )
		self.tabBar.setShape( QtGui.QTabBar.RoundedSouth )
		self.tabBar.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)

		self.toolbarEdit = QtGui.QToolBar()
		bottomLayout.addWidget( self.toolbarEdit )
		self.toolbarEdit.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)

		self.setScrollPos( 0 )
		self.setCursorPos( 0 )
		self.setZoom( 1.0 )
		# self.trackView.cursorPosChanged.connect(  )
	def onTabChanged( self, idx ):
		self.ui.containerContents.setCurrentIndex( idx )

	def getRulerHeight( self ):
		return _RULER_SIZE
		
	def getZoom( self ):
		return self.rulerView.getZoom()

	def getScrollPos( self ):
		return self.rulerView.getScrollPos()

	def getCursorPos( self ):
		return self.rulerView.getCursorPos()

	def setZoom( self, zoom ):
		self.rulerView.setZoom( zoom )

	def setScrollPos( self, pos ):
		self.rulerView.setScrollPos( pos )

	def setCursorPos( self, pos ):
		self.rulerView.setCursorPos( pos )

	def posToTime( self, x ):
		zoom = self.getZoom()
		pos  = self.getScrollPos()
		return x/zoom + pos

	def timeToPos( self, pos ):
		zoom = self.getZoom()
		pos0 = self.getScrollPos()
		return ( pos - pos0 ) * zoom

	def setShiftMode( self, enabled = True ):
		self.shiftMode = enabled
		
	def rebuild( self ):
		self.clear()
		self.hide()
		self.rebuilding = True
		for node in self.getTrackNodes():
			self.addTrack( node )
		self.updateTrackLayout()
		self.rebuilding = False
		self.show()

	def clear( self ):
		self.hide()
		self.trackView.clear()
		self.rulerView.clear()
		self.tracks = []
		self.updateTrackLayout()
		self.show()

	def updateTrackLayout( self ):
		y = 0
		for track in self.tracks:
			vis = track.isVisible()
			if vis:
				track.setY( y )
				y += _TRACK_SIZE + _TRACK_MARGIN
			track.setViewItemVisible( vis )
		
	def getTrackByNode( self, node ):
		return self.nodeToTrack.get( node, None )

	def getKeyByNode( self, keyNode ):
		track = self.getParentTrack( keyNode )
		return track and track.getKeyByNode( keyNode ) or None

	def addTrack( self, node, **option ):
		assert not self.nodeToTrack.has_key( node )
		track = TimelineTrack( self, node )
		
		self.nodeToTrack[ node ] = track
		self.tracks.append( track )

		#add keys
		keyNodes = self.getKeyNodes( node )
		if keyNodes:
			for keyNode in keyNodes:
				self.addKey( keyNode )

		self.refreshTrack( node, **option )

		return track

	def removeTrack( self, trackNode ):
		track = self.getTrackByNode( trackNode )
		if not track: return
		i = self.tracks.index( track ) #excpetion catch?
		del self.tracks[i]
		del self.nodeToTrack[ track.node ]
		track.node = None
		track.clear()
		self.ui.containerTracks.layout().removeWidget( track )
		track.setParent( None )
		self.updateScrollTrackSize()

	def addKey( self, keyNode, **option ):
		track = self.getParentTrack( keyNode )
		if not track: return None
		key = track.addKey( keyNode )
		if key:
			self.refreshKey( keyNode, **option )			
		return key

	def removeKey( self, keyNode ):
		track = self.getParentTrack( keyNode )
		if not track: return
		track.removeKey( keyNode )

	def getParentTrack( self, keyNode ):
		trackNode = self.getParentTrackNode( keyNode )
		if not trackNode: return None
		return self.getTrackByNode( trackNode )
	
	def selectTrack( self, trackNode ):
		track = self.getTrackByNode( trackNode )
		if self.selectedTrack == track: return
		if self.selectedTrack: 
			self.selectedTrack.setSelected( False )
			if self.selectedKey:
				self.selectedKey.setSelected( False )
				self.selectedKey = None
		self.selectedTrack = track
		track.setSelected( True )
		self.trackSelectionChanged.emit( trackNode )
		self.keySelectionChanged.emit( None )

	def selectKey( self, keyNode ):
		key = self.getKeyByNode( keyNode )
		if key == self.selectedKey: return
		if self.selectedKey:
			self.selectedKey.setSelected( False )
			self.selectedKey = None
		if key:
			track = key.track
			self.selectTrack( track.node )			
			key.setSelected( True )
			self.selectedKey = key
			self.keySelectionChanged.emit( keyNode )
		else:
			self.keySelectionChanged.emit( None )

	def getSelectedTrack( self ):
		return self.selectedTrack

	def getSelectedKey( self ):
		return self.selectedKey
	
	def getSelectedTrackNode( self ):
		track = self.selectedTrack
		return track and track.node or None

	def getSelectedKey( self ):
		key = self.selectedKey
		return key and key.node or None
	
	def setCursorDraggable( self, draggable = True ):
		self.rulerView.setCursorDraggable( draggable )

	def onCursorPosChanged( self, pos ):
		if self.updating: return
		self.updating = True
		self.rulerView.setCursorPos( pos )
		self.trackView.setCursorPos( pos )
		self.updating = False

	def onScrollPosChanged( self, pos ):
		if self.updating: return
		self.updating = True
		self.rulerView.setScrollPos( pos )
		self.trackView.setScrollPos( pos )
		self.updating = False

	def onZoomChanged( self, zoom ):
		if self.updating: return
		self.updating = True
		#sync widget zoom
		self.rulerView.setZoom( zoom )
		self.trackView.setZoom( zoom )
		self.zoomChanged.emit( zoom )
		self.updating = False
	
	def refreshKey( self, keyNode, **option ):
		key = self.getKeyByNode( keyNode )
		if key:
			pos, length, resizable = self.getKeyParam( keyNode )
			key.setTimePos( pos )
			key.setTimeLength( length )
			key.resizable = resizable
			self.updateKeyContent( key, keyNode, **option )

	def refreshTrack( self, trackNode, **option ):
		track = self.getTrackByNode( trackNode )
		if track:
			self.updateTrackContent( track, trackNode, **option )

	#####
	#VIRUTAL data model functions
	#####
	def getRulerParam( self ):
		return {}

	def formatPos( self, pos ):
		return '%.1f' % pos

	def updateTrackContent( self, track, node, **option ):
		pass

	def updateKeyContent( self, key, keyNode, **option ):
		pass

	def createKey( self ):
		return TimelineKey( )

	def createTrack( self, node ):
		return TimelineTrack( )

	def getTrackNodes( self ):
		return []

	def getKeyNodes( self, trackNode ):
		return []

	def getKeyParam( self, keyNode ):
		return ( 0, 10, True )

	def getParentTrackNode( self, keyNode ):
		return None

	#######
	#Interaction
	#######
	def onTrackClicked( self, track, pos ):
		self.selectTrack( track.node )

	def onTrackDClicked( self, track, pos ):
		pass

	def onKeyClicked( self, key, pos ):
		self.selectKey( key.node )

	def closeEvent( self, ev ):
		self.trackView.deleteLater()
		self.rulerView.deleteLater()
		
	def __del__( self ):
		self.deleteLater()

##----------------------------------------------------------------##
if __name__ == '__main__':
	import testView
