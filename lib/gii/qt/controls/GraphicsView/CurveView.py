import sys
import math

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform, QStyle

from GraphicsViewHelper import *

##----------------------------------------------------------------##
CV_INNER_SIZE = 6
CV_SIZE = 15
TP_INNER_SIZE = 6
TP_SIZE = 15

_PIXEL_PER_UNIT = 100.0 #basic scale
_HEAD_OFFSET = 15

##----------------------------------------------------------------##
_DEFAULT_BG = makeBrush( color = '#222' )
makeStyle( 'cv',                '#acbcff',    '#4d9fff'              )
makeStyle( 'cv:selected',       '#ffffff',    '#000000'              )
makeStyle( 'tp',                dict( color = '#b940d6', alpha=0.5 ),    '#b940d6'    )
makeStyle( 'tp:selected',       dict( color = '#ffffff', alpha=1.0 ),    '#000000'    )
makeStyle( 'curve',             '#7f7f7f',    None             )



##----------------------------------------------------------------##
SPAN_MODE_CONSTANT = 0
SPAN_MODE_LINEAR   = 1
SPAN_MODE_BEZIER   = 2

TANGENT_MODE_AUTO    = 0
TANGENT_MODE_SPLIT   = 1
TANGENT_MODE_SMOOTH  = 2


##----------------------------------------------------------------##
class CursorItem( QtGui.QGraphicsLineItem ):
	_pen  = makePen( color = '#a3ff00', width = 1 )
	def __init__( self ):
		super( CursorItem, self ).__init__()
		self.setPen( self._pen )

	def paint( self, painter, option, widget ):
		# painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
		super( CursorItem, self ).paint( painter, option, widget )

