import sys
import math

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

TimelineForm,BaseClass = uic.loadUiType( _getModulePath('timeline.ui') )


##----------------------------------------------------------------##
_RULER_SIZE = 25
_TRACK_SIZE = 20


##----------------------------------------------------------------##
class TimelineRuler( QtGui.QFrame ):
	#BRUSHES
	_brushLine = QtGui.QBrush( QtGui.QColor.fromRgbF( 0,0,0 ) )

	#SIGNALS
	scrollPosChanged  = pyqtSignal( float )
	cursorPosChanged  = pyqtSignal( float )
	zoomChanged       = pyqtSignal( float )

	#BODY
	def __init__( self, *args ):
		super( TimelineRuler, self ).__init__( *args )
		self.setObjectName( 'TimelineRuler' )
		self.dragging = False
		self.dragFrom = None
		self.scrollPos = 0
		self.cursorPos = 0
		self.targetDragPos = 0
		self.zoom = 1
		self.setCursor( Qt.PointingHandCursor )
		self.setMinimumSize( 50, _RULER_SIZE )
		self.setMaximumSize( 16777215, _RULER_SIZE )
		self.grabbing = False

	def setScrollPos( self, pos ):
		p = max( pos, 0 )
		if p == self.scrollPos: return
		self.scrollPos = p
		self.update()
		self.scrollPosChanged.emit( p )

	def getScrollPos( self ):
		return self.scrollPos

	def setCursorPos( self, pos ):
		p = max( pos, 0 )
		if p == self.cursorPos: return
		self.cursorPos = p
		self.cursorPosChanged.emit( p )

	def getCursorPos( self ):
		return self.cursorPos

	def getPosAt( self, x ):
		return x/ self.zoom + self.scrollPos

	def setZoom( self, zoom = 1 ):
		zoom = max( zoom, 0.01 )
		if zoom == self.zoom: return
		self.zoom = zoom
		self.update()
		self.zoomChanged.emit( zoom )

	def getZoom( self ):
		return self.zoom

	def paintEvent( self, event ):
		painter = QtGui.QPainter()
		painter.begin( self )
		# painter.setBrush( TimelineRuler._brushLine )
		width  = self.width()
		height = self.height()
		zoom   = self.zoom
		scrollPos = self.scrollPos
		posStep = 100
		subStep = 20		
		posFrom = int( math.floor( scrollPos/posStep ) * posStep )
		posTo   = int( math.ceil ( (scrollPos + width/zoom )/posStep + 1 ) * posStep )
		for pos in range( posFrom, posTo, posStep ):
			x = ( pos - scrollPos ) * zoom
			rect = QRect( x + 3, 2, x+50, height )
			painter.drawLine( QPoint( x, 1 ), QPoint( x, height - 3 ) )
			painter.drawText( rect, QtCore.Qt.AlignLeft, '%.2f' % pos )
			for subPos in range( pos, pos + posStep, subStep ):
				x = ( subPos - scrollPos ) * zoom
				painter.drawLine( QPoint( x, height/4*3 ), QPoint( x, height - 3 ) )
		painter.end()

	def sizeHint( self ):
		return QSize( 100, 100 )

	def mousePressEvent(self, ev):
		if self.dragging: return
		button = ev.button()
		if button == Qt.LeftButton:
			self.grabMouse()
			self.dragging = 'scroll'
			self.setCursor( Qt.ClosedHandCursor )
			self.targetDragPos = self.scrollPos
			self.dragFrom = ev.x()
		elif button == Qt.RightButton:
			self.grabMouse()
			self.dragging = 'cursor'
			self.setCursorPos( self.getPosAt( ev.x() ) )

	def mouseReleaseEvent(self, ev):
		if not self.dragging: return
		self.releaseMouse()
		self.dragging = False
		self.setCursor( Qt.PointingHandCursor )
		button = ev.button()

	def mouseMoveEvent( self, ev ):
		if self.dragging:
			if self.dragging == 'scroll':
				delta = ev.x() - self.dragFrom
				self.dragFrom = ev.x()
				self.targetDragPos -= delta / self.zoom
				self.scrollPos = max( 0, self.targetDragPos )
				self.update()
				self.scrollPosChanged.emit( self.scrollPos )
			elif self.dragging == 'cursor':
				self.setCursorPos( self.getPosAt(ev.x()) )

	# def mouseDoubleClickEvent( self, ev ):

	def wheelEvent(self, event):
		steps = event.delta() / 120.0;
		dx = 0
		dy = 0
		zoomRate = 1.1
		if event.orientation() == Qt.Horizontal : 
			dx = steps
		else:
			dy = steps
			if dy>0:
				self.setZoom( self.zoom * zoomRate )
			else:
				self.setZoom( self.zoom / zoomRate )


