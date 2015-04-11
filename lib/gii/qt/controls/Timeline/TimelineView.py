# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform
from OpenGL.GL import *


from GraphicsViewHelper import *

import sys
import math

_USE_GL = True
_RULER_SIZE = 25
_TRACK_SIZE = 20
_TRACK_MARGIN = 3
_PIXEL_PER_SECOND = 100.0 #basic scale
_HEAD_OFFSET = 15

_PaintingView = None

##----------------------------------------------------------------##
_DEFAULT_BG = makeBrush( color = '#222' )

##----------------------------------------------------------------##
##styles:  ID                     Pen           Brush          Text
makeStyle( 'black',              '#000000',    '#000000'              )
makeStyle( 'default',            '#000000',    '#ff0ecf'              )
makeStyle( 'key',                '#000000',    '#acbcff'              )
makeStyle( 'key:hover',          '#dfecff',    '#acbcff'              )
makeStyle( 'key:selected',       '#ffffff',    '#a0ff00'              )
makeStyle( 'key-span',           '#000000',    '#303459'    ,'#c2c2c2' )
makeStyle( 'key-span:selected',  '#ffffff',    '#303459'               )


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

TimelineForm,BaseClass = uic.loadUiType( _getModulePath('timeline2.ui') )

##----------------------------------------------------------------##
class TimelineCursorLine( QtGui.QGraphicsLineItem ):
	_pen  = makePen( color = '#9cff00', width = 1 )
	def __init__( self ):
		super( TimelineCursorLine, self ).__init__()
		self.setPen( self._pen )

	def paint( self, painter, option, widget ):
		painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
		super( TimelineCursorLine, self ).paint( painter, option, widget )

##----------------------------------------------------------------##
class TimelineKeyResizeHandle( QtGui.QGraphicsRectItem ):
	def __init__( self, parent, *args, **kwargs ):
		super( TimelineKeyResizeHandle, self ).__init__( parent = parent )
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

##----------------------------------------------------------------##
class TimelineKeySpanItem( QtGui.QGraphicsRectItem, StyledItemMixin ):
	_handleWidth = 10
	def __init__( self, key, *args, **kwargs ):
		super( TimelineKeySpanItem, self ).__init__( parent = key.parentItem() )
		self.key = key
		self.width = 100
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.setCursor( Qt.PointingHandCursor )
		self.leftHandle = TimelineKeyResizeHandle( self )
		# self.RightHandle = TimelineKeyResizeHandle( self )
		self.setItemType( 'key-span' )
		self.setItemState( 'normal' )

	def updateShape( self ):
		spanHeight = _TRACK_SIZE - 2
		self.width = self.key.timeToPos( self.key.timeLength )
		self.setRect( 0, (_TRACK_SIZE - spanHeight)/2 + 1, self.width, spanHeight )
		self.leftHandle.setRect( - TimelineKeySpanItem._handleWidth/2, 0, 10, spanHeight )
		# self.RightHandle.setRect( self.width - TimelineKeySpanItem._handleWidth/2, 0, 10, spanHeight )

	def onResizeStart( self, handle ):
		self.width0 = self.width
		self.x0 = self.x()

	def onResizeStop( self, handle ):
		pass

	def onResize( self, handle, diff ):
		if handle == self.leftHandle:
			self.setX( self.x0 + diff )
			self.width = self.width0 - diff
		else:
			self.width = self.width0 + diff
		self.key.setTimeLength( self.key.posToTime( self.width ) )

	def onPaint( self, painter, option, widget ):
		rect = self.rect()
		painter.drawRect( rect.translated( 0, -1 ) )
		painter.drawStyledText( rect.translated( 4, 2 ), Qt.AlignTop | Qt.AlignLeft, self.key.getLabel() )

	def mousePressEvent( self, event ):
		self.key.mousePressEvent( event )

	def mouseMoveEvent( self, event ):
		self.key.mouseMoveEvent( event )

	def mouseReleaseEvent( self, event ):
		self.key.mouseReleaseEvent( event )