##----------------------------------------------------------------##
class AxisGridBackground( QtGui.QGraphicsRectItem ):
	_gridPen  = makePen( color = '#333', width = 1 )
	_axisPen  = makePen( color = '#777', width = 1 )
	_originPen  = makePen( color = '#204800', width = 2 )
	_cursorPen  = makePen( color = '#a3ff00', width = 1 )
	def __init__( self ):
		super( AxisGridBackground, self ).__init__()
		self.setZValue( -100 )
		self.gridWidth = 50
		self.gridHeight = 50 
		self.offsetX = 1
		self.offsetY = 1
		self.zoomX = 2
		self.zoomY = 1
		self.showXAxis = True
		self.showYAxis = True
		self.cursorVisible = False
		self.cursorPosX = 0
		self.cursorPen = AxisGridBackground._cursorPen

	def setOffset( self, x, y ):
		self.offsetX = x
		self.offsetY = y
		self.updateTransfrom()

	def setCursorPosX( self, pos ):
		self.cursorPosX = pos

	def setGridSize( self, width, height = None ):
		if not height:
			height = width
		self.gridWidth = width
		self.gridHeight = height
		self.update()

	def setGridWidth( self, width ):
		self.setGridSize( width, self.gridHeight )

	def setGridHeight( self, height ):
		self.setGridSize( self.gridWidth, height )

	def paint( self, painter, option, widget ):
		# painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
		rect = painter.viewport()
		transform = painter.transform()
		dx = transform.dx() 
		dy = transform.dy()
		w = rect.width()
		h = rect.height()
		x0 = -dx
		y0 = -dy
		x1 = x0 + w
		y1 = y0 + h

		u = 100
		stepx = 1
		stepy = 1
		ux = u * self.zoomX
		uy = u * self.zoomY
		vx0 = x0 / ux
		vy0 = y0 / uy
		dvx = w / ux
		dvy = h / uy
		vx1 = vx0 + dvx
		vy1 = vy0 + dvy
		stepWidth = stepx * ux
		stepHeight = stepy * uy

		#Grid
		ox = (dx) % ux
		oy = (dy) % uy
		rows = int( h/uy ) + 1
		cols = int( w/ux ) + 1
		offx = self.offsetX
		painter.setPen( AxisGridBackground._gridPen )
		for col in range( cols ): #V lines
			x = col * ux + ox + x0 + offx
			painter.drawLine( x, y0, x, y1 )
		
		# x0 = max( x0, _HEAD_OFFSET )
		offy = self.offsetY
		painter.setPen( AxisGridBackground._gridPen )
		for row in range( rows ): #H lines
			y = row * uy + oy + y0 + offy
			painter.drawLine( x0, y, x1, y )
		
		#Origin
		painter.setPen( AxisGridBackground._originPen )
		originX = 0
		originY = 0
		painter.drawLine( originX, y0, originX, y1 )
		painter.drawLine( x0, originY, x1, originY )

		trans = painter.transform()
		trans.translate( -dx, -dy )
		painter.setTransform( trans )
		#XAxis
		if self.showXAxis:
			start = math.floor( vx0/stepx ) * stepx
			end   = math.ceil( vx1/stepx ) * stepx
			count = int( (end-start)/stepx ) + 1
			
			painter.setPen( AxisGridBackground._axisPen )
			subStep = 5
			subPitch = stepWidth/subStep
			for i in range( count ): #V lines
				vx = start + i * stepx
				xx = (vx-vx0) * ux
				painter.drawLine( xx, h-20, xx, h - 1 )
				for j in range( 1, subStep ):
					sxx = xx + j * subPitch
					painter.drawLine( sxx, h-6, sxx, h - 1 )
				markText = '%.1f'%( vx )
				painter.drawText( QRectF( xx + 2, h-20, 100, 100 ), Qt.AlignTop|Qt.AlignLeft, markText )

		#YAxis
		if self.showYAxis:
			start = math.floor( vy0/stepy ) * stepy
			end   = math.ceil( vy1/stepy ) * stepy
			count = int( (end-start)/stepy ) + 1

			painter.setPen( AxisGridBackground._axisPen )
			subStep = 5
			subPitch = stepHeight/subStep
			for i in range( count ): #V lines
				vy = start + i * stepy
				yy = (vy-vy0) * uy
				painter.drawLine( 0, yy, 20, yy )
				for j in range( 1, subStep ):
					syy = yy + j * subPitch
					painter.drawLine( 0, syy, 6, syy )
				markText = '%.1f'%( vy )
				painter.drawText( QRectF( 5, yy + 3, 100, 20 ), Qt.AlignTop|Qt.AlignLeft, markText )

		if self.cursorVisible:
			x = self.cursorPosX + dx
			painter.setPen( self.cursorPen )
			painter.drawLine( x, y0 + dy, x, y1 + dy )

	def setZoom( self, zx, zy ):
		self.zoomX = zx
		self.zoomY = zy
		self.update()

##----------------------------------------------------------------##
class CurveSpanItem( QtGui.QGraphicsPathItem ):
	def __init__( self, startVert, *args ):
		super( CurveSpanItem, self ).__init__( *args )
		self.startVert = startVert
		self.setParentItem( startVert.parentItem() )
		applyStyle( 'curve', self )

	def updateShape( self ):
		mode = self.startVert.spanMode
		if mode == SPAN_MODE_CONSTANT:
			self.updateConstantCurve()
		if mode == SPAN_MODE_LINEAR:
			self.updateLinearCurve()
		if mode == SPAN_MODE_BEZIER:
			self.updateBezierCurve()

	def updateLinearCurve( self ):
		startVert = self.startVert
		endVert = startVert.getNextVert()
		if not endVert: 
			self.hide()
			return
		self.show()
		self.setPos( startVert.pos() )

		path = QtGui.QPainterPath()
		pos1 = self.mapFromScene( endVert.scenePos() )
		path.moveTo( 0, 0 )
		path.lineTo( pos1 )
		self.setPath( path )

	def updateConstantCurve( self ):
		startVert = self.startVert
		endVert = startVert.getNextVert()
		if not endVert: 
			self.hide()
			return
		self.show()
		self.setPos( startVert.pos() )

		path = QtGui.QPainterPath()
		pos1 = self.mapFromScene( endVert.scenePos() )
		path.moveTo( 0, 0 )
		path.lineTo( pos1.x(), 0 )
		path.lineTo( pos1 )
		self.setPath( path )

	def updateBezierCurve( self ):
		startVert = self.startVert
		endVert  = startVert.getNextVert()
		if not endVert: 
			self.hide()
			return
		self.show()

		self.setPos( startVert.pos() )

		path = QtGui.QPainterPath()
		pos1 = self.mapFromScene( endVert.scenePos() )
		tp0  = startVert.getPostTP() # + (0,0)
		preTP = endVert.getPreTP() + pos1
		path.moveTo( 0, 0 )
		path.cubicTo( tp0, preTP, pos1 )
		self.setPath( path )

	def paint( self, painter, option, widget ):
		painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
		applyStyle( 'curve', painter)
		path = self.path()
		painter.drawPath( path )

