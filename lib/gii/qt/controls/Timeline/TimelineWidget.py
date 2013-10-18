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
	def __init__( self, parent, scale ):
		super( TimelineRuler, self ).__init__( parent )
		self.setObjectName( 'TimelineRuler' )
		self.dragging = False
		self.dragFrom = None
		self.scrollPos = 0
		self.cursorPos = 0
		self.targetDragPos = 0
		self.scale = scale
		self.zoom  = 1
		self.setCursor( Qt.PointingHandCursor )
		self.setMinimumSize( 50, _RULER_SIZE )
		self.setMaximumSize( 16777215, _RULER_SIZE )
		self.grabbing = False
		self.formatter = self.defaultFormatter
		self.posStep = 1000
		self.subStep = 100

	def setScrollPos( self, pos ):
		p = max( pos, 0 )
		if p == self.scrollPos: return
		self.scrollPos = p
		self.update()
		self.scrollPosChanged.emit( p )

	def getScrollPos( self ):
		return self.scrollPos

	def getEndPos( self ):
		return self.getPosAt( self.width() )

	def setCursorPos( self, pos ):
		p = max( pos, 0 )
		if p == self.cursorPos: return
		self.cursorPos = p
		self.cursorPosChanged.emit( p )		

	def getCursorPos( self ):
		return self.cursorPos

	def getPosAt( self, x ):
		return x/ self.zoom  + self.scrollPos

	def setUnit( self, unit ):
		self.unit = unit

	def setFormatter( self, formatter ):
		self.formatter = formatter

	def defaultFormatter( self, pos ):
		return '%.1f' % pos

	def setZoom( self, zoom = 1 ):
		zoom = max( zoom, 0.01 )
		if zoom == self.zoom: return
		self.zoom = zoom
		self.update()
		self.zoomChanged.emit( zoom )

	def getZoom( self ):
		return self.zoom

	def paintEvent( self, event ):
		painter = QtGui.QPainter( self )
		# painter.setBrush( TimelineRuler._brushLine )
		formatter = self.formatter
		width     = self.width()
		height    = self.height()
		zoom      = self.zoom
		scrollPos = self.scrollPos
		posStep   = self.posStep
		subStep   = self.subStep
		posFrom   = int( math.floor( scrollPos/posStep ) * posStep )
		posTo     = int( math.ceil ( (scrollPos + width/zoom )/posStep + 1 ) * posStep )
		for pos in range( posFrom, posTo, posStep ):
			x = ( pos - scrollPos ) * zoom
			rect = QRect( x + 3, 2, x+50, height )
			painter.drawLine( QPoint( x, 1 ), QPoint( x, height - 3 ) )
			painter.drawText( rect, QtCore.Qt.AlignLeft, formatter( pos ) )
			for subPos in range( pos, pos + posStep, subStep ):
				x = ( subPos - scrollPos ) * zoom
				painter.drawLine( QPoint( x, height/4*3 ), QPoint( x, height - 3 ) )

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
class TimelineSpan( QtGui.QWidget ):
	posChanged     = pyqtSignal( object, float )
	lengthChanged  = pyqtSignal( object, float )
	clicked        = pyqtSignal( object, float )

	def __init__( self, track, *args, **option ):
		super( TimelineSpan, self ).__init__( track )
		self.length    = 100
		self.pos       = 0
		self.spanWidth = 1
		self.mouseOp   = None
		self.dragging  = False
		self.dragFrom  = 0
		self.track     = track
		self.text      = 'goo'
		self.resizable = option.get( 'resizable', True )
		# self.setFocusPolicy( QtCore.Qt.WheelFocus )
		self.setMouseTracking( True )
		self.setObjectName( 'TimelineSpan' )

	def setText( self, text ):
		self.text = text
		tw = self.fontMetrics().width( self.text )
		self.resize( max( self.width(), tw + 10 ) , self.height() )
		self.update()

	def setPos( self, pos ):
		pos = self.track.correctSpanPos( self, self.pos, pos )
		if pos == self.pos: return
		self.pos = pos 
		self.posChanged.emit( self, pos )

	def setLength( self, length ):
		length = max( 0, length )
		if length == self.length: return
		self.length = length
		self.lengthChanged.emit( self, length )

	def setShape( self, x, y, w, h ):
		self.spanWidth = w
		tw = self.fontMetrics().width( self.text )
		self.setGeometry( x, y, max( w, tw + 10 ) , h )

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

	def paintEvent( self, ev ):
		p = QtGui.QStylePainter( self )
		opt = QtGui.QStyleOptionButton()
		opt.init( self )
		h  = self.height()
		tw = self.fontMetrics().width( self.text )

		if self.spanWidth>=8:
			opt.rect= QtCore.QRect( 0,0,self.spanWidth,h )
			p.drawControl( QtGui.QStyle.CE_PushButton, opt )
			p.drawText( QtCore.QRect( 3,2,tw+10,h-2 ) , QtCore.Qt.AlignLeft, self.text )
		else:
			opt.rect = QtCore.QRect( 0, 0, 5, h )
			p.drawControl( QtGui.QStyle.CE_PushButton, opt )
			p.drawText( QtCore.QRect( 9,2,tw+10,h-2 ) , QtCore.Qt.AlignLeft, self.text )

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
				right     = self.pos + self.length
				self.setPos( newPos )
				actualLength = right - self.pos
				self.setLength( actualLength )
			elif op == 'right-size':
				newLength = self.track.correctSpanLength( self, self.length + delta / zoom  )
				self.setLength( newLength )
		else:
			#determine action
			if self.resizable:
				x = ev.x()
				width = self.width()
				sizeHandle = max( 5, min( 12, width/5 ) )
				if x < sizeHandle:
					self.mouseOp = 'left-size'
					self.setCursor( Qt.SizeHorCursor )
					return
				elif x > width-sizeHandle:
					self.mouseOp = 'right-size'
					self.setCursor( Qt.SizeHorCursor )
					return
			self.mouseOp = 'move'
			self.setCursor( Qt.OpenHandCursor )