##----------------------------------------------------------------##
class TimelineKeyItem( QtGui.QGraphicsRectItem, StyledItemMixin ):
	_polyMark = QtGui.QPolygonF([
			QPointF( -0, 0 ),
			QPointF( 10, 0 ),
			QPointF( 0, -10 ),
		]).translated( 0, _TRACK_SIZE )

	def __init__( self, parent, *args, **kwargs ):
		super( TimelineKeyItem, self ).__init__( parent = parent )
		self.setRect( -10, 0, 20, _TRACK_SIZE)
		self.setZValue( 10 )
		self.setCursor( Qt.PointingHandCursor )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.setAcceptHoverEvents( True )

		self.dragging = False
		self.setItemType( 'key' )
		self.setItemState( 'normal' )
		self.timePos    = 0
		self.timeLength = 0
		self.updatingPos = False
		self.span = TimelineKeySpanItem( self )
		self.span.hide()
		self.track = False

	def onPaint( self, painter, option, widget ):
		rect = self.rect()
		painter.drawRect( QRectF( 0,0,4, rect.height() ) )
		# painter.drawPolygon( TimelineKeyItem._polyMark )

	def getTrack( self ):
		return self.track

	def itemChange( self, change, value ):
		if change == self.ItemPositionChange or change == self.ItemPositionHasChanged:
			self.updateSpan()
			if not self.updatingPos:
				self.updatingPos = True
				tpos = self.posToTime( self.x() )
				self.setTimePos( tpos )
				self.updatingPos = False
		return QtGui.QGraphicsRectItem.itemChange( self, change, value )

	def delete( self ):
		scn = self.scene()
		scn.removeItem( self )

	def updateSpan( self ):
		self.span.setPos( self.pos() )

	def hoverEnterEvent( self, event ):
		self.setItemState( 'hover' )
		self.track.view.update()

	def hoverLeaveEvent( self, event ):
		self.setItemState( 'normal' )
		self.track.view.update()

	def mousePressEvent( self, event ):
		if event.button() == Qt.LeftButton:
			x0 = self.pos().x()
			mx0 = event.scenePos().x()
			self.dragging = ( x0, mx0 )

	def mouseMoveEvent( self, event ):
		if self.dragging == False: return
		x0, mx0 = self.dragging
		mx1 = event.scenePos().x()
		x1 = x0 + mx1 - mx0
		self.setPos( max( x1, _HEAD_OFFSET ), 0 )

	def mouseReleaseEvent( self, event ):
		if event.button() == Qt.LeftButton:
			self.dragging = False

	def timeToPos( self, t ):
		return self.track.timeToPos( t )

	def posToTime( self, t ):
		return self.track.posToTime( t )

	def updateShape( self ):
		self.setTimePos( self.timePos )
		self.span.updateShape()

	def setTimePos( self, tpos ):
		tpos = max( 0, tpos )
		self.timePos = tpos
		x = self.timeToPos( tpos )
		if not self.updatingPos:
			self.updatingPos = True
			self.setX( x )
			self.updatingPos = False

	def getTimePos( self ):
		return self.timePos

	def setTimeLength( self, l ):
		self.timeLength = max( l, 0 )
		if self.timeLength > 0:
			self.span.updateShape()
			self.span.show()
		else:
			self.span.hide()

	def getTimeLength( self ):
		return self.timeLength

	def getLabel( self ):
		return 'Time:%.2f' % self.timePos
		
##----------------------------------------------------------------##
class TimelineTrackItem( QtGui.QGraphicsRectItem ):
	def __init__( self, *args ):
		super(TimelineTrackItem, self).__init__( *args )
		self.index = 0
		self.keys = []
		self.zoom = 1		

	def addKey( self ):
		key = TimelineKeyItem( self )
		key.track = self
		self.keys.append( key )
		key.updateShape()
		return key

	def clear( self ):
		keys = self.keys[:]
		for key in keys:
			key.delete()

	def setZoom( self, zoom ):
		self.zoom = zoom
		for key in self.keys:
			key.updateShape()

	def timeToPos( self, t ):
		return self.view.timeToPos( t )

	def posToTime( self, p ):
		return self.view.posToTime( p )