##----------------------------------------------------------------##
class CurveTangentPointItem( QtGui.QGraphicsRectItem ):
	def __init__( self ):
		super( CurveTangentPointItem, self ).__init__()
		self.setZValue( 9 )
		self.setRect( -TP_SIZE/2, -TP_SIZE/2, TP_SIZE, TP_SIZE )
		self.innerRect = QRectF( -TP_INNER_SIZE/2, -TP_INNER_SIZE/2, TP_INNER_SIZE, TP_INNER_SIZE )
		self.setCursor( Qt.PointingHandCursor )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.setFlag( self.ItemIsMovable, True )
		self.setFlag( self.ItemIsSelectable, True )


	def itemChange( self, change, value ):
		if change == self.ItemPositionChange or change == self.ItemPositionHasChanged:
			self.parentItem().onTPUpdate( self )
		return super( CurveTangentPointItem, self ).itemChange( change, value )

	def paint( self, painter, option, widget ):
		if self.isSelected():
			applyStyle( 'tp:selected', painter )
		else:
			applyStyle( 'tp', painter )
		painter.drawEllipse( self.innerRect )

##----------------------------------------------------------------##
class CurveVertPointItem( QtGui.QGraphicsRectItem ):
	def __init__( self, vertItem ):
		super( CurveVertPointItem, self ).__init__()
		self.setZValue( 10 )
		self.setRect( -CV_SIZE/2, -CV_SIZE/2, CV_SIZE, CV_SIZE )
		self.innerRect = QRectF( -CV_INNER_SIZE/2, -CV_INNER_SIZE/2, CV_INNER_SIZE, CV_INNER_SIZE )
		self.setCursor( Qt.PointingHandCursor )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.setFlag( self.ItemIsMovable, True )
		self.setFlag( self.ItemIsSelectable, True )
		self.vertItem = vertItem
		self.setParentItem( vertItem.parentItem() )

	def itemChange( self, change, value ):
		if change == self.ItemPositionChange or change == self.ItemPositionHasChanged:
			self.vertItem.setPos( self.pos() )
		return super( CurveVertPointItem, self ).itemChange( change, value )

	def paint( self, painter, option, widget ):
		if self.isSelected():
			applyStyle( 'cv:selected', painter )
		else:
			applyStyle( 'cv', painter )
		painter.drawRect( self.innerRect )