##----------------------------------------------------------------##
class TimelineSpan( QtGui.QLabel ):
	posChanged     = pyqtSignal( object, float )
	lengthChanged  = pyqtSignal( object, float )
	clicked        = pyqtSignal( object, float )

	def __init__( self, *args ):
		super( TimelineSpan, self ).__init__( *args )
		self.length   = 100
		self.pos      = 0
		self.mouseOp  = None
		self.dragging = False
		self.dragFrom = 0
		# self.setFocusPolicy( QtCore.Qt.WheelFocus )
		self.setMouseTracking( True )
		self.setObjectName( 'TimelineSpan' )

	def setPos( self, pos ):
		pos = max( 0, pos )
		if pos == self.pos: return
		self.pos = pos 
		self.posChanged.emit( self, pos )

	def setLength( self, length ):
		length = max( 0, length )
		if length == self.length: return
		self.length = length
		self.lengthChanged.emit( self, length )

	def getStartPos( self ):
		return self.pos

	def getEndPos( self ):
		return self.pos + self.length

	def setSelected( self, selected = True ):
		selected = selected == True
		self.selected = selected
		self.setProperty( 'selected', selected and 'true' or 'false' )
		self.style().unpolish( self )
		self.style().polish( self )
		self.update()

	def mousePressEvent( self, ev ):
		button = ev.button()
		if button == Qt.LeftButton:
			self.dragging = True
			self.grabMouse()
			if self.mouseOp == 'move':
				self.setCursor( Qt.ClosedHandCursor )
			x = ev.globalPos().x()
			self.dragFrom = x
			self.clicked.emit( self, self.track.getPosAt( x ) )			

	def mouseReleaseEvent( self, ev ):
		button = ev.button()
		if button == Qt.LeftButton:
			self.dragging = False
			self.releaseMouse()
			if self.mouseOp == 'move':
				self.setCursor( Qt.OpenHandCursor )

	def mouseMoveEvent( self, ev ):
		if self.dragging:
			op = self.mouseOp
			zoom = self.parent().getZoom()
			x = ev.globalPos().x()
			delta = x - self.dragFrom
			self.dragFrom = x
			if op == 'move':
				self.setPos( self.pos + delta / zoom )
			elif op == 'left-size':
				oldLength = self.length
				newLength = max( 0, self.length - delta / zoom )
				newPos    = max( 0, self.pos - ( newLength - oldLength ) )
				actualLength = (self.pos + self.length ) - newPos
				self.setPos( newPos )
				self.setLength( actualLength )
			elif op == 'right-size':
				self.setLength( self.length + delta / zoom )
		else:
			#determine action
			x = ev.x()
			width = self.width()
			sizeHandle = max( 5, min( 20, width/5 ) )
			if x < sizeHandle:
				self.mouseOp = 'left-size'
				self.setCursor( Qt.SizeHorCursor )
			elif x > width-sizeHandle:
				self.mouseOp = 'right-size'
				self.setCursor( Qt.SizeHorCursor )
			else:
				self.mouseOp = 'move'
				self.setCursor( Qt.OpenHandCursor )