##----------------------------------------------------------------##
class TimelineTrack( QtGui.QFrame ):
	doubleClicked      = pyqtSignal( object, float )
	clicked            = pyqtSignal( object, float )
	headerClicked      = pyqtSignal( object, object )
	spanClicked        = pyqtSignal( object, float )
	spanPosChanged     = pyqtSignal( object, float )
	spanLengthChanged  = pyqtSignal( object, float )

	def __init__( self, *args, **option ):
		super( TimelineTrack, self ).__init__( *args )
		self.setObjectName( 'TimelineTrack' )
		self.scrollPos = 0
		self.zoom      = 1
		self.spans = []
		self.spanNodeDict = {}
		self.setMinimumSize( 80, _TRACK_SIZE )
		self.setMaximumSize( 16777215, _TRACK_SIZE )
		self.allowOverlap = option.get( 'allow_overlap', False )

	def sizeHint( self ):
		return QSize( 50, _TRACK_SIZE )

	def setHeader( self, header ):
		self.header = header
		header.clicked.connect( self.onHeaderClicked )
		maxSize  = self.maximumSize()
		minSize  = self.minimumSize()
		maxSize0 = header.maximumSize()
		minSize0 = header.minimumSize()
		header.setMinimumSize( minSize0.width(), minSize.height() )
		header.setMaximumSize( maxSize0.width(), maxSize.height() )

	def getHeader( self ):
		return self.header

	def getSpanByNode( self, node ):
		return self.spanNodeDict.get( node, None )

	def correctSpanPos( self, span, oldPos, pos ):
		delta = pos - oldPos
		left  = pos
		right = pos + span.length
		if delta > 0:
			for span1 in self.spans:
				if span1==span: continue				
				if span1.pos >= right: continue
				if span1.pos + span1.length <= left: continue
				right = min( right, span1.pos )
			return right - span.length
		elif delta < 0:
			for span1 in self.spans:
				if span1==span: continue
				if span1.pos >= right: continue
				if span1.pos + span1.length <= left: continue
				left = max( left, span1.pos + span1.length )
			return max( 0, left )
		return pos

	def correctSpanLength( self, span, length ):
		oldLength = span.length
		delta = length - oldLength
		if delta == 0: return length
		pos = span.pos
		right = pos + length
		for span1 in self.spans:
			if span1==span: continue
			if span1.pos >= right: continue			
			if span1.pos + span1.length < right: continue			
			right = min( right, span1.pos )
		return right - pos

	def addSpan( self, node, **option ):
		span = TimelineSpan( self, option )
		self.spans.append( span )
		self.updateSpanShape( span )
		span.posChanged.connect( self.onSpanPosChanged )
		span.lengthChanged.connect( self.onSpanLengthChanged )		
		span.clicked.connect( self.spanClicked )
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
		width  = max( span.length * zoom, 1 )
		height = self.height() 
		x      = ( span.pos - scrollPos ) * zoom
		y      = 0
		span.setShape( x, y, width + 1, height-1 )

	def resizeEvent( self, size ):
		for span in self.spans:
			self.updateSpanShape( span )		

	def onSpanPosChanged( self, span, pos ):
		self.updateSpanShape( span )
		self.spanPosChanged.emit( span, pos )

	def onSpanLengthChanged( self, span, length ):
		self.updateSpanShape( span )
		self.spanLengthChanged.emit( span, length )

	def getPosAt( self, x ):
		return self.timeline.getPosAt( x )

	def mouseDoubleClickEvent( self, ev ):
		pos = self.getPosAt( ev.x() )
		self.doubleClicked.emit( self, pos )

	def mousePressEvent( self, ev ):
		pos = self.getPosAt( ev.x() )
		self.clicked.emit( self, pos )

	def setSelected( self, selected = True ):
		self.setProperty( 'selected', selected )
		self.style().unpolish( self )
		self.style().polish( self )
		self.update()
		header = self.header
		header.setProperty( 'selected', selected )
		header.style().unpolish( header )
		header.style().polish( header )
		header.update()

	def onHeaderClicked( self, header ):
		self.headerClicked.emit( self, header )