##----------------------------------------------------------------##
class CurveVertItem( QtGui.QGraphicsRectItem ):
	def __init__( self, parent ):
		super( CurveVertItem, self ).__init__()
		self.index = 0 #update by curve verts sorting
		self.setParentItem( parent )
		self.setZValue( 10 )
		self.setRect( -CV_SIZE/2, -CV_SIZE/2, CV_SIZE, CV_SIZE )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.updating = False

		self.value    = 0.0

		self.spanMode = SPAN_MODE_LINEAR

		#components
		self.VP     = CurveVertPointItem( self )
		self.span   = CurveSpanItem( self )
		self.preTP  = CurveTangentPointItem()
		self.postTP = CurveTangentPointItem()

		self.preTP.setParentItem( self )
		self.postTP.setParentItem( self )
		self.preTP.hide()
		self.postTP.hide()

		self.preTPValue  = ( 0.5, 0 )
		self.postTPValue = ( 0.5, 0 )

	def updateZoom( self, zx, zy ):
		trans = QTransform()
		trans.scale( 1.0/zx, 1.0/zy )
		# self.setTransform( trans )
		self.VP.setTransform( trans )
		self.preTP.setTransform( trans )
		self.postTP.setTransform( trans )
		prev = self.getPrevVert()
		if prev: #update TP pos
			(px0, py0) = prev.postTPValue
			(px1, py1) = self.preTPValue
			pos0 = prev.pos()
			pos1 = self.pos()
			dx = ( pos1.x() - pos0.x() )
			prev.postTP.setPos(   px0 * dx, py0 )
			self.preTP .setPos( - px1 * dx, py1 )

	def setValue( self, v ):
		self.value = v

	def getPostTP( self ):
		return self.postTP.pos()

	def getPreTP( self ):
		return self.preTP.pos()	

	def itemChange( self, change, value ):		
		if change == self.ItemPositionChange or change == self.ItemPositionHasChanged:
			if not self.updating:
				self.updating = True
				self.VP.setPos( self.pos() )
				self.updateSpan()
				self.updating = False

		return QtGui.QGraphicsRectItem.itemChange( self, change, value )

	def onTPUpdate( self, tp ):
		if tp == self.postTP:
			nextVert = self.getNextVert()
			if nextVert:
				pos = tp.pos()
				dx = nextVert.pos().x() - self.pos().x()
				if dx == 0:
					self.postTPValue = ( 0, pos.y() )
				else:
					( tpx, tpy ) = nextVert.preTPValue 
					v0 = 0.0
					v1 = (1.0 - tpx)
					v = tp.pos().x() / dx
					corrected = max( 0.0, min( v1, v  ) )
					self.postTPValue = ( corrected , pos.y() )
					if v != corrected:
						tp.setFlag( self.ItemSendsGeometryChanges, False )
						tp.setX( dx*corrected )
						tp.setFlag( self.ItemSendsGeometryChanges, True )


		elif tp == self.preTP:
			prevVert = self.getPrevVert()
			if prevVert:
				pos = tp.pos()
				dx = prevVert.pos().x() - self.pos().x()
				if dx == 0:
					self.preTPValue = ( 0, pos.y() )
				else:
					( tpx, tpy ) = prevVert.postTPValue 
					v0 = 0.0
					v1 = (1.0 - tpx)
					v = tp.pos().x() / dx
					corrected = max( 0.0, min( v1, v ) )
					self.preTPValue = ( corrected , pos.y() )
					if v != corrected:
						tp.setFlag( self.ItemSendsGeometryChanges, False )
						tp.setX( dx * corrected )
						tp.setFlag( self.ItemSendsGeometryChanges, True )
		self.updateSpan()

	def getIndex( self ):
		return self.index

	def getPrevVert( self ):
		return self.parentItem().getPrevVert( self )

	def getNextVert( self ):
		return self.parentItem().getNextVert( self )

	def updateSpan( self, updateNeighbor = True ):
		if updateNeighbor:
			prevVert = self.getPrevVert()
			if prevVert:
				prevVert.updateSpan( False )
		self.span.updateShape()
		bx = ( self.preTP.x(), self.postTP.x(), 0.0 )
		by = ( self.preTP.y(), self.postTP.y(), 0.0 )
		x0 = min( bx )
		y0 = min( by )
		x1 = max( bx )
		y1 = max( by )
		self.setRect( x0,y0,x1-x0,y1-y0 )		

	def paint( self, painter, option, widget ):
		applyStyle( 'tp', painter)
		p0 = QPointF( 0.0, 0.0 )
		if self.preTP.isVisible():
			painter.drawLine( p0, self.preTP.pos() )
		if self.postTP.isVisible():
			painter.drawLine( p0, self.postTP.pos() )

	def setSpanMode( self, mode ):
		self.spanMode = mode
		self.updateSpan()

	def setParam( self, x,y, curveMode, tanPre, tanPost ):
		self.setPos( x,y )
		self.spanMode = curveMode
		#Todo tangent
		self.updateSpan()
		self.showTP()

	def showTP( self ):
		self.preTP.show()
		self.postTP.show()
		prev = self.getPrevVert()
		if prev:
			prev.postTP.show()
		next = self.getNextVert()
		if next:
			next.preTP.show()

	def hideTP( self ):
		self.preTP.hide()
		self.postTP.hide()
		prev = self.getPrevVert()
		if prev:
			prev.postTP.hide()
		next = self.getNextVert()
		if next:
			next.preTP.hide()




