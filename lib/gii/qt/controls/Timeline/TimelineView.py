# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform
from OpenGL.GL import *

import sys
import math

_USE_GL = True
_RULER_SIZE = 25
_TRACK_SIZE = 25
_TRACK_MARGIN = 3


_PaintingView = None


def makeBrush( **option ):
	brush = QtGui.QBrush()
	brush.setStyle( option.get( 'style', Qt.SolidPattern ) )
	color = QColor( option.get( 'color', '#ffffff' ) )
	color.setAlphaF( option.get( 'alpha', 1 ) )
	brush.setColor( color )
	return brush

def makePen( **option ):
	pen = QtGui.QPen()
	pen.setStyle( option.get( 'style', Qt.SolidLine ) )
	color = QColor( option.get( 'color', '#ffffff' ) )
	color.setAlphaF( option.get( 'alpha', 1 ) )
	pen.setColor( color )
	pen.setWidth( option.get( 'width', 1 ) )
	return pen

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

TimelineForm,BaseClass = uic.loadUiType( _getModulePath('timeline.ui') )

class GridBackground( QtGui.QGraphicsRectItem ):
	_gridPen  = makePen( color = '#212121', width = 1 )
	def __init__( self ):
		super( GridBackground, self ).__init__()
		self.setZValue( -100 )
		self.gridWidth = 50
		self.gridHeight = 50 

	def setGridSize( self, width, height = None ):
		if not height:
			height = width
		self.gridWidth = width
		self.gridHeight = height
		self.update()

	def paint( self, painter, option, widget ):
		painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
		rect = painter.viewport()
		transform = painter.transform()
		dx = transform.dx()
		dy = transform.dy()
		painter.setPen( GridBackground._gridPen )
		tw = self.gridWidth
		th = self.gridHeight
		w = rect.width()
		h = rect.height()
		rows = int( h/self.gridHeight ) + 1
		cols = int( w/self.gridWidth ) + 1
		x0 = -dx
		y0 = -dy
		x1 = x0 + w
		y1 = y0 + h
		ox = (dx) % tw
		oy = (dy) % th

		for col in range( cols ):
			x = col * tw + ox + x0
			painter.drawLine( x, y0, x, y1 )

		for row in range( rows ):
			y = row * th + oy + y0
			painter.drawLine( x0, y, x1, y )

class TimelineCursorLine( QtGui.QGraphicsLineItem ):
	_pen  = makePen( color = '#9cff00', width = 1 )
	def __init__( self ):
		super( TimelineCursorLine, self ).__init__()
		self.setPen( self._pen )

	def paint( self, painter, option, widget ):
		painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
		super( TimelineCursorLine, self ).paint( painter, option, widget )


class TimelineResizeHandle( QtGui.QGraphicsRectItem ):
	def __init__( self, parent, *args, **kwargs ):
		super( TimelineResizeHandle, self ).__init__( parent = parent )
		self.setFlag( self.ItemHasNoContents, True)
		self.setCursor( Qt.SizeHorCursor )
		self.dragging = False
		self.draggingFrom = None

	def mousePressEvent( self, event ):
		self.dragging = True
		self.draggingFrom = event.scenePos().x()
		self.parentItem().onResizeStart( self )

	def mouseReleaseEvent( self, event ):
		self.dragging = False
		self.parentItem().onResizeStop( self )

	def mouseMoveEvent( self, event ):
		if not self.dragging: return
		p0 = self.draggingFrom
		p1 = event.scenePos().x()
		diff = p1 - p0
		self.parentItem().onResize( self, diff )

