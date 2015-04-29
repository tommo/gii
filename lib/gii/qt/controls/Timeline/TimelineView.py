from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform, QStyle
from OpenGL.GL import *

from GraphicsViewHelper import *
from CurveView import CurveView

import sys
import math

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

TimelineForm,BaseClass = uic.loadUiType( _getModulePath('timeline2.ui') )

##----------------------------------------------------------------##

_RULER_SIZE = 23
_TRACK_SIZE = 17
_TRACK_MARGIN = 3
_PIXEL_PER_SECOND = 100.0 #basic scale
_HEAD_OFFSET = 30

##----------------------------------------------------------------##
_DEFAULT_BG = makeBrush( color = '#222' )

##----------------------------------------------------------------##
##styles:  ID                     Pen           Brush          Text
makeStyle( 'black',              '#000000',    '#000000'              )
makeStyle( 'default',            '#000000',    '#ff0ecf'              )
makeStyle( 'key',                '#000000',    '#acbcff'              )
makeStyle( 'key:hover',          '#dfecff',    '#acbcff'              )
makeStyle( 'key:selected',       '#ffffff',    '#a0ff00'              )
makeStyle( 'key-span',           '#000',       '#303459'    ,'#c2c2c2' )
makeStyle( 'key-span:selected',  '#ffffff',    '#303459'               )
makeStyle( 'track',                None,       dict( color = '#444', alpha = 0.2 ) )
makeStyle( 'track:selected',       None,       dict( color = '#555', alpha = 0.2 ) )
makeStyle( 'selection',          dict( color = '#ffa000', alpha = 0.5 ), dict( color = '#ffa000', alpha = 0.2 ) )


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

	def setCursorVisible( self, visible ):
		pass

##----------------------------------------------------------------##
class CursorItem( QtGui.QGraphicsLineItem ):
	_pen  = makePen( color = '#9cff00', width = 1 )
	def __init__( self ):
		super( CursorItem, self ).__init__()
		self.setPen( self._pen )

	def paint( self, painter, option, widget ):
		painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
		super( CursorItem, self ).paint( painter, option, widget )


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
		self.cursorVisible = True

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
			painter.drawLine( xx, h-25, xx, h - 1 )
			for j in range( 1, subStep ):
				sxx = xx + j * subPitch
				painter.drawLine( sxx, h-8, sxx, h - 1 )
			markText = '%.1f'%( t )
			painter.drawText( QRectF( xx + 2, h-20, 100, 100 ), Qt.AlignTop|Qt.AlignLeft, markText )

		#draw cursor
		if self.cursorVisible:
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
		self.draggable = True

	def clear( self ):
		pass

	def setCursorVisible( self, visible ):
		self.ruler.cursorVisible = visible
		self.update()

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

	def setDraggable( self, draggable ):
		self.draggable = draggable

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

		self.node = None

		self.dragging = False
		self.setItemType( 'key' )
		self.setItemState( 'normal' )
		self.timePos    = 0
		self.timeLength = 0
		self.updatingPos = False
		self.span = TimelinekeyItemspanItem( self )
		self.span.hide()
		self.track = track

		self.selected = False

	def onPaint( self, painter, option, widget ):
		rect = self.rect()
		painter.drawRect( QRectF( 0,0,4, rect.height() ) )
		# painter.drawPolygon( TimelineKeyItem._polyMark )

	def itemChange( self, change, value ):
		if change == self.ItemPositionChange:
			self.updateKey()
		elif change == self.ItemPositionHasChanged:
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
		if self.selected: return
		self.setItemState( 'hover' )
		self.update()

	def hoverLeaveEvent( self, event ):
		if self.selected: return
		self.setItemState( 'normal' )
		self.update()

	def setSelected( self, selected, notifyParent = False ):
		self.selected = selected
		if selected:
			self.setItemState( 'selected' )
		else:
			self.setItemState( 'normal' )
		if notifyParent:
			self.getTimelineView().selectKey( self.node, True )

	def mousePressEvent( self, event ):
		if event.button() == Qt.LeftButton:
			x0 = self.pos().x()
			mx0 = event.scenePos().x()
			self.dragging = ( x0, mx0 )
			if event.modifiers() == Qt.ShiftModifier:
				if self.selected:
					self.getTimelineView().deselectKey( self.node )
				else:
					self.getTimelineView().selectKey( self.node, True )
			else:
				self.getTimelineView().selectKey( self.node, False )

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
		self.setTimePos( self.timePos, False )
		self.span.updateShape()

	def setTimePos( self, tpos, notify = True ):
		tpos = max( 0, tpos )
		self.timePos = tpos
		x = self.timeToPos( tpos )
		if notify:
			self.getTimelineView().notifyKeyChanged( self.node, self.timePos, self.timeLength )
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

	def getTimelineView( self ):
		return self.track.getTimelineView()
	