##----------------------------------------------------------------##
class CurveItem( QtGui.QGraphicsRectItem ):
	def __init__( self, curveNode ):
		super(CurveItem, self).__init__()
		self.node = curveNode

		self.zx = 1
		self.zy = 1
		self.vertItems = []
		self.nodeToVert = {}
		
	def getVertByNode( self, node ):
		return self.nodeToVert.get( node, None )

	def addVert( self, node ):
		vert = CurveVertItem( self )
		vert.node = node
		self.vertItems.append( vert )
		vert.index = len( self.vertItems ) - 1
		self.nodeToVert[ node ] = vert
		self.sortVerts()
		self.updateSpan()

		vert.updateZoom( self.zx, self.zy )
		return vert

	def removeVert( self, node ):
		vert = self.getVertByNode( node )
		if vert :
			del self.nodeToVert[ node ]
			vert.setParentItem( None )
			vert.node = None
			self.vertItems.remove( vert )

	def getPrevVert( self, vert ):
		index = vert.index
		index1 = index - 1
		if index1 >= 0:
			return self.vertItems[ index1 ]
		return None

	def getNextVert( self, vert ):
		index = vert.index
		index1 = index + 1
		if index1 < len( self.vertItems ):
			return self.vertItems[ index1 ]
		return None

	def clear( self ):
		for vert in self.vertItems:
			vert.setParentItem( None )
			del self.nodeToVert[ vert.node ]
			vert.node = None
		self.vertItems = []
		self.updateSpan()

	def sortVerts( self ):
		pass

	def setZoom( self, x, y ):
		self.zx = x
		self.zy = y
		trans = QTransform()
		trans.scale( self.zx, self.zy )
		self.setTransform( trans )
		for vert in self.vertItems:
			vert.updateZoom( self.zx, self.zy )

	def updateSpan( self ):
		pass


