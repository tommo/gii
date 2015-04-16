from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform, QStyle
from OpenGL.GL import *


from GraphicsViewHelper import *

import sys
import math

_RULER_SIZE = 25
_TRACK_SIZE = 25
_TRACK_MARGIN = 3
_PIXEL_PER_SECOND = 100.0 #basic scale
_HEAD_OFFSET = 15

##----------------------------------------------------------------##
_DEFAULT_BG = makeBrush( color = '#222' )

##----------------------------------------------------------------##
##styles:  ID                     Pen           Brush          Text
makeStyle( 'black',              '#000000',    '#000000'              )
makeStyle( 'default',            '#000000',    '#ff0ecf'              )
makeStyle( 'key',                '#000000',    '#acbcff'              )
makeStyle( 'key:hover',          '#dfecff',    '#acbcff'              )
makeStyle( 'key:selected',       '#ffffff',    '#a0ff00'              )
makeStyle( 'key-span',           '#000',    '#303459'    ,'#c2c2c2' )
makeStyle( 'key-span:selected',  '#ffffff',    '#303459'               )


##----------------------------------------------------------------##
class TimelineSubView( GLGraphicsView ):
	zoomChanged       = pyqtSignal( float )
	scrollPosChanged  = pyqtSignal( float )
	cursorPosChanged  = pyqtSignal( float )
	def __init__( self, *args, **kwargs ):
		super(TimelineSubView, self).__init__( *args, **kwargs )
		self.zoom = 1.0
		self.scrollPos = 0.0
		self.cursorPos = 0.0
		self.updating = False

	def timeToPos( self, t ):
		return t * self.zoom * _PIXEL_PER_SECOND + _HEAD_OFFSET

	def posToTime( self, p ):
		return ( p - _HEAD_OFFSET ) / ( self.zoom * _PIXEL_PER_SECOND )

	def setZoom( self, zoom, update = True ):
		self.zoom = zoom
		if self.updating: return
		self.updating = True
		self.onZoomChanged( zoom )
		self.zoomChanged.emit( zoom )
		self.updating = False

	def onZoomChanged( self, zoom ):
		pass

	def setScrollPos( self, scrollPos, update = True ):
		self.scrollPos = max( scrollPos, 0.0 )
		if self.updating: return
		self.updating = True
		self.onScrollPosChanged( scrollPos )
		self.scrollPosChanged.emit( scrollPos )
		self.updating = False

	def onScrollPosChanged( self, scrollPos ):
		pass

	def setCursorPos( self, cursorPos, update = True ):
		self.cursorPos = max( cursorPos, 0.0 )
		if self.updating: return
		self.updating = True
		self.onCursorPosChanged( cursorPos )
		self.cursorPosChanged.emit( cursorPos )
		self.updating = False

	def onCursorPosChanged( self, cursorPos ):
		pass


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
class TimelinekeyItemspanItem( QtGui.QGraphicsRectItem, StyledItemMixin ):
	_handleWidth = 10
	def __init__( self, keyItem, *args, **kwargs ):
		super( TimelinekeyItemspanItem, self ).__init__( parent = keyItem.parentItem() )
		self.keyItem = keyItem
		self.width = 100
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.leftHandle = TimelineKeyResizeHandle( self )
		self.RightHandle = TimelineKeyResizeHandle( self )
		self.setItemType( 'key-span' )
		self.setItemState( 'normal' )

	def updateShape( self ):
		spanHeight = _TRACK_SIZE - 2
		self.width = self.keyItem.timeToPos( self.keyItem.timeLength )
		self.setRect( 0, (_TRACK_SIZE - spanHeight)/2 + 1, self.width, spanHeight )
		self.leftHandle.setRect( - TimelinekeyItemspanItem._handleWidth/2, 0, 10, spanHeight )
		self.RightHandle.setRect( self.width - TimelinekeyItemspanItem._handleWidth/2, 0, 10, spanHeight )

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
		self.keyItem.setTimeLength( self.keyItem.posToTime( self.width ) )

	def onPaint( self, painter, option, widget ):
		rect = self.rect()
		painter.drawRect( rect.translated( 0, -1 ) )
		painter.drawStyledText( rect.translated( 4, 0 ), Qt.AlignVCenter | Qt.AlignLeft, self.keyItem.getLabel() )