##----------------------------------------------------------------##
class TimelineHeaderView( GLGraphicsView ):
	scrollYChanged  = pyqtSignal( float )
	def __init__( self, *args, **kwargs ):
		super( TimelineHeaderView, self ).__init__( *args, **kwargs )
		self.scene = QtGui.QGraphicsScene( self )
		self.scene.setBackgroundBrush( _DEFAULT_BG );
		self.scene.setSceneRect( QRectF( 0,0, 10000, 10000 ) )
		self.setScene( self.scene )
		self.scrollY = 0
		self.updatingScrollY = False
		button = QtGui.QPushButton()
		button.setFixedWidth( 300 )
		self.scene.addWidget( button )
		button.setText( 'hello, graphics button' )
		self.scene.sceneRectChanged.connect( self.onRectChanged )

	def setScrollY( self, y, update = True ):
		self.scrollY = y
		if self.updatingScrollY: return
		self.updatingScrollY = True
		self.scrollYChanged.emit( self.scrollY )
		if update:
			self.updateTransfrom()
		self.updatingScrollY = False

	def updateTransfrom( self ):
		trans = QTransform()
		trans.translate( 0, self.scrollY )
		self.setTransform( trans )

	def onRectChanged( self ):
		pass

	def wheelEvent(self, event):
		pass

##----------------------------------------------------------------##
class TimelineView( GLGraphicsView ):
	scrollYChanged  = pyqtSignal( float )
	def __init__( self, *args, **kwargs ):
		super( TimelineView, self ).__init__( *args, **kwargs )
		
		self.gridSize  = 100
		self.scrollPos = 0
		self.scrollY   = 0
		self.zoom      = 1
		self.panning   = False
		self.updatingScrollY = False

		self.scene = QtGui.QGraphicsScene( self )
		self.scene.setBackgroundBrush( _DEFAULT_BG );
		self.setScene( self.scene )
		self.scene.sceneRectChanged.connect( self.onRectChanged )

		self.tracks = []
		
		#components
		self.cursorLine = TimelineCursorLine()
		self.cursorLine.setLine( 0,0, 0, 10000 )
		self.cursorLine.setZValue( 1000 )
		self.scene.addItem( self.cursorLine )
		#grid
		self.gridBackground = GridBackground()
		self.gridBackground.setGridSize( self.gridSize, _TRACK_SIZE + _TRACK_MARGIN )
		self.gridBackground.setOffset( _HEAD_OFFSET, -1 )
		self.scene.addItem( self.gridBackground )

		self.scene.setSceneRect( QRectF( 0,0, 10000, 10000 ) )

	def addTrack( self ):
		track = TimelineTrackItem()
		track.view = self
		self.scene.addItem( track )
		self.tracks.append( track )
		track.index = len( self.tracks )
		track.setPos( 0, ( track.index - 1 ) * ( _TRACK_SIZE + _TRACK_MARGIN ) )
		return track

	def removeTrack( self, track ):
		pass

	def setCursorPos( self, pos ):
		self.cursorLine.setPos( self.timeToPos( pos ), 0 )

	def setScrollPos( self, p, update = True ):
		p = max( p, 0 )
		if self.scrollPos == p: return
		self.scrollPos = p
		if update:
			self.updateTransfrom()

	def setScrollY( self, y, update = True ):
		self.scrollY = y
		if self.updatingScrollY: return
		self.updatingScrollY = True
		self.scrollYChanged.emit( self.scrollY )
		if update:
			self.updateTransfrom()
		self.updatingScrollY = False

	def setZoom( self, zoom, update = True ):
		self.zoom = zoom
		if update:
			self.updateTransfrom()
			for track in self.tracks:
				track.setZoom( self.zoom )
			self.gridBackground.setGridWidth( self.gridSize * zoom )

	def timeToPos( self, t ):
		return t * self.zoom * _PIXEL_PER_SECOND + _HEAD_OFFSET

	def posToTime( self, p ):
		return ( p - _HEAD_OFFSET ) / ( self.zoom * _PIXEL_PER_SECOND )

	def updateTransfrom( self ):
		trans = QTransform()
		sx = - self.timeToPos( self.scrollPos ) + _HEAD_OFFSET
		trans.translate( sx, self.scrollY )
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
			self.setScrollPos( self.posToTime( sp1 ), True )
			self.setScrollY( sy1, False )
			self.updateTransfrom()

	def mousePressEvent( self, event ):
		super( TimelineView, self ).mousePressEvent( event )
		if event.button() == Qt.MidButton:
			self.panning = ( event.pos(), self.timeToPos( self.scrollPos ), self.scrollY )
			self.setCursor( Qt.ClosedHandCursor )

	def mouseReleaseEvent( self, event ):
		super( TimelineView, self ).mouseReleaseEvent( event )
		if event.button() == Qt.MidButton :
			if self.panning:
				self.panning = False
				self.setCursor( Qt.ArrowCursor )

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

	def paintEvent( self, event ):
		global _PaintingView
		prevPainting = _PaintingView
		_PaintingView = self
		QtGui.QGraphicsView.paintEvent( self, event )
		_PaintingView = prevPainting

	def onRectChanged( self, rect ):
		self.gridBackground.setRect( rect )

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