##----------------------------------------------------------------##
class CurveView( GLGraphicsView ):
	scrollXChanged = pyqtSignal( float )
	scrollYChanged = pyqtSignal( float )
	zoomXChanged   = pyqtSignal( float )
	zoomYChanged   = pyqtSignal( float )
	cursorPosXChanged = pyqtSignal( float )
	cursorPosYChanged = pyqtSignal( float )

	vertChanged        = pyqtSignal( object, float, float )
	vertTangentChanged = pyqtSignal( object, float, float )
	
	def __init__(self, *args, **kwargs ):
		super(CurveView, self).__init__( *args, **kwargs )
		self.updating = False
		self.setScene( GLGraphicsScene() )
		self.setBackgroundBrush( _DEFAULT_BG )
		self.gridBackground = AxisGridBackground()
		self.scene().addItem( self.gridBackground )
		self.scene().sceneRectChanged.connect( self.onRectChanged )
		
		self.curveItems = []
		self.nodeToCurve = {}

		#components
		self.cursorItem = CursorItem()
		self.cursorItem.setLine( 0,-10000, 0, 20000 )
		self.cursorItem.setZValue( 1000 )
		# self.scene().addItem( self.cursorItem )

		self.rebuilding = False
		self.panning = False
		self.scrollX = 0
		self.scrollY = 0
		self.scrollXMin = None
		self.scrollXMax = None

		self.cursorX = 0
		self.cursorY = 0
		
		self.offsetX = 0

		self.zoomX = 1.0
		self.zoomY = 1.0
		self.scene().setSceneRect( QRectF( -10000,-10000, 20000, 20000 ) )
		self.setZoomX( 1 )
		self.setZoomY( 1 )
		self.setCursorVisible( True )

	def onRectChanged( self, rect ):
		self.gridBackground.setRect( rect )

	def setAxisShown( self, xAxis, yAxis ):
		self.gridBackground.showXAxis = xAxis
		self.gridBackground.showYAxis = yAxis

	def setCursorVisible( self, visible ):
		# self.cursorItem.setVisible( visible )
		self.gridBackground.cursorVisible = visible

	def setScrollXLimit( self, minX, maxX ):
		self.scrollXMin = minX
		self.scrollXMax = maxX

	def setScroll( self, x, y ):
		if not self.scrollXMin is None:
			x = max( self.scrollXMin, x )
		# if self.scrollXMin:
		# 	x = max( self.scrollXMin, x )
		self.scrollX = x
		self.scrollY = y
		self.scrollXChanged.emit( self.scrollX )
		self.scrollYChanged.emit( self.scrollY )
		self.updateTransfrom()

	def setScrollX( self, x ):
		if not self.scrollXMin is None:
			x = max( self.scrollXMin, x )
		self.scrollX = x
		self.scrollXChanged.emit( self.scrollX )
		self.updateTransfrom()

	def setOffset( self, x, y ):
		self.offsetX = x
		self.offsetY = y
		self.updateTransfrom()

	def setCursorX( self, vx ):
		self.cursorX = vx
		# self.cursorItem.setX( self.valueToX( vx ) )
		x = self.valueToX( vx )
		self.gridBackground.setCursorPosX( x )
		self.update()

	def wheelEvent(self, event):
		steps = event.delta() / 120.0;
		dx = 0
		dy = 0
		zoomRate = 1.1
		if event.orientation() == Qt.Horizontal : 
			dy = steps
			if dy>0:
				self.setZoomY( self.zoomY * zoomRate )
			else:
				self.setZoomY( self.zoomY / zoomRate )
		else:
			dy = steps
			if dy>0:
				self.setZoomX( self.zoomX * zoomRate )
			else:
				self.setZoomX( self.zoomX / zoomRate )

	def setZoomX( self, zoom ):
		self.zoomXChanged.emit( zoom )
		self.zoomX = zoom
		self.onZoomChanged()

	def setZoomY( self, zoom ):
		self.zoomYChanged.emit( zoom )
		self.zoomY = zoom
		self.onZoomChanged()

	def onZoomChanged( self ):
		for curve in self.curveItems:
			curve.setZoom( self.zoomX, self.zoomY )
		self.gridBackground.setZoom( self.zoomX, self.zoomY )
		self.updateTransfrom()
		# self.cursorItem.setX( self.valueToX( self.cursorX ) )
		self.gridBackground.setCursorPosX( self.valueToX( self.cursorX ) )

	def mouseMoveEvent( self, event ):
		super( CurveView, self ).mouseMoveEvent( event )
		if self.panning:
			p1 = event.pos()
			p0, off0 = self.panning
			dx = p0.x() - p1.x()
			dy = p0.y() - p1.y()
			offX0, offY0 = off0
			offX1 = offX0 + dx
			offY1 = offY0 + dy
			self.setScroll( self.xToValue( offX1 ), self.yToValue( offY1 ) )

	def mousePressEvent( self, event ):
		super( CurveView, self ).mousePressEvent( event )
		if event.button() == Qt.MidButton:
			offX0, offY0 = self.valueToPos( self.scrollX, self.scrollY )
			self.panning = ( event.pos(), ( offX0, offY0 ) )

	def mouseReleaseEvent( self, event ):
		super( CurveView, self ).mouseReleaseEvent( event )
		if event.button() == Qt.MidButton :
			if self.panning:
				self.panning = False

	def updateTransfrom( self ):
		if self.updating : return
		self.updating = True
		trans = QTransform()
		trans.translate( self.valueToX( -self.scrollX ) + self.offsetX, self.valueToY( -self.scrollY ) )
		self.setTransform( trans )
		self.update()
		self.updating = False

	def xToValue( self, x ):
		return  x /( _PIXEL_PER_UNIT * self.zoomX )

	def valueToX( self, v ):
		return v * self.zoomX * _PIXEL_PER_UNIT

	def yToValue( self, y ):
		return  y /( _PIXEL_PER_UNIT * self.zoomY )

	def valueToY( self, v ):
		return v * self.zoomY * _PIXEL_PER_UNIT

	def valueToPos( self, x, y ):
		return ( self.valueToX( x ), self.valueToY( y ) )

	def posToValue( self, xv, yv ):
		return ( self.xToValue( xv ), self.yToValue( yv ) )

	#====Building
	def rebuild( self ):
		self.clear()
		self.rebuilding = True
		for curveNode in self.getCurveNodes():
			self.addCurve( curveNode )
		self.rebuilding = False

	def clear( self ):
		for curve in self.curveItems:
			curve.clear()
			self.scene().removeItem( curve )
		self.curveItems = []

	def removeCurve( self, curveNode ):
		curve = self.getCurveByNode( curveNode )
		if curve:
			del self.nodeToCurve[ curveNode ]
			curve.clear()
			curve.node = None
			self.scene().removeItem( curve )
			self.curveItems.remove( curve )

	def addCurve( self, curveNode, **option ):
		curve = CurveItem( curveNode )
		self.scene().addItem( curve )
		self.curveItems.append( curve )
		self.nodeToCurve[ curveNode ] = curve

		vertNodes = self.getVertNodes( curveNode )
		if vertNodes:
			for vertNode in vertNodes:
				self.addVert( vertNode )

		curve.setZoom( self.zoomX, self.zoomY )
		self.refreshCurve( curveNode, **option )
		self.updateCurveLayout()
		return curve

	def addVert( self, vertNode, **option ):
		curve = self.affirmParentCurve( vertNode )
		if not curve: return None
		vert = curve.addVert( vertNode )
		if vert:
			self.refreshVert( vertNode, **option )			
		return vert

	def removeVert( self, vertNode ):
		curve = self.getParentCurve( vertNode )
		if not curve: return
		curve.removeVert( vertNode )
		if vertNode in self.selection:
			self.selection.remove( vertNode )

	def refreshVert( self, vertNode, **option ):
		vert = self.getVertByNode( vertNode )
		if vert:
			x, y, curveMode, tanPre, tanPost = self.getVertParam( vertNode )
			vert.setParam( x,y, curveMode, tanPre,tanPost )
			self.updateVertContent( vert, vertNode, **option )

	def refreshCurve( self, curveNode, **option ):
		curve = self.getCurveByNode( curveNode )
		if curve:
			self.updateCurveContent( curve, curveNode, **option )

	def getParentCurve( self, vertNode ):
		curveNode = self.getParentCurveNode( vertNode )
		if not curveNode: return None
		return self.getCurveByNode( curveNode )

	def getCurveByNode( self, curveNode ):
		return self.nodeToCurve.get( curveNode, None )

	def getVertByNode( self, vertNode ):
		curve = self.getParentCurve( vertNode )
		if not curve: return None
		return curve.getVertByNode( vertNode )

	def affirmParentCurve( self, vertNode ):
		curveNode = self.getParentCurveNode( vertNode )
		if not curveNode: return None
		curveItem = self.getCurveByNode( curveNode )
		if not curveItem:
			return self.addCurve( curveNode )
		else:
			return curveItem

	def updateCurveLayout( self ):
		#TODO: zoom to fit curve value range
		pass

	#====Selection====
	def initSelectionRegion( self ):
		self.selecting = False
		self.selectionRegion = SelectionRegionItem()
		self.selectionRegion.setZValue( 9999 )
		self.selectionRegion.setVisible( False )
		self.scene().addItem( self.selectionRegion )

	def startSelectionRegion( self, pos ):
		self.selecting = True
		self.selectionRegion.setPos( pos )
		self.selectionRegion.setRect( 0,0,0,0 )
		self.selectionRegion.setVisible( True )
		self.resizeSelectionRegion( pos )

	def resizeSelectionRegion( self, pos1 ):
		pos = self.selectionRegion.pos()
		w, h = pos1.x()-pos.x(), pos1.y()-pos.y()
		self.selectionRegion.setRect( 0,0, w, h )
		itemsInRegion = self.scene().items( pos.x(), pos.y(), w, h )
		for item in self.selectingItems:
			item.setSelected( False, False )

		self.selectingItems = []
		for item in itemsInRegion:
			if isinstance( item, TimelineVertItem ):
				self.selectingItems.append( item )
				item.setSelected( True, False )

	def stopSelectionRegion( self ):
		self.selectionRegion.setRect( 0,0,0,0 )
		self.selectionRegion.setVisible( False )
		selection = []
		for key in self.selectingItems:
			selection.append( key.node )

	def applySelection( self, selection ):
		pass
		# self.timelineView.updateSelection( selection )

	#====VIRTUAL FUNCTIONS ========
	def getParentCurveNode( self, vertNode ):
		return None

	def getCurveNodes( self ):
		return []

	def getVertNodes( self, curveNode ):
		return []

	def getVertParam( self, curveNode ):
		#x, y, curveMode, pre-tangent, post-tangeng
		return ( 0,0, SPAN_MODE_BEZIER, 0, 0 )

	def updateCurveContent( self, curve, node, **option ):
		pass

	def updateVertContent( self, vert, vertNode, **option ):
		pass