##----------------------------------------------------------------##
class TimelineKeyItem( QtGui.QGraphicsRectItem, StyledItemMixin ):
	_polyMark = QtGui.QPolygonF([
			QPointF( -0, 0 ),
			QPointF( 10, 0 ),
			QPointF( 0, -10 ),
		]).translated( 0, _TRACK_SIZE )

	def __init__( self, track ):
		super( TimelineKeyItem, self ).__init__( parent = track )
		#
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
		self.span = TimelinekeyItemspanItem( self )
		self.span.hide()
		self.track = track

	def onPaint( self, painter, option, widget ):
		rect = self.rect()
		painter.drawRect( QRectF( 0,0,4, rect.height() ) )
		# painter.drawPolygon( TimelineKeyItem._polyMark )

	def itemChange( self, change, value ):
		if change == self.ItemPositionChange or change == self.ItemPositionHasChanged:
			self.updateKey()
			if not self.updatingPos:
				self.updatingPos = True
				tpos = self.posToTime( self.x() )
				self.setTimePos( tpos )
				self.updatingPos = False
		return QtGui.QGraphicsRectItem.itemChange( self, change, value )

	def delete( self ):
		scn = self.scene()
		scn.removeItem( self )

	def updateKey( self ):
		self.span.setPos( self.pos() )

	def hoverEnterEvent( self, event ):
		self.setItemState( 'hover' )
		self.update()

	def hoverLeaveEvent( self, event ):
		self.setItemState( 'normal' )
		self.update()

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

	def updateFromData( self, key ):
		self.setTimeLength( key.getTimeLength() )
		self.setTimePos( key.getTimePos() )

##----------------------------------------------------------------##
class TimelineTrackItem( QtGui.QGraphicsRectItem ):
	def __init__( self, track ):
		super(TimelineTrackItem, self).__init__()
		self.track = track
		self.index = 0
		self.keyItems = []
		self.zoom = 1		

	def addKeyItem( self, key ):
		keyItem = TimelineKeyItem( self )
		keyItem.key = key
		keyItem.track = self
		self.keyItems.append( keyItem )
		keyItem.updateShape()
		return keyItem

	def clear( self ):
		keyItems = self.keyItems[:]
		for keyItem in keyItems:
			keyItem.delete()

	def setZoom( self, zoom ):
		self.zoom = zoom
		for keyItem in self.keyItems:
			keyItem.updateShape()

	def timeToPos( self, t ):
		return self.view.timeToPos( t )

	def posToTime( self, p ):
		return self.view.posToTime( p )

##----------------------------------------------------------------##
class TimelineRulerCursorItem( QtGui.QGraphicsRectItem ):
	_bgBrush   = makeBrush( color = '#71ff00' )
	_bgPen     = makePen( color = '#71ff00' )
	_polyMark = QtGui.QPolygonF([
			QPointF( -5, -5 ),
			QPointF( 5, -5 ),
			QPointF( 0, 0 ),
		])

	def paint( self, painter, option, widget ):
		rect = self.rect()
		painter.setPen( Qt.transparent )
		painter.setBrush( TimelineRulerCursorItem._bgBrush )
		painter.drawPolygon( TimelineRulerCursorItem._polyMark )