class TimelineKeySpan( QtGui.QGraphicsRectItem ):
	_brush = makeBrush( color = '#dfd293' )
	_pen   = makePen( color = '#a67c53' )
	_penSelected = makePen( color = '#715443' )

	_handleWidth = 10
	def __init__( self, source, *args, **kwargs ):
		super( TimelineKeySpan, self ).__init__( parent = source.parentItem() )
		self.source = source
		self.width = 100
		self.setFlag( self.ItemIsSelectable, True )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.setCursor( Qt.PointingHandCursor )
		self.leftHandle = TimelineResizeHandle( self )
		self.RightHandle = TimelineResizeHandle( self )
		self.updateShape()
		self.setPos( 0,0 )	

	def updateShape( self ):
		spanHeight = _TRACK_SIZE - 4
		self.setRect( 0, 4, self.width, spanHeight )
		self.leftHandle.setRect( - TimelineKeySpan._handleWidth/2, 0, 10, spanHeight )
		self.RightHandle.setRect( self.width - TimelineKeySpan._handleWidth/2, 0, 10, spanHeight )

	def onResizeStart( self, handle ):
		self.width0 = self.width
		self.x0 = self.x()

	def onResizeStop( self, handle ):
		pass

	def onResize( self, handle, diff ):
		if handle == self.leftHandle:
			self.setX( self.x0 + diff )
			self.width = self.width0 - diff
			self.updateShape()
		else:
			self.width = self.width0 + diff
			self.updateShape()

	def paint( self, painter, option, widget ):
		rect = self.rect()
		if self.isSelected():
			painter.setBrush( TimelineKeySpan._brush )
			painter.setPen( TimelineKeySpan._penSelected )
		else:
			painter.setBrush( TimelineKeySpan._brush )
			painter.setPen( TimelineKeySpan._pen )
		painter.drawRect( rect.translated( 0, -1 ) )
		painter.drawText( rect.translated( 2, 0 ), Qt.AlignVCenter | Qt.AlignLeft, u"インビクタ腕時計 " )

class TimelineKey( QtGui.QGraphicsRectItem ):
	_polyMark = QtGui.QPolygonF([
			QPointF( -5, 0 ),
			QPointF( 5, 0 ),
			QPointF( 0, -10 ),
		]).translated( 0, _TRACK_SIZE )
	_brushMark =makeBrush( color = '#d599ff' )
	# _brushMark =makeBrush( color = '#ff60cc' )
	_penMark = makePen( color = '#c03745' )

	def __init__( self, parent, *args, **kwargs ):
		super( TimelineKey, self ).__init__( parent = parent )
		self.setRect( -10, 0, 20, _TRACK_SIZE)
		self.setZValue( 10 )
		self.setCursor( Qt.PointingHandCursor )
		self.setFlag( self.ItemIsSelectable, True )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.span = TimelineKeySpan( self )
		self.updateSpan()
		self.dragging = False

	def paint( self, painter, option, widget ):
		painter.setBrush( TimelineKey._brushMark )
		painter.setPen( TimelineKey._penMark )
		painter.drawPolygon( TimelineKey._polyMark )

	def itemChange( self, change, value ):
		if change == self.ItemPositionChange or change == self.ItemPositionHasChanged:
			self.updateSpan()
		return QtGui.QGraphicsRectItem.itemChange( self, change, value )

	def updateSpan( self ):
		self.span.setPos( self.pos() )

	def mousePressEvent( self, event ):
		x0 = self.pos().x()
		mx0 = event.scenePos().x()
		self.dragging = ( x0, mx0 )

	def mouseMoveEvent( self, event ):
		if self.dragging == False: return
		x0, mx0 = self.dragging
		mx1 = event.scenePos().x()
		x1 = x0 + mx1 - mx0
		self.setPos( x1, 0 )

	def mouseReleaseEvent( self, event ):
		self.dragging = None
		
class TimelineTrack( QtGui.QGraphicsRectItem ):
	def __init__( self, *args ):
		super(TimelineTrack, self).__init__( *args )
		self.index = 0
		self.keys = []
		self.zoom = 1
		key = TimelineKey( self )
		self.keys.append( key )

		key = TimelineKey( self )
		self.keys.append( key )

class TimelineScene( QtGui.QGraphicsScene ):

	def __init__( self, parent ):
		super( TimelineScene, self ).__init__( parent = parent )
		self.tracks = []
		
		self.cursorLine = TimelineCursorLine()
		self.cursorLine.setLine( 0,0, 0, 10000 )
		self.cursorLine.setZValue( 1000 )
		self.addItem( self.cursorLine )

		self.sceneRectChanged.connect( self.onRectChanged )
		self.gridBackground = GridBackground()
		self.gridBackground.setGridSize( 100, _TRACK_SIZE + _TRACK_MARGIN )
		self.addItem( self.gridBackground )

	def onRectChanged( self, rect ):
		self.gridBackground.setRect( rect )

	def addTrack( self ):
		track = TimelineTrack()
		self.addItem( track )
		self.tracks.append( track )
		track.index = len( self.tracks )
		track.setPos( 0, ( track.index - 1 ) * ( _TRACK_SIZE + _TRACK_MARGIN ) )
		return track

	def setCursorPos( self, pos ):
		self.cursorLine.setPos( pos, 0 )

	def removeTrack( self, track ):
		pass