##----------------------------------------------------------------##
class TimelineTrackHeader( QtGui.QFrame ):
	clicked = pyqtSignal( object )
	def __init__( self, *args ):
		super( TimelineTrackHeader, self ).__init__( *args )
		self.setObjectName('TimelineTrackHeader')
		self.setMinimumSize( 80, _TRACK_SIZE )
		self.setMouseTracking( True )

	def mousePressEvent( self, ev ):
		self.clicked.emit( self )

	def setIcon( self, icon ):
		self.icon = icon

	def setText( self, text):
		self.text = text
		self.update()

	def paintEvent( self, ev ):
		p = QtGui.QStylePainter( self )
		if self.icon:
			self.icon.paint( p, QtCore.QRect( 3,3,14,14 ) )
		p.drawText( self.contentsRect().adjusted( 22, 2,-22, -2 ), QtCore.Qt.AlignLeft, self.text )

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
	spanSelectionChanged  = pyqtSignal( object )
	trackSelectionChanged = pyqtSignal( object )
	spanPosChanged        = pyqtSignal( object, float )
	spanLengthChanged     = pyqtSignal( object, float )
	trackDClicked         = pyqtSignal( object, float )

	def __init__( self, *args, **option ):
		super(TimelineWidget, self).__init__( *args )
		self.scale  = option.get( 'scale', 1 )

		self.tracks = []
		self.trackNodeDict = {}

		self.setObjectName( 'Timeline' )
		self.ui = TimelineForm()
		self.ui.setupUi( self )
		self.ui.containerLeft.setSizePolicy( QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed )

		self.setMouseTracking( True )
		self.ui.containerLT.setObjectName( 'TimelineToolBar' )
		containerRuler = self.ui.containerRuler
		self.ruler = ruler = TimelineRuler( containerRuler, self.scale )
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
		self.ruler.setFormatter( self.formatPos )
		
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
		self.timelineCursor.setStyleSheet( 
			'''
			QLabel{
				background-color:#5c6; width:1px;
			}

			QLabel::disabled{
				background-color:#222; width:0px;
			}
			'''
			)
		self.updateScrollTrackSize()
		self.setCursorPos( 0 )

		self.selectedTrack = None
		self.selectedSpan  = None
		
		rulerParam  = self.getRulerParam()
		self.ruler.posStep = rulerParam.get( 'step', 1000 )
		self.ruler.subStep = rulerParam.get( 'sub_step', 100 )
		self.onZoomChanged( rulerParam.get( 'zoom', 1 ) )

	def setZoom( self, zoom ):
		self.ruler.setZoom( zoom )

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
		p0 = self.getPos()
		p1 = self.ruler.getEndPos()
		if pos>p1 or pos<p0:
			self.setPos( pos )

	def getPosAt( self, x ):
		zoom = self.getZoom()
		pos  = self.getPos()
		return x/zoom + pos

	def mapPos( self, pos ):
		zoom = self.getZoom()
		pos0 = self.getPos()
		return ( pos - pos0 ) * zoom

	def rebuild( self ):
		self.clear()
		self.hide()
		self.rebuilding = True
		for node in self.getTrackNodes():
			self.addTrack( node )
		self.updateScrollTrackSize()
		self.rebuilding = False
		self.show()

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
		self.hide()
		for t in self.tracks:
			t.clear()
		_clearLayout( self.ui.containerTracks.layout() )
		_clearLayout( self.ui.containerHeaders.layout() )
		self.tracks = []
		self.trackNodeDict.clear()
		self.updateScrollTrackSize()
		self.show()
		
	def getTrackByNode( self, node ):
		return self.trackNodeDict.get( node, None )

	def addTrack( self, node, **option ):
		assert not self.trackNodeDict.has_key( node )
		container       = self.ui.containerTracks
		containerHeader = self.ui.containerHeaders
		
		track = self.createTrack( node )
		track.timeline = self
		track.setHeader( self.createTrackHeader( node ) )
		track.setZoom( self.getZoom() )
		track.setScrollPos( self.getPos() )

		container.layout().addWidget( track )
		track.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Minimum
				)

		header = track.getHeader()		
		containerHeader.layout().addWidget( header )
		header.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Minimum
				)
		track.node = node
		self.trackNodeDict[ node ] = track
		self.tracks.append( track )
		self.refreshTrack( node, **option )
		#add spans
		spanNodes = self.getSpanNodes( node )
		if spanNodes:
			for spanNode in spanNodes:
				self.addSpan( spanNode )
		if not self.rebuilding:
			self.updateScrollTrackSize()

		track.spanPosChanged.connect    ( self.spanPosChanged )
		track.spanLengthChanged.connect ( self.spanLengthChanged )

		track.doubleClicked.connect     ( self.onTrackDClicked )
		track.headerClicked.connect     ( self.onTrackHeaderClicked )
		track.clicked.connect           ( self.onTrackClicked )
		track.spanClicked.connect       ( self.onSpanClicked )
		
		return track

	def removeTrack( self, trackNode ):
		track = self.getTrackByNode( trackNode )
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
			self.refreshSpan( spanNode, **option )			
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
		return track and track.getSpanByNode( spanNode ) or None

	def selectTrack( self, trackNode ):
		track = self.getTrackByNode( trackNode )
		if self.selectedTrack == track: return
		if self.selectedTrack: 
			self.selectedTrack.setSelected( False )
			if self.selectedSpan:
				self.selectedSpan.setSelected( False )
				self.selectedSpan = None
		self.selectedTrack = track
		track.setSelected( True )
		self.trackSelectionChanged.emit( trackNode )
		self.spanSelectionChanged.emit( None )

	def selectSpan( self, spanNode ):
		span = self.getSpanByNode( spanNode )
		if span == self.selectedSpan: return
		if self.selectedSpan:
			self.selectedSpan.setSelected( False )
			self.selectedSpan = None
		if span:
			track = span.track
			self.selectTrack( track.node )			
			span.setSelected( True )
			self.selectedSpan = span
			self.spanSelectionChanged.emit( spanNode )
		else:
			self.spanSelectionChanged.emit( None )

	def getSelectedTrack( self ):
		return self.selectedTrack

	def getSelectedSpan( self ):
		return self.selectedSpan
	
	def getSelectedTrackNode( self ):
		track = self.selectedTrack
		return track and track.node or None

	def getSelectedSpan( self ):
		span = self.selectedSpan
		return span and span.node or None
	
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
	
	def refreshSpan( self, spanNode, **option ):
		span = self.getSpanByNode( spanNode )
		if span:
			pos, length, resizable = self.getSpanParam( spanNode )
			span.setPos( pos )
			span.setLength( length )
			span.resizable = resizable
			self.updateSpanContent( span, spanNode, **option )

	def refreshTrack( self, trackNode, **option ):
		track = self.getTrackByNode( trackNode )
		if track:
			self.updateTrackContent( track, trackNode, **option )

	def onScrollTracksResize( self, ev ):
		self.updateScrollTrackSize()

	def syncScrollBarToHeaders( self, value ):
		self.ui.scrollHeaders.verticalScrollBar().setValue( value )

	def syncScrollBarToTracks( self, value ):
		self.ui.scrollTracks.verticalScrollBar().setValue( value )

	def getRulerParam( self ):
		return {}

	#####
	#VIRUTAL functions
	#####
	def formatPos( self, pos ):
		return '%.1f' % pos

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
		return ( 0, 10, True )

	def getParentTrackNode( self, spanNode ):
		return None

	#######
	#Interaction
	#######
	def onTrackClicked( self, track, pos ):
		self.selectTrack( track.node )

	def onTrackHeaderClicked( self, track, header ):
		self.selectTrack( track.node )

	def onTrackDClicked( self, track, pos ):
		pass

	def onSpanClicked( self, span, pos ):
		self.selectSpan( span.node )

#TEST
if __name__ == '__main__':
	import test
	