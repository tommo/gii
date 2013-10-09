import sys
import math
import random

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt, QObject, QEvent
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
	scrollPosChanged  = QtCore.pyqtSignal( float )
	zoomChanged       = QtCore.pyqtSignal( float )

	#BODY
	def __init__( self, *args ):
		super( TimelineRuler, self ).__init__( *args )
		self.setObjectName( 'TimelineRuler' )
		self.dragging = False
		self.dragFrom = None
		self.scrollPos = 0
		self.targetScrollPos = 0
		self.zoom = 1
		self.setCursor( Qt.PointingHandCursor )
		self.setMinimumSize( 50, _RULER_SIZE )
		self.setMaximumSize( 16777215, _RULER_SIZE )

	def setScrollPos( self, pos ):
		p = max( pos, 0 )
		if p == self.scrollPos: return
		self.scrollPos = p
		self.targetScrollPos = p
		self.update()
		self.scrollPosChanged.emit( p )

	def getScrollPos( self ):
		return self.scrollPos

	def getPosAt( self, x, y ):
		pass

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
			painter.drawLine( QPoint( x,0 ), QPoint( x, height - 3 ) )
			painter.drawText( rect, QtCore.Qt.AlignLeft, '%.2f' % pos )
			for subPos in range( pos, pos + posStep, subStep ):
				x = ( subPos - scrollPos ) * zoom
				painter.drawLine( QPoint( x, height/4*3 ), QPoint( x, height - 3 ) )
		painter.end()

	def sizeHint( self ):
		return QSize( 100, 100 )

	def mousePressEvent(self, ev):	
		button = ev.button()
		if button == Qt.LeftButton:
			self.grabMouse()
			self.dragging = True
			self.dragFrom = ev.x()
			self.setCursor( Qt.ClosedHandCursor )
			self.targetScrollPos = self.scrollPos

	def mouseReleaseEvent(self, ev):
		button = ev.button()
		if button == Qt.LeftButton:
			self.releaseMouse()
			self.dragging = False
			self.setCursor( Qt.PointingHandCursor )

	def mouseMoveEvent( self, ev ):
		if self.dragging:
			delta = ev.x() - self.dragFrom
			self.dragFrom = ev.x()
			self.targetScrollPos -= delta / self.zoom
			self.scrollPos = max( 0, self.targetScrollPos )
			self.update()
			self.scrollPosChanged.emit( self.scrollPos )

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
	posChanged     = QtCore.pyqtSignal( object, float )
	lengthChanged  = QtCore.pyqtSignal( object, float )

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

	def mousePressEvent( self, ev ):
		button = ev.button()
		if button == Qt.LeftButton:
			self.dragging = True
			self.grabMouse()
			if self.mouseOp == 'move':
				self.setCursor( Qt.ClosedHandCursor )
			x = ev.globalPos().x()
			self.dragFrom = x

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
	def __init__( self, *args ):
		super( TimelineTrack, self ).__init__( *args )
		self.setObjectName( 'TimelineTrack' )
		self.scrollPos = 0
		self.zoom      = 1
		self.spans = []
		self.setMinimumSize( 80, _TRACK_SIZE )
		self.setMaximumSize( 16777215, _TRACK_SIZE )

	def sizeHint( self ):
		return QSize( 50, _TRACK_SIZE )

	def addSpan( self, pos = 0, length = 100 ):
		span = TimelineSpan( self )
		# span.setText( 'span' )
		span.setPos( pos )
		span.setLength( length )
		self.spans.append( span )
		self.updateSpanShape( span )
		span.posChanged.connect( self.onSpanPosChanged )
		span.lengthChanged.connect( self.onSpanLengthChanged )
		return span

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
class TimelineWidget( QtGui.QFrame ):
	def __init__( self, *args, **kwargs ):
		super(TimelineWidget, self).__init__( *args )
		self.setObjectName( 'Timeline' )
		self.ui = TimelineForm()
		self.ui.setupUi( self )
		self.ui.containerLeft.setSizePolicy( QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed )
		self.tracks = []
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
		self.ruler.zoomChanged.connect( self.onZoomChanged )
		
		layout = QtGui.QVBoxLayout()
		layout.setSpacing( 0)
		layout.setMargin( 0 )
		self.ui.containerTracks.setLayout( layout )

		layout = QtGui.QVBoxLayout()
		layout.setSpacing( 0 )
		layout.setMargin( 0 )
		self.ui.containerHeaders.setLayout( layout )

		self.updating = False
		# self.installEventFilter( TimelineEventFilter( self ) )
		self.ui.mainSplitter.setObjectName('TimelineSplitter')
		self.ui.mainSplitter.setStretchFactor( 0, 0 )
		self.ui.mainSplitter.setStretchFactor( 1, 1 )

		self.ui.scrollTracks.resizeEvent = self.onScrollTracksResize
		self.ui.scrollHeaders.resizeEvent = self.onScrollTracksResize
		
		self.ui.scrollTracks.verticalScrollBar().valueChanged.connect( self.syncScrollBarToHeaders )
		self.ui.scrollHeaders.verticalScrollBar().valueChanged.connect( self.syncScrollBarToTracks )
		self.ui.scrollHeaders.verticalScrollBar().setStyleSheet('width:2px')

	def setZoom( self, zoom ):
		return self.ruler.setZoom( zoom )

	def getZoom( self ):
		return self.ruler.getZoom()

	def setPos( self, pos ):
		self.ruler.setScrollPos( pos )

	def getPos( self ):
		return self.ruler.getScrollPos()

	def addTrack( self, id, **option ):
		container       = self.ui.containerTracks
		containerHeader = self.ui.containerHeaders
		
		track = TimelineTrack( container )
		track.id = id

		container.layout().addWidget( track )
		track.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Minimum
				)
		self.tracks.append( track )

		header = TimelineTrackHeader( containerHeader )
		track.header = header
		containerHeader.layout().addWidget( header )
		header.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Minimum
				)

		header.setText( id )

		self.updateScrollTrackSize()
		return track

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

	def onScrollPosChanged( self, pos ):
		if self.updating: return
		self.updating = True
		#sync widget pos
		self.ruler.setScrollPos( pos )
		for track in self.tracks:
			track.setScrollPos( pos )
		self.updating = False

	def onZoomChanged( self, zoom ):
		if self.updating: return
		self.updating = True
		#sync widget zoom
		self.ruler.setZoom( zoom )
		for track in self.tracks:
			track.setZoom( zoom )
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

	def onScrollTracksResize( self, ev ):
		self.updateScrollTrackSize()

	def syncScrollBarToHeaders( self, value ):
		self.ui.scrollHeaders.verticalScrollBar().setValue( value )

	def syncScrollBarToTracks( self, value ):
		self.ui.scrollTracks.verticalScrollBar().setValue( value )

#TEST
if __name__ == '__main__':
	class TestFrame( QtGui.QWidget ):
		def __init__( self ):
			pass

	app = QtGui.QApplication( sys.argv )
	styleSheetName = 'xn.qss'
	app.setStyleSheet(
			open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
		)
	timeline = TimelineWidget()
	timeline.resize( 600, 300 )
	timeline.show()
	timeline.raise_()

	for i in range( 1, 30 ):
		t1 = timeline.addTrack( 'test-%d' % i )
		for s in range( 1, 3 ):
			span = t1.addSpan( random.random() * 1000, random.random() * 500 + 50 )
			span.setText( 'span-%d' % s )

	app.exec_()
			