##----------------------------------------------------------------##
class TimelineTrack( QtGui.QFrame ):
	doubleClicked = pyqtSignal( object, float )

	def __init__( self, *args ):
		super( TimelineTrack, self ).__init__( *args )
		self.setObjectName( 'TimelineTrack' )
		self.scrollPos = 0
		self.zoom      = 1
		self.spans = []
		self.spanNodeDict = {}
		self.setMinimumSize( 80, _TRACK_SIZE )
		self.setMaximumSize( 16777215, _TRACK_SIZE )

	def sizeHint( self ):
		return QSize( 50, _TRACK_SIZE )

	def getHeader( self ):
		return self.header

	def getSpanByNode( self, node ):
		return self.spanNodeDict.get( node, None )

	def addSpan( self, node ):
		span = TimelineSpan( self )
		span.track = self
		self.spans.append( span )
		self.updateSpanShape( span )
		span.posChanged.connect( self.onSpanPosChanged )
		span.lengthChanged.connect( self.onSpanLengthChanged )		
		span.show()
		span.node = node
		self.spanNodeDict[ node ] = span
		return span

	def removeSpan( self, node ):
		span = self.spanNodeDict.get( node, None )
		if not span: return
		i = self.spans.index( span )
		span.setParent( None )
		del self.spans[i]
		del self.spanNodeDict[ node ]

	def clear( self ):
		for sp in self.spans:
			sp.setParent( None )
		self.spans = []
		self.spanNodeDict.clear()

	def setScrollPos( self, pos ):
		self.scrollPos = pos
		for span in self.spans:
			self.updateSpanShape( span )
		self.update()

	def getScrollPos( self ):
		return self.scrollPos

	def setZoom( self, zoom ):
		self.zoom = zoom
		for span in self.spans:
			self.updateSpanShape( span )
		self.update()

	def getZoom( self ):
		return self.zoom

	def updateSpanShape( self, span ):
		scrollPos = self.scrollPos
		zoom      = self.zoom
		width  = max( span.length * zoom, 12 )
		height = self.height() 
		x      = ( span.pos - scrollPos ) * zoom
		y      = 0
		span.setGeometry( x, y, width, height-1 )

	def resizeEvent( self, size ):
		for span in self.spans:
			self.updateSpanShape( span )		

	def onSpanPosChanged( self, span, pos ):
		self.updateSpanShape( span )

	def onSpanLengthChanged( self, span, zoom ):
		self.updateSpanShape( span )

	def getPosAt( self, x ):
		return self.timeline.getPosAt( x )

	def mouseDoubleClickEvent( self, ev ):
		pos = self.getPosAt( ev.x() )
		self.doubleClicked.emit( self, pos )

##----------------------------------------------------------------##
class TimelineTrackHeader( QtGui.QLabel ):
	def __init__( self, *args ):
		super( TimelineTrackHeader, self ).__init__( *args )
		self.setObjectName('TimelineTrackHeader')
		self.setMinimumSize( 80, _TRACK_SIZE )

##----------------------------------------------------------------##
class TimelineEventFilter(QObject):
	def eventFilter(self, obj, event):
		e = event.type()
		if e == QEvent.Wheel:
			obj.onWheelEvent( event )
			return False
		return QObject.eventFilter( self, obj, event )

##----------------------------------------------------------------##
class TimelineCursor( QtGui.QWidget ):
	pass