##----------------------------------------------------------------##
class TimelineWidget( QtGui.QWidget ):
	keySelectionChanged   = pyqtSignal( object )
	trackSelectionChanged = pyqtSignal( object )
	keyPosChanged         = pyqtSignal( object, float )
	keyLengthChanged      = pyqtSignal( object, float )
	trackDClicked         = pyqtSignal( object, float )
	cursorPosChanged      = pyqtSignal( float )

	def __init__( self, *args, **kwargs ):
		super( TimelineWidget, self ).__init__( *args, **kwargs )
		self.setObjectName( 'Timeline' )

		# layout = QtGui.QVBoxLayout( self )
		# layout.setSpacing( 1 )
		# layout.setMargin( 5 )

		self.ui = TimelineForm()
		self.ui.setupUi( self )
		self.ui.splitter.setObjectName('TimelineHeaderSplitter')
		
		self.view = TimelineView( parent = self )
		self.headerView = TimelineHeaderView( parent = self )

		self.view.scrollYChanged.connect( self.headerView.setScrollY )
		self.headerView.scrollYChanged.connect( self.view.setScrollY )

		layout = QtGui.QVBoxLayout()
		layout.setSpacing( 0)
		layout.setMargin( 0 )
		self.ui.containerTrack.setLayout( layout )
		layout.addWidget( self.view )

		layout = QtGui.QVBoxLayout()
		layout.setSpacing( 0)
		layout.setMargin( 0 )
		self.ui.containerHeader.setLayout( layout )
		layout.addWidget( self.headerView )

		
		self.headerView.setMinimumSize( 150, 200 )
		# self.ruler = TimelineRuler( self, 1 )
		# self.ruler.setSizePolicy(
		# 		QtGui.QSizePolicy.Expanding,
		# 		QtGui.QSizePolicy.Fixed
		# 		)
		# layout.addWidget( self.ruler )
		# self.ruler.scrollPosChanged.connect( self.onScrollPosChanged )
		# self.ruler.cursorPosChanged.connect( self.onCursorPosChanged )
		# self.ruler.zoomChanged.connect( self.onZoomChanged )		
		# self.ruler.setFormatter( self.formatPos )
		self.updating = False
		for i in range( 10 ):
			track = self.view.addTrack()
			for j in range( 5 ):
				key = track.addKey()
				key.setTimePos( j*2 )
				key.setTimeLength( 2 )

		self.view.setCursorPos( 0 )

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
		self.view.setCursorPos( pos )
		# self.scene.setCursorPos( pos )
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

	def closeEvent( self, ev ):
		self.view.setUpdatesEnabled( False )
		self.view.deleteLater()
		self.headerView.deleteLater()
		
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