if __name__ == '__main__':
	from random import random
	# import testView
	##----------------------------------------------------------------##
	class TestCurve(object):
		def __init__( self ):
			self.verts = []

		def getVerts( self ):
			return self.verts

		def randomFill( self, off ):
			for i in range( 0, 4 ):
				vert = TestCurveVert( self )
				vert.x = i * 100 + random()*5
				vert.y = (random()-0.5)*100 + off
				self.verts.append( vert )


	class TestCurveVert(object):
		def __init__( self, parent ):
			self.parentCurve = parent
			self.x = 0
			self.y = 1
			self.curveMode = SPAN_MODE_BEZIER
			self.tangentPre = 90
			self.tangentPost = 90

		def getParam( self ):
			return ( self.x, self.y, self.curveMode, self.tangentPre, self.tangentPost )
	
	class TestCurveView( CurveView ):
		"""docstring for TestCurveView"""
		def __init__(self, *args):
			super(TestCurveView, self).__init__( *args )
			self.testCurves = []
			for i in range( 0, 1 ):
				curve = TestCurve()
				curve.randomFill( i * 100 )
				self.testCurves.append( curve )

		def getParentCurveNode( self, vertNode ):
			return vertNode.parentCurve

		def getCurveNodes( self ):
			return self.testCurves

		def getVertNodes( self, curveNode ):
			return curveNode.getVerts()

		def getVertParam( self, vertNode ):
			return vertNode.getParam()

	class CurveWidget( QtGui.QWidget ):
		def __init__( self, *args, **kwargs ):
			super( CurveWidget, self ).__init__( *args, **kwargs )		
			layout = QtGui.QVBoxLayout( self )
			self.view = TestCurveView()
			layout.addWidget( self.view )
			self.view.rebuild()

		def closeEvent( self, event ):
			self.view.deleteLater()
	
	app = QtGui.QApplication( sys.argv )
	styleSheetName = 'gii.qss'
	app.setStyleSheet(
			open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
		)
	view = CurveWidget()
	view.resize( 600, 300 )
	view.show()
	view.raise_()
	
	app.exec_()