##----------------------------------------------------------------##	
class TimelineWidget( QtGui.QFrame ):
	spanSelectionChanged = pyqtSignal()
	trackDClicked        = pyqtSignal( object, float )
	def __init__( self, *args, **kwargs ):
		super(TimelineWidget, self).__init__( *args )
		self.tracks = []
		self.trackNodeDict = {}

		self.setObjectName( 'Timeline' )
		self.ui = TimelineForm()
		self.ui.setupUi( self )
		self.ui.containerLeft.setSizePolicy( QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed )

		self.setMouseTracking( True )
		self.ui.containerLT.setObjectName( 'TimelineToolBar' )
		containerRuler = self.ui.containerRuler
		self.ruler = ruler = TimelineRuler( containerRuler )
		containerRuler.setLayout( QtGui.QVBoxLayout() )
		containerRuler.layout().addWidget( ruler )
		containerRuler.layout().setSpacing( 2 )
		containerRuler.layout().setMargin( 0 )
		ruler.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Fixed
				)
		self.ruler.scrollPosChanged.connect( self.onScrollPosChanged )
		self.ruler.cursorPosChanged.connect( self.onCursorPosChanged )
		self.ruler.zoomChanged.connect( self.onZoomChanged )
		
		layout = QtGui.QVBoxLayout()
		layout.setSpacing( 0)
		layout.setMargin( 0 )
		self.ui.containerTracks.setLayout( layout )

		layout = QtGui.QVBoxLayout()
		layout.setSpacing( 0 )
		layout.setMargin( 0 )
		self.ui.containerHeaders.setLayout( layout )

		self.updating   = False
		self.rebuilding = False
		# self.installEventFilter( TimelineEventFilter( self ) )
		self.ui.mainSplitter.setObjectName('TimelineSplitter')
		self.ui.mainSplitter.setStretchFactor( 0, 0 )
		self.ui.mainSplitter.setStretchFactor( 1, 1 )

		self.ui.scrollTracks.resizeEvent = self.onScrollTracksResize
		self.ui.scrollHeaders.resizeEvent = self.onScrollTracksResize
		
		self.ui.scrollTracks.verticalScrollBar().valueChanged.connect( self.syncScrollBarToHeaders )
		self.ui.scrollHeaders.verticalScrollBar().valueChanged.connect( self.syncScrollBarToTracks )
		self.ui.scrollHeaders.verticalScrollBar().setStyleSheet('width:2px')
		
		self.timelineCursor = QtGui.QLabel( self.ui.containerRight )
		self.timelineCursor.setStyleSheet( 'background-color:#5c6; opacity: 80;' )
		self.updateScrollTrackSize()
		self.setCursorPos( 0 )

	def setZoom( self, zoom ):
		return self.ruler.setZoom( zoom )

	def getZoom( self ):
		return self.ruler.getZoom()

	def setPos( self, pos ):
		self.ruler.setScrollPos( pos )

	def getPos( self ):
		return self.ruler.getScrollPos()

	def getCursorPos( self ):
		return self.ruler.cursorPos

	def setCursorPos( self, pos ):
		self.ruler.setCursorPos( pos )

	def getPosAt( self, x ):
		zoom = self.getZoom()
		pos  = self.getPos()
		return x/zoom + pos

	def mapPos( self, pos ):
		zoom = self.getZoom()
		pos0 = self.getPos()
		return ( pos - pos0 ) * zoom

	def rebuild( self ):
		self.setUpdatesEnabled( False )
		self.clear()
		self.rebuilding = True
		for node in self.getTrackNodes():
			self.addTrack( node )
		self.updateScrollTrackSize()
		self.setUpdatesEnabled( True )
		self.rebuilding = False

	def clear( self ):		
		def _clearLayout( layout ):
			while layout.count() > 0:
				child = layout.takeAt( 0 )
				if child :
					w = child.widget()
					if w:
						w.setParent( None )
				else:
					break
		for t in self.tracks:
			t.clear()
		_clearLayout( self.ui.containerTracks.layout() )
		_clearLayout( self.ui.containerHeaders.layout() )
		self.tracks = []
		self.trackNodeDict.clear()
		self.updateScrollTrackSize()

	def getTrackByNode( self, node ):
		return self.trackNodeDict.get( node, None )

	def addTrack( self, node, **option ):
		assert not self.trackNodeDict.has_key( node )
		container       = self.ui.containerTracks
		containerHeader = self.ui.containerHeaders
		
		track = self.createTrack( node )
		track.timeline = self

		container.layout().addWidget( track )
		track.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Minimum
				)

		header = self.createTrackHeader( node )
		track.header = header
		containerHeader.layout().addWidget( header )
		header.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Minimum
				)
		track.doubleClicked.connect( self.onTrackDClicked )
		track.node = node
		self.trackNodeDict[ node ] = track
		self.tracks.append( track )
		self.updateTrackContent( track, node, **option )
		#add spans
		spanNodes = self.getSpanNodes( node )
		if spanNodes:
			for spanNode in spanNodes:
				self.addSpan( spanNode )
		if not self.rebuilding:
			self.updateScrollTrackSize()
		return track

	def removeTrack( self, trackNode ):
		track = self.getTrackNodes( trackNode )
		if not track: return
		i = self.tracks.index( track ) #excpetion catch?
		del self.tracks[i]
		del self.trackNodeDict[ track.node ]
		track.node = None
		track.clear()
		self.ui.containerHeaders.layout().removeWidget( track.header )
		self.ui.containerTracks.layout().removeWidget( track )
		track.setParent( None )
		track.header.setParent( None )
		self.updateScrollTrackSize()

	def addSpan( self, spanNode, **option ):
		track = self.getParentTrack( spanNode )
		if not track: return None
		span = track.addSpan( spanNode )
		if span:
			pos, length = self.getSpanParam( spanNode )
			span.setPos( pos )
			span.setLength( length )
			self.updateSpanContent( span, spanNode, **option )
		return span

	def removeSpan( self, spanNode ):
		track = self.getParentTrack( spanNode )
		if not track: return
		track.removeSpan( spanNode )

	def getParentTrack( self, spanNode ):
		trackNode = self.getParentTrackNode( spanNode )
		if not trackNode: return None
		return self.getTrackByNode( trackNode )

	def getSpanByNode( self, spanNode ):
		track = self.getParentTrack( spanNode )
		return track.getSpanByNode( spanNode )
	# def onWheelEvent(self, event):
	# 	steps = event.delta() / 120.0
	# 	dx = 0
	# 	dy = 0
	# 	zoomRate = 1.1
	# 	moveSpeed = 100
	# 	if event.orientation() == Qt.Horizontal : 
	# 		dx = steps
	# 	else:
	# 		dy = steps
	# 		if event.modifiers() & Qt.ControlModifier:
	# 			if dy>0:
	# 				self.setZoom( self.getZoom() * zoomRate )
	# 			else:
	# 				self.setZoom( self.getZoom() / zoomRate )
	# 		else:
	# 			self.setPos( self.getPos() - steps * moveSpeed / self.getZoom() )

	

	def updateTimelineCursor( self ):
		self.timelineCursor.move( self.mapPos( self.getCursorPos() ), 0 )

	def onCursorPosChanged( self, pos ):
		self.updateTimelineCursor()

	def onScrollPosChanged( self, pos ):
		if self.updating: return
		self.updating = True
		#sync widget pos
		self.ruler.setScrollPos( pos )
		for track in self.tracks:
			track.setScrollPos( pos )
		self.updateTimelineCursor()
		self.updating = False

	def onZoomChanged( self, zoom ):
		if self.updating: return
		self.updating = True
		#sync widget zoom
		self.ruler.setZoom( zoom )
		for track in self.tracks:
			track.setZoom( zoom )
		self.updateTimelineCursor()
		self.updating = False
	
	def calcTrackContainerHeight( self ):
		h = 0
		for track in self.tracks:
			size = track.size()
			h += size.height()
		h += 20
		return h

	def updateScrollTrackSize( self ):
		height = self.calcTrackContainerHeight()
		width  =  self.ui.scrollTracks.width()
		#
		self.ui.scrollTracksInner.resize( width, height )
		self.ui.scrollTracksInner.setMinimumSize( width - 10, height )
		self.ui.outterContainerTracks.resize( width, height )
		#
		width  =  self.ui.scrollHeaders.width()
		self.ui.scrollHeadersInner.resize( width, height )
		self.ui.scrollHeadersInner.setMinimumSize( width - 10, height )
		self.ui.outterContainerHeaders.resize( width, height )

		self.timelineCursor.resize( 1, height - 20 + 25 )
		self.timelineCursor.raise_()
		

	def onScrollTracksResize( self, ev ):
		self.updateScrollTrackSize()

	def syncScrollBarToHeaders( self, value ):
		self.ui.scrollHeaders.verticalScrollBar().setValue( value )

	def syncScrollBarToTracks( self, value ):
		self.ui.scrollTracks.verticalScrollBar().setValue( value )

	#####
	#VIRUTAL functions
	#####
	def updateTrackContent( self, track, node, **option ):
		pass

	def updateSpanContent( self, span, spanNode, **option ):
		pass

	def createSpan( self ):
		return TimelineSpan( )

	def createTrack( self, node ):
		return TimelineTrack( )

	def createTrackHeader( self, node ):
		return TimelineTrackHeader( )

	def getTrackNodes( self ):
		return []

	def getSpanNodes( self, node ):
		return []

	def getSpanParam( self, spanNode ):
		return ( 0, 10 )

	def getParentTrackNode( self, spanNode ):
		return None

	#######
	#Interaction
	#######
	def onTrackDClicked( self, track, pos ):
		pass


#TEST
if __name__ == '__main__':
	import test
	