##----------------------------------------------------------------##
class TimelineTrackItem( QtGui.QGraphicsRectItem, StyledItemMixin ):
	def __init__( self ):
		super(TimelineTrackItem, self).__init__()
		self.trackType  = 'normal' # group / object / property
		self.index = 0
		self.keys = []
		self.zoom = 1
		self.setItemType( 'track' )
		self.setItemState( 'normal' )
		self.node = None

	def addKey( self, keyNode ):
		for key in self.keys:
			if key.node == keyNode:
				return key
		keyItem = TimelineKeyItem( self )
		keyItem.track = self
		keyItem.node  = keyNode
		self.keys.append( keyItem )
		keyItem.updateShape()
		return keyItem

	def removeKey( self, keyNode ):
		key = self.getKeyByNode( keyNode )
		if key:
			key.setParentItem( None )
			self.keys.remove( key )
			key.delete()
		
	def getKeyByNode( self, keyNode ):
		for key in self.keys:
			if key.node == keyNode:
				return key
		return None

	def clear( self ):
		keys = self.keys[:]
		for keyItem in keys:
			keyItem.setParentItem( None )
			keyItem.delete()
		self.keys = ()

	def setZoom( self, zoom ):
		self.zoom = zoom
		for keyItem in self.keys:
			keyItem.updateShape()

	def timeToPos( self, t ):
		return self.view.timeToPos( t )

	def posToTime( self, p ):
		return self.view.posToTime( p )

	def onKeyUpdate( self, key ):
		self.view.onKeyUpdate( self, key )

	def onPaint( self, painter, option, widget ):
		rect = self.rect()
		painter.drawRect( rect )

	def getTimelineView( self ):
		return self.view.getTimelineView()