class TimelineRulerItem( QtGui.QGraphicsRectItem ):
	_gridPenV  = makePen( color = '#777', width = 1 )
	_gridPenH  = makePen( color = '#444', width = 1 )
	_cursorPen = makePen( color = '#71ff00', width = 1 )
	_bgBrush   = makeBrush( color = '#222' )
	def __init__( self ):
		super( TimelineRulerItem, self ).__init__()
		self.setCursor( Qt.PointingHandCursor)
		self.step = 1
		self.size = 50
		self.view = None		
		self.setRect( 0,0,10000,50 )
		self.dragging = False

	def mousePressEvent( self, event ):
		if event.button() == Qt.LeftButton:
			self.dragging = True
			x = event.scenePos().x()
			self.view.setCursorPos( self.view.posToTime( x ) + self.view.scrollPos )

	def mouseReleaseEvent( self, event ):
		if event.button() == Qt.LeftButton:
			self.dragging = False

	def mouseMoveEvent( self, event ):
		if not self.dragging: return
		x = event.scenePos().x()
		self.view.setCursorPos( self.view.posToTime( x ) + self.view.scrollPos )

	def formatter( self, pos ):
		return '%.1f' % pos

	def paint( self, painter, option, widget ):
		formatter = self.formatter
		painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
		rect      = painter.viewport()
		transform = painter.transform()
		x = -transform.dx()
		y = -transform.dy()
		w = rect.width()
		h = rect.height()
		size = self.size

		painter.setPen( TimelineRulerItem._gridPenH )
		painter.drawLine( 0,h-1,w,h-1 ) #topline
		painter.setPen( TimelineRulerItem._gridPenV )
		u = self.view.zoom * _PIXEL_PER_SECOND
		t0 = self.view.scrollPos
		dt = w / u
		t1 = t0 + dt
		step = self.step
		start = math.floor( t0/step ) * step
		end   = math.ceil( t1/step + 1 ) * step
		count = int( ( end - start ) / step )
		sw = step * u
		ox = t0 * u

		subStep = 5
		subPitch = sw/subStep
		for i in range( count ): #V lines
			t = start + i * step
			xx = (t-t0) * u + _HEAD_OFFSET
			painter.drawLine( xx, h-20, xx, h - 1 )
			for j in range( 1, subStep ):
				sxx = xx + j * subPitch
				painter.drawLine( sxx, h-5, sxx, h - 1 )
			markText = '%.1f'%( t )
			painter.drawText( QRectF( xx + 2, h-18, 100, 100 ), Qt.AlignTop|Qt.AlignLeft, markText )

		#draw cursor
		painter.setPen( TimelineRulerItem._cursorPen )
		cx = float( self.view.cursorPos - t0 ) * u + _HEAD_OFFSET
		painter.drawLine( cx, 0, cx, h-1 )

##----------------------------------------------------------------##
class TimelineRulerView( TimelineSubView ):
	_BG = makeBrush( color = '#333' )
	def __init__( self, *args, **kwargs ):
		super( TimelineRulerView, self ).__init__( *args, **kwargs )
		self.scene = QtGui.QGraphicsScene( self )
		self.scene.setBackgroundBrush( TimelineRulerView._BG );
		self.scene.setSceneRect( QRectF( 0,0, 10000, 10000 ) )
		self.setScene( self.scene )
		self.ruler = TimelineRulerItem()
		self.ruler.view = self
		self.scene.addItem( self.ruler )
		self.dragging = False

		# self.cursorItem = TimelineRulerCursorItem()
		# self.cursorItem.setRect( 0,0,1,1 )
		# self.scene.addItem( self.cursorItem )
		# self.cursorItem.setY( self.height() )

	def clear( self ):
		pass

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

	def onZoomChanged( self, zoom ):
		# self.updateCursorItem()
		self.update()

	def onScrollPosChanged( self, p ):
		# self.updateCursorItem()
		self.update()

	def onCursorPosChanged( self, pos ):
		self.update()
		# self.updateCursorItem()

	def updateCursorItem( self ):
		self.cursorItem.setX( self.timeToPos( self.cursorPos - self.scrollPos ) ) 

##----------------------------------------------------------------##
class TimelineHeaderItem( QtGui.QGraphicsProxyWidget ):
	foldClicked = pyqtSignal()
	def __init__( self, track ):
		super( TimelineHeaderItem, self ).__init__()
		self.track = track
		self.setCursor( Qt.PointingHandCursor )
		button = QtGui.QPushButton( "TrackView" )
		self.setWidget( button )
		self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
		button.clicked.connect( self.foldClicked )

	def setIndent( self, indent ):
		self.indent = indent

	def setText( self, text ):
		self.text = text
		self.update()

	def setWidth( self, width ):
		pos = self.pos()
		self.setGeometry( QRectF( 0, pos.y(), width, _TRACK_SIZE ) )