class TimelineView( QtGui.QGraphicsView ):
	def __init__( self, *args, **kwargs ):
		super( TimelineView, self ).__init__( *args, **kwargs )
		self.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
		self.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
		self.setTransformationAnchor( self.NoAnchor )
		if _USE_GL:
			self.setViewportUpdateMode( QtGui.QGraphicsView.FullViewportUpdate )
			fmt = QtOpenGL.QGLFormat()
			fmt.setRgba(True)
			fmt.setAlpha(True)
			fmt.setDepth(False)
			fmt.setDoubleBuffer(True)
			fmt.setSwapInterval(0)
			fmt.setSampleBuffers( True )
			viewport = QtOpenGL.QGLWidget( QtOpenGL.QGLContext(fmt, None) )
			viewport.makeCurrent()
			# glEnable(GL_MULTISAMPLE)
			# glEnable(GL_LINE_SMOOTH)
			self.setViewport( viewport )
		self.setRenderHint( QtGui.QPainter.Antialiasing, True )
		self.setRenderHint( QtGui.QPainter.HighQualityAntialiasing, False )
			# self.setCacheMode( self.CacheBackground )
		self.scrollPos = 0
		self.scrollY = 0
		self.zoom = 1
		self.panning = False

	def setScrollPos( self, p, update = True ):
		self.scrollPos = p
		if update:
			self.updateTransfrom()
		# self.horizontalScrollBar().setValue( p )

	def setScrollY( self, y, update = True ):
		self.scrollY = y
		if update:
			self.updateTransfrom()

	def setZoom( self, zoom, update = True ):
		self.zoom = zoom
		if update:
			self.updateTransfrom()

	def updateTransfrom( self ):
		trans = QTransform()
		trans.translate( -self.scrollPos, self.scrollY )
		# trans.scale( self.zoom, self.zoom ) 
		self.setTransform( trans )

	def mouseMoveEvent( self, event ):
		super( TimelineView, self ).mouseMoveEvent( event )
		if self.panning:
			p1 = event.pos()
			p0, sp0, sy0 = self.panning
			dx = p1.x() - p0.x()
			dy = p1.y() - p0.y()
			sp1 = sp0 - dx
			sy1 = sy0 + dy
			self.setScrollPos( sp1, False )
			self.setScrollY( sy1, False )
			self.updateTransfrom()

	def mousePressEvent( self, event ):
		super( TimelineView, self ).mousePressEvent( event )
		if event.button() == Qt.MidButton:
			self.panning = ( event.pos(), self.scrollPos, self.scrollY )

	def mouseReleaseEvent( self, event ):
		super( TimelineView, self ).mouseReleaseEvent( event )
		if event.button() == Qt.MidButton :
			if self.panning:
				self.panning = False

	def wheelEvent( self, event ):
		pass

	def paintEvent( self, event ):
		global _PaintingView
		prevPainting = _PaintingView
		_PaintingView = self
		QtGui.QGraphicsView.paintEvent( self, event )
		_PaintingView = prevPainting


##----------------------------------------------------------------##
class TimelineRulerCursor( QtGui.QWidget ):
	def __init__( self, *args ):
		super( TimelineRulerCursor, self ).__init__( *args )
		self.setObjectName( 'TimelineCursor' )
		self.setFixedWidth( 1 )
		
	def paintEvent( self, ev ):
		painter = QtGui.QPainter( self )
		height    = self.height()
		painter.drawLine( QPoint( 0, 0 ), QPoint( 0, height ) )

	def setMode( self, mode ):
		self.setProperty( 'mode', mode )