##----------------------------------------------------------------##
class SelectionRegionItem( QtGui.QGraphicsRectItem, StyledItemMixin ):
	def __init__( self, *args, **kwargs ):
		super( SelectionRegionItem, self ).__init__( *args, **kwargs )
		self.setItemType( 'selection' )

	def onPaint( self, painter, option, widget ):
		rect = self.rect()
		painter.drawRect( rect )

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
		
		self.selecting = False
		self.selectingItems = []

		scene = QtGui.QGraphicsScene( self )
		scene.setBackgroundBrush( _DEFAULT_BG );
		self.setScene( scene )
		scene.sceneRectChanged.connect( self.onRectChanged )

		self.trackItems = []
		
		#components
		self.cursorItem = CursorItem()
		self.cursorItem.setLine( 0,0, 0, 10000 )
		self.cursorItem.setZValue( 1000 )
		scene.addItem( self.cursorItem )
		#grid
		self.gridBackground = GridBackground()
		self.gridBackground.setGridSize( self.gridSize, _TRACK_SIZE + _TRACK_MARGIN )
		self.gridBackground.setAxisShown( False, True )
		self.gridBackground.setOffset( _HEAD_OFFSET, -1 )
		scene.addItem( self.gridBackground )

		scene.setSceneRect( QRectF( 0,0, 10000, 10000 ) )

		self.selectionRegion = SelectionRegionItem()
		self.selectionRegion.setZValue( 9999 )
		self.selectionRegion.setVisible( False )
		scene.addItem( self.selectionRegion )

	def clear( self ):
		scn = self.scene()
		for trackItem in self.trackItems:
			trackItem.clear()
			trackItem.setParentItem( None )
			scn.removeItem( trackItem )
		self.trackItems = []

	def setCursorVisible( self, visible ):
		self.cursorItem.setVisible( visible )

	def addTrackItem( self ):
		item = TimelineTrackItem()
		item.view = self
		item.setRect( 0,0, 10000, _TRACK_SIZE )
		self.scene().addItem( item )
		self.trackItems.append( item )
		item.index = len( self.trackItems )
		item.setPos( 0, ( item.index - 1 ) * ( _TRACK_SIZE + _TRACK_MARGIN ) )
		return item

	def removeTrackItem( self, track ):
		self.trackItems.remove( track )
		track.setParentItem( None )
		track.node = None
		track.scene().removeItem( track )

	def setScrollY( self, y, update = True ):
		self.scrollY = min( y, 0.0 )
		if self.updating: return
		self.updating = True
		self.scrollYChanged.emit( self.scrollY )
		if update:
			self.updateTransfrom()
		self.updating = False

	def getScrollY( self ):
		return self.scrollY

	def onCursorPosChanged( self, pos ):
		self.cursorItem.setX( self.timeToPos( self.cursorPos ) )

	def onScrollPosChanged( self, p ):
		self.updateTransfrom()

	def onZoomChanged( self, zoom ):
		self.updateTransfrom()
		for track in self.trackItems:
			track.setZoom( self.zoom )
		self.gridBackground.setGridWidth( self.gridSize * zoom )
		self.cursorItem.setX( self.timeToPos( self.cursorPos ) )

	def updateTransfrom( self ):
		trans = QTransform()
		sx = - self.timeToPos( self.scrollPos ) + _HEAD_OFFSET
		trans.translate( sx, self.scrollY )
		self.setTransform( trans )
		# self.update()

	def startSelectionRegion( self, pos ):
		self.selecting = True
		self.selectionRegion.setPos( pos )
		self.selectionRegion.setRect( 0,0,0,0 )
		self.selectionRegion.setVisible( True )
		self.resizeSelectionRegion( pos )
		# for keyNode in self.selection:
		# 	key = self.getKeyByNode( keyNode )
		# 	key.setSelected( False, False )

	def resizeSelectionRegion( self, pos1 ):
		pos = self.selectionRegion.pos()
		w, h = pos1.x()-pos.x(), pos1.y()-pos.y()
		self.selectionRegion.setRect( 0,0, w, h )
		itemsInRegion = self.scene().items( pos.x(), pos.y(), w, h )
		for item in self.selectingItems:
			item.setSelected( False, False )

		self.selectingItems = []
		for item in itemsInRegion:
			if isinstance( item, TimelineKeyItem ):
				self.selectingItems.append( item )
				item.setSelected( True, False )

	def stopSelectionRegion( self ):
		self.selectionRegion.setRect( 0,0,0,0 )
		self.selectionRegion.setVisible( False )
		selection = []
		for key in self.selectingItems:
			selection.append( key.node )
		self.timelineView.updateSelection( selection )

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
			# self.setScrollY( sy1, False )
			self.updateTransfrom()
		elif self.selecting:
			self.resizeSelectionRegion( self.mapToScene( event.pos() ) )

	def mousePressEvent( self, event ):
		super( TimelineTrackView, self ).mousePressEvent( event )
		if event.button() == Qt.MidButton:
			self.panning = ( event.pos(), self.timeToPos( self.scrollPos ), self.scrollY )
		elif event.button() == Qt.LeftButton and event.modifiers() == Qt.ShiftModifier:
			self.startSelectionRegion( self.mapToScene( event.pos() ) )
			self.selecting = True

	def mouseReleaseEvent( self, event ):
		super( TimelineTrackView, self ).mouseReleaseEvent( event )
		if event.button() == Qt.MidButton :
			if self.panning:
				self.panning = False
		if event.button() == Qt.LeftButton:
			if self.selecting:
				self.stopSelectionRegion()
				self.selecting = False

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

	def keyPressEvent( self, event ):
		key = event.key()
		modifiers = event.modifiers()
		if key in ( Qt.Key_Delete, Qt.Key_Backspace ):
			self.timelineView.deleteSelection()


	def onRectChanged( self, rect ):
		self.gridBackground.setRect( rect )

	def getTimelineView( self ):
		return self.timelineView