##----------------------------------------------------------------##
class TimelineHeaderView( TimelineSubView ):
	scrollYChanged  = pyqtSignal( float )
	def __init__( self, *args, **kwargs ):
		super( TimelineHeaderView, self ).__init__( *args, **kwargs )
		self.scene = QtGui.QGraphicsScene( self )
		self.scene.setBackgroundBrush( _DEFAULT_BG );
		self.scene.setSceneRect( QRectF( 0,0, 10000, 10000 ) )
		self.setScene( self.scene )
		self.scrollY = 0
		self.updating = False
		self.scene.sceneRectChanged.connect( self.onRectChanged )
		self.headerItems = []

	def clear( self ):
		pass

	def setScrollY( self, y, update = True ):
		self.scrollY = y
		if self.updating: return
		self.updating = True
		self.scrollYChanged.emit( self.scrollY )
		if update:
			self.updateTransfrom()
		self.updating = False

	def updateTransfrom( self ):
		trans = QTransform()
		trans.translate( 0, self.scrollY )
		self.setTransform( trans )

	def onRectChanged( self ):
		pass

	def wheelEvent(self, event):
		pass

	def addTrackItem( self, track ):
		item = TimelineHeaderItem( track )
		self.scene.addItem( item )
		self.headerItems.append( item )
		item.setWidth( self.width() )
		# button = QtGui.QPushButton()
		# button.setFixedSize( 300, _TRACK_SIZE * 2 )
		# self.scene.addWidget( button )
		# button.setText( 'hello, graphics button' )
		return item

	def resizeEvent( self, event ):
		w = self.width()
		for item in self.headerItems:
			item.setWidth( w )


##----------------------------------------------------------------##
class TimelineTrackView( TimelineSubView ):
	scrollYChanged   = pyqtSignal( float )
	def __init__( self, *args, **kwargs ):
		super( TimelineTrackView, self ).__init__( *args, **kwargs )
		
		self.gridSize  = 100
		self.scrollPos = 0.0
		self.cursorPos = 0.0
		self.scrollY   = 0.0
		self.zoom      = 1
		self.panning   = False
		self.updating  = False

		self.scene = QtGui.QGraphicsScene( self )
		self.scene.setBackgroundBrush( _DEFAULT_BG );
		self.setScene( self.scene )
		self.scene.sceneRectChanged.connect( self.onRectChanged )

		self.trackItems = []
		
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

	def clear( self ):
		pass

	def addTrackItem( self, track ):
		item = TimelineTrackItem( track )
		item.view = self
		self.scene.addItem( item )
		self.trackItems.append( item )
		item.index = len( self.trackItems )
		item.setPos( 0, ( item.index - 1 ) * ( _TRACK_SIZE + _TRACK_MARGIN ) )
		return item

	def setScrollY( self, y, update = True ):
		self.scrollY = min( y, 0.0 )
		if self.updating: return
		self.updating = True
		self.scrollYChanged.emit( self.scrollY )
		if update:
			self.updateTransfrom()
		self.updating = False

	def onCursorPosChanged( self, pos ):
		self.cursorLine.setX( self.timeToPos( self.cursorPos ) )

	def onScrollPosChanged( self, p ):
		self.updateTransfrom()

	def onZoomChanged( self, zoom ):
		self.updateTransfrom()
		for track in self.trackItems:
			track.setZoom( self.zoom )
		self.gridBackground.setGridWidth( self.gridSize * zoom )
		self.cursorLine.setX( self.timeToPos( self.cursorPos ) )

	def updateTransfrom( self ):
		trans = QTransform()
		sx = - self.timeToPos( self.scrollPos ) + _HEAD_OFFSET
		trans.translate( sx, self.scrollY )
		self.setTransform( trans )
		self.update()

	def mouseMoveEvent( self, event ):
		super( TimelineTrackView, self ).mouseMoveEvent( event )
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
		super( TimelineTrackView, self ).mousePressEvent( event )
		if event.button() == Qt.MidButton:
			self.panning = ( event.pos(), self.timeToPos( self.scrollPos ), self.scrollY )
			self.setCursor( Qt.ClosedHandCursor )

	def mouseReleaseEvent( self, event ):
		super( TimelineTrackView, self ).mouseReleaseEvent( event )
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

	def onRectChanged( self, rect ):
		self.gridBackground.setRect( rect )

##----------------------------------------------------------------##
if __name__ == '__main__':
	import testView