##----------------------------------------------------------------##
class TimelineRuler( QtGui.QFrame ):
	#BRUSHES
	_brushLine = QtGui.QBrush( QtGui.QColor.fromRgbF( 0,0,0 ) )
	_cursorPen = makePen( color = '#9cff00', width = 1 )
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
		self.cursorDraggable = True
		# self.cursorWidget = TimelineRulerCursor( self )

	def setCursorDraggable( self, draggable = True ):
		self.cursorDraggable = draggable

	def setScrollPos( self, pos ):
		p = max( pos, 0 )
		if p == self.scrollPos: return
		self.scrollPos = p
		self.update()
		self.scrollPosChanged.emit( p )
		self.updateCursorWidget()

	def getScrollPos( self ):
		return self.scrollPos

	def getEndPos( self ):
		return self.getPosAt( self.width() )

	def setCursorPos( self, pos ):
		p = max( pos, 0 )
		if p == self.cursorPos: return
		self.cursorPos = p
		self.cursorPosChanged.emit( p )
		self.updateCursorWidget()
		self.update()

	def updateCursorWidget( self ):
		p = self.cursorPos
		x = ( p - self.scrollPos )*self.zoom
		# self.cursorWidget.move( x, 0 )

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
		cpos = ( self.cursorPos - scrollPos ) * zoom
		painter.setPen( self._cursorPen )
		painter.drawLine( cpos, 0, cpos, height )

	def sizeHint( self ):
		return QSize( 100, 100 )

	def mousePressEvent(self, ev):
		if self.dragging: return
		button = ev.button()
		if button == Qt.RightButton:
			self.grabMouse()
			self.dragging = 'scroll'
			self.setCursor( Qt.ClosedHandCursor )
			self.targetDragPos = self.scrollPos
			self.dragFrom = ev.x()
		elif button == Qt.LeftButton:
			if not self.cursorDraggable: return
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
				self.setScrollPos( max( 0, self.targetDragPos ) )				
			elif self.dragging == 'cursor':
				self.setCursorPos( self.getPosAt(ev.x()) )

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

class TimelineWidget( QtGui.QWidget ):
	keySelectionChanged   = pyqtSignal( object )
	trackSelectionChanged = pyqtSignal( object )
	keyPosChanged         = pyqtSignal( object, float )
	keyLengthChanged      = pyqtSignal( object, float )
	trackDClicked         = pyqtSignal( object, float )
	cursorPosChanged      = pyqtSignal( float )

	def __init__( self, *args, **kwargs ):
		super( TimelineWidget, self ).__init__( *args, **kwargs )		
		layout = QtGui.QVBoxLayout( self )
		layout.setSpacing( 1 )
		layout.setMargin( 20 )
		self.scene = TimelineScene( self )
		self.scene.setBackgroundBrush( makeBrush( color = '#111' ) );
		self.view = TimelineView( self.scene, parent = self )
		self.scene.setSceneRect( QRectF( 0,0, 10000, 10000 ) )
		self.view.setSceneRect( QRectF( 0,0, 10000, 10000 ) )
		self.ruler = TimelineRuler( self, 1 )
		self.ruler.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Fixed
				)
		layout.addWidget( self.view )
		layout.addWidget( self.ruler )
		self.ruler.scrollPosChanged.connect( self.onScrollPosChanged )
		self.ruler.cursorPosChanged.connect( self.onCursorPosChanged )
		self.ruler.zoomChanged.connect( self.onZoomChanged )		
		self.ruler.setFormatter( self.formatPos )
		self.updating = False

		self.scene.addTrack()
		self.scene.addTrack()
		self.scene.addTrack()

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

	def onCursorPosChanged( self, pos ):
		self.scene.setCursorPos( pos )
		# self.timelineCursor.move( self.mapPos( self.getCursorPos() ), 0 )

	def onScrollPosChanged( self, pos ):
		if self.updating: return
		self.updating = True
		self.view.setScrollPos( pos )
		self.updating = False

	def onZoomChanged( self, zoom ):
		if self.updating: return
		self.updating = True
		#sync widget zoom
		self.ruler.setZoom( zoom )
		self.view.setZoom( zoom )
		self.updating = False

	def formatPos( self, pos ):
		return '%.1f' % pos

	def __del__( self ):
		self.deleteLater()

if __name__ == '__main__':
	app = QtGui.QApplication( sys.argv )
	styleSheetName = 'gii.qss'
	app.setStyleSheet(
			open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
		)

	timeline = TimelineWidget()
	timeline.resize( 600, 300 )
	timeline.show()
	timeline.raise_()
	# timeline.setZoom( 10 )
	# timeline.selectTrack( dataset[1] )

	app.exec_()