##----------------------------------------------------------------##	
class TimelineView( QtGui.QWidget ):
	keySelectionChanged   = pyqtSignal()
	trackSelectionChanged = pyqtSignal()
	keyChanged            = pyqtSignal( object, float, float )
	keyModeChanged        = pyqtSignal( object )
	keyCurvateChanged     = pyqtSignal( object, float, float )
	cursorPosChanged      = pyqtSignal( float )
	zoomChanged           = pyqtSignal( float )

	def __init__( self, *args, **kwargs ):
		super( TimelineView, self ).__init__( *args, **kwargs )
		#start up
		self.rebuilding = False
		self.updating   = False
		self.shiftMode  = False
		self.selection = []

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
		self.trackView.timelineView = self

		self.rulerView  = TimelineRulerView( parent = self )
		self.curveView  = CurveView( parent = self )
		self.curveView.setAxisShown( False, True )
		self.curveView.setOffset( _HEAD_OFFSET, 0 )
		self.curveView.setScrollXLimit( 0, None )

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
		self.curveView.zoomXChanged.connect( self.onZoomChanged )

		self.trackView.scrollPosChanged.connect( self.onScrollPosChanged )
		self.rulerView.scrollPosChanged.connect( self.onScrollPosChanged )
		self.curveView.scrollXChanged.connect( self.onScrollPosChanged )

		self.trackView.cursorPosChanged.connect( self.onCursorPosChanged )
		self.rulerView.cursorPosChanged.connect( self.onCursorPosChanged )

		self.tabViewSwitch = QtGui.QTabBar()		
		bottomLayout = QtGui.QHBoxLayout( self.ui.containerBottom )
		bottomLayout.addWidget( self.tabViewSwitch )
		bottomLayout.setSpacing( 0 )
		bottomLayout.setMargin( 0 )
		self.tabViewSwitch.addTab( 'Dope Sheet')
		self.tabViewSwitch.addTab( 'Curve View' )
		self.tabViewSwitch.currentChanged.connect( self.onTabChanged )
		self.tabViewSwitch.setShape( QtGui.QTabBar.RoundedSouth )
		self.tabViewSwitch.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)

		self.toolbarEdit = QtGui.QToolBar()
		self.toolbarEdit.setObjectName( 'TimelineToolBarEdit')
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

	def getBottomToolHeight( self ):
		return self.toolbarEdit.height()
		
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

	def setTrackViewScroll( self, y ):
		self.trackView.setScrollY( y )

	def getTrackViewScroll( self, y ):
		return self.trackView.getScrollY( y )

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
		self.rebuilding = True
		for node in self.getTrackNodes():
			self.addTrack( node )
		self.updateTrackLayout()
		self.rebuilding = False

	def clear( self ):
		self.hide()
		self.trackView.clear()
		self.rulerView.clear()
		self.tracks = []
		self.nodeToTrack = {}
		self.updateTrackLayout()
		self.show()

	def updateTrackLayout( self ):
		y = 0
		for track in self.tracks:
			node = track.node
			vis = self.isTrackVisible( node )
			if vis:
				y = self.getTrackPos( node )
				track.setY( y )
				y += _TRACK_SIZE + _TRACK_MARGIN
			track.setVisible( vis or False )
		
	def getTrackByNode( self, trackNode ):
		return self.nodeToTrack.get( trackNode, None )

	def getKeyByNode( self, keyNode ):
		track = self.getParentTrack( keyNode )
		return track and track.getKeyByNode( keyNode ) or None

	def addTrack( self, node, **option ):
		assert not self.nodeToTrack.has_key( node )
		track =  self.trackView.addTrackItem()
		track.node = node
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
		self.trackView.removeTrackItem( track )
		self.updateTrackLayout()

	def addKey( self, keyNode, **option ):
		track = self.affirmParentTrack( keyNode )
		if not track: return None
		key = track.addKey( keyNode )
		if key:
			self.refreshKey( keyNode, **option )			
		return key

	def removeKey( self, keyNode ):
		track = self.getParentTrack( keyNode )
		if not track: return
		track.removeKey( keyNode )
		if keyNode in self.selection:
			self.selection.remove( keyNode )

	def getParentTrack( self, keyNode ):
		trackNode = self.getParentTrackNode( keyNode )
		if not trackNode: return None
		return self.getTrackByNode( trackNode )

	def affirmParentTrack( self, keyNode ):
		trackNode = self.getParentTrackNode( keyNode )
		if not trackNode: return None
		trackItem = self.getTrackByNode( trackNode )
		if not trackItem:
			return self.addTrack( trackNode )
		else:
			return trackItem

	def getSelectedTrackNode( self ):
		track = self.selectedTrack
		return track and track.node or None

	def setCursorDraggable( self, draggable = True ):
		self.rulerView.setCursorDraggable( draggable )

	def onCursorPosChanged( self, pos ):
		if self.updating: return
		self.updating = True
		self.rulerView.setCursorPos( pos )
		self.trackView.setCursorPos( pos )
		self.curveView.setCursorX( pos )
		self.cursorPosChanged.emit( pos )
		self.updating = False

	def onScrollPosChanged( self, pos ):
		if self.updating: return
		self.updating = True
		self.rulerView.setScrollPos( pos )
		self.trackView.setScrollPos( pos )
		self.curveView.setScrollX( pos )
		self.updating = False

	def onZoomChanged( self, zoom ):
		if self.updating: return
		self.updating = True
		#sync widget zoom
		self.rulerView.setZoom( zoom )
		self.trackView.setZoom( zoom )
		self.curveView.setZoomX( zoom )
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

	def notifyKeyChanged( self, keyNode, pos, length ):
		self.keyChanged.emit( keyNode, pos, length )

	def deselectKey( self, keyNode ):
		if not keyNode in self.selection:
			return
		self.selection.remove( keyNode )
		keyItem = self.getKeyByNode(keyNode)
		keyItem.setSelected( False, False )

	def selectKey( self, keyNode, additive = False ):
		if additive:
			if not keyNode in self.selection:
				self.selection.append( keyNode )
			keyItem = self.getKeyByNode(keyNode)
			keyItem.setSelected( True, False )

		else:
			for prevKey in self.selection:				
				keyItem = self.getKeyByNode( prevKey )
				keyItem.setSelected( False, False )

			self.selection = []
			if keyNode:
				self.selection.append( keyNode )
				keyItem = self.getKeyByNode( keyNode )
				keyItem.setSelected( True, False )
		self.keySelectionChanged.emit()
		self.update()
		self.onSelectionChanged( self.selection )

	def clearSelection( self ):
		self.selectKey( None )

	def updateSelection( self, selection ):
		self.selection = selection
		self.onSelectionChanged( self.selection )

	def getSelection( self ):
		return self.selection

	def deleteSelection( self ):
		oldSelection = self.selection [:]
		for keyNode in oldSelection:
			if self.onKeyRemoving( keyNode ) != False:
				self.removeKey( keyNode )

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
		return TimelineKeyItem( )

	def createTrack( self, node ):
		return TimelineTrackItem( )

	def getTrackNodes( self ):
		return []

	def getKeyNodes( self, trackNode ):
		return []

	def getKeyParam( self, keyNode ):
		return ( 0, 10, True )

	def getParentTrackNode( self, keyNode ):
		return None

	def getTrackPos( self, trackNode ):
		return 0

	def isTrackVisible( self, trackNode ):
		return 0

	def onSelectionChanged( self, selection ):
		pass

	def onKeyRemoving( self, keyNode ):
		return True


	#######
	#Interaction
	#######
	def onTrackClicked( self, track, pos ):
		self.selectTrack( track.node )

	def onKeyClicked( self, key, pos ):
		self.selectKey( key.node )

	def setEnabled( self, enabled ):
		super( TimelineView, self ).setEnabled( enabled )
		self.trackView.setCursorVisible( enabled )
		self.rulerView.setCursorVisible( enabled )
		self.curveView.setCursorVisible( enabled )

	# def closeEvent( self, ev ):
	# 	self.trackView.deleteLater()
	# 	self.rulerView.deleteLater()
		
	# def __del__( self ):
	# 	self.deleteLater()

##----------------------------------------------------------------##
if __name__ == '__main__':
	import testView
