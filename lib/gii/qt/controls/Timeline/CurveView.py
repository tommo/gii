import sys
import math

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform, QStyle
from OpenGL.GL import *

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
makeStyle( 'cv',                '#ffffff',    '#acbcff'              )
makeStyle( 'tp',                dict( color = '#b940d6', alpha=0.5 ),    '#b940d6'    )
makeStyle( 'curve',             '#c1ff03',    None             )



##----------------------------------------------------------------##
SPAN_MODE_CONSTANT = 0
SPAN_MODE_LINEAR   = 1
SPAN_MODE_BEZIER   = 2

TANGENT_MODE_AUTO    = 0
TANGENT_MODE_SPLIT   = 1
TANGENT_MODE_SMOOTH  = 2


##----------------------------------------------------------------##
class CursorLine( QtGui.QGraphicsLineItem ):
	_pen  = makePen( color = '#9cff00', width = 1 )
	def __init__( self ):
		super( CursorLine, self ).__init__()
		self.setPen( self._pen )

	def paint( self, painter, option, widget ):
		painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
		super( CursorLine, self ).paint( painter, option, widget )

##----------------------------------------------------------------##
class AxisGridBackground( QtGui.QGraphicsRectItem ):
	_gridPen  = makePen( color = '#333', width = 1 )
	_axisPen  = makePen( color = '#777', width = 1 )
	_originPen  = makePen( color = '#49599c', width = 1 )
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


	def setOffset( self, x, y ):
		self.offsetX = x
		self.offsetY = y
		self.updateTransfrom()

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
		painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
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

	def setZoom( self, zx, zy ):
		self.zoomX = zx
		self.zoomY = zy
		self.update()

##----------------------------------------------------------------##
class CurveSpanItem( QtGui.QGraphicsPathItem ):
	def setVertex( self, startVert, endVert ):
		self.startVert = startVert
		self.endVert   = endVert
		self.updateShape()
		applyStyle( 'curve', self )

	def updateShape( self ):
		mode = self.startVert.spanMode
		if mode == SPAN_MODE_CONSTANT:
			self.startVert.postTP.hide()
			self.endVert.preTP.hide()
			self.updateConstantCurve()
		if mode == SPAN_MODE_LINEAR:
			self.startVert.postTP.hide()
			self.endVert.preTP.hide()
			self.updateLinearCurve()
		if mode == SPAN_MODE_BEZIER:
			self.startVert.postTP.show()
			self.endVert.preTP.show()
			self.updateBezierCurve()

	def updateLinearCurve( self ):
		path = QtGui.QPainterPath()
		pos0 = self.startVert.scenePos()
		pos1 = self.endVert.scenePos()
		pos0 = self.mapFromScene( pos0 )
		self.setPos( pos0 )
		pos1 = self.mapFromScene( pos1 )
		path.moveTo( 0, 0 )
		path.lineTo( pos1 )
		self.setPath( path )

	def updateConstantCurve( self ):
		path = QtGui.QPainterPath()
		pos0 = self.startVert.scenePos()
		pos1 = self.endVert.scenePos()
		pos0 = self.mapFromScene( pos0 )
		self.setPos( pos0 )
		pos1 = self.mapFromScene( pos1 )
		path.moveTo( 0, 0 )
		path.lineTo( pos1.x(), 0 )
		path.lineTo( pos1 )
		self.setPath( path )

	def updateBezierCurve( self ):
		path = QtGui.QPainterPath()
		pos0 = self.startVert.scenePos()
		pos1 = self.endVert.scenePos()
		pos0 = self.mapFromScene( pos0 )
		self.setPos( pos0 )
		pos1 = self.mapFromScene( pos1 )
		tp0 = self.startVert.getPostTP() # + (0,0)
		preTP = self.endVert.getPreTP() + pos1
		path.moveTo( 0, 0 )
		path.cubicTo( tp0, preTP, pos1 )
		self.setPath( path )

	def paint( self, painter, option, widget ):
		painter.setRenderHint( QtGui.QPainter.Antialiasing, True )
		applyStyle( 'curve', painter)
		path = self.path()
		painter.drawPath( path )

class CurveTangentPointItem( QtGui.QGraphicsRectItem ):
	def __init__( self ):
		super( CurveTangentPointItem, self ).__init__()
		self.setZValue( 9 )
		self.setRect( -TP_SIZE/2, -TP_SIZE/2, TP_SIZE, TP_SIZE )
		self.innerRect = QRectF( -TP_INNER_SIZE/2, -TP_INNER_SIZE/2, TP_INNER_SIZE, TP_INNER_SIZE )
		self.setCursor( Qt.PointingHandCursor )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.setFlag( self.ItemIsMovable, True )

	def itemChange( self, change, value ):
		if change == self.ItemPositionChange or change == self.ItemPositionHasChanged:
			self.parentItem().onTPUpdate( self )
		return super( CurveTangentPointItem, self ).itemChange( change, value )

	def paint( self, painter, option, widget ):
		applyStyle( 'tp', painter )
		painter.drawEllipse( self.innerRect )

class CurveVertPointItem( QtGui.QGraphicsRectItem ):
	def __init__( self, vertItem ):
		super( CurveVertPointItem, self ).__init__()
		self.setZValue( 10 )
		self.setRect( -CV_SIZE/2, -CV_SIZE/2, CV_SIZE, CV_SIZE )
		self.innerRect = QRectF( -CV_INNER_SIZE/2, -CV_INNER_SIZE/2, CV_INNER_SIZE, CV_INNER_SIZE )
		self.setCursor( Qt.PointingHandCursor )
		applyStyle( 'cv', self )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.setFlag( self.ItemIsMovable, True )
		self.vertItem = vertItem
		self.setParentItem( vertItem.parentItem() )

	def itemChange( self, change, value ):
		if change == self.ItemPositionChange or change == self.ItemPositionHasChanged:
			self.vertItem.setPos( self.pos() )
		return super( CurveVertPointItem, self ).itemChange( change, value )

	def paint( self, painter, option, widget ):
		applyStyle( 'cv', painter )
		painter.drawRect( self.innerRect )

class CurveVertItem( QtGui.QGraphicsRectItem ):
	def __init__( self, parent ):
		super( CurveVertItem, self ).__init__()
		self.setParentItem( parent )
		self.setZValue( 10 )
		self.setRect( -CV_SIZE/2, -CV_SIZE/2, CV_SIZE, CV_SIZE )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.updating = False

		self.value    = 0.0
		self.nextVert = None
		self.prevVert = None
		self.span = None
		self.spanMode = SPAN_MODE_LINEAR
		# self.tangentMode = 

		self.preTP  = CurveTangentPointItem()
		self.postTP = CurveTangentPointItem()
		self.preTP.setParentItem( self )
		self.postTP.setParentItem( self )
		self.preTP.setPos( -100,50 )
		self.postTP.setPos( 50, 0 )
		self.preTP.hide()
		self.postTP.hide()

		self.VP = CurveVertPointItem( self )

	def updateZoom( self, zx, zy ):
		trans = QTransform()
		trans.scale( 1.0/zx, 1.0/zy )
		self.setTransform( trans )
		self.VP.setTransform( trans )

	def setValue( self, v ):
		self.value = v

	def getPostTP( self ):
		return self.postTP.pos()

	def getPreTP( self ):
		return self.preTP.pos()

	def createSpan( self ):
		span = CurveSpanItem()
		span.setParentItem( self.parentItem() )
		span.setVertex( self, self.nextVert )
		self.span = span
		pass

	def itemChange( self, change, value ):		
		if change == self.ItemPositionChange or change == self.ItemPositionHasChanged:
			if not self.updating:
				self.updating = True
				self.VP.setPos( self.pos() )
				self.updateSpan()
				self.updating = False

		return QtGui.QGraphicsRectItem.itemChange( self, change, value )

	def onTPUpdate( self, tp ):
		# self.correctTP()
		self.updateSpan()

	def correctTP( self ):
		self.correctPreTP()
		self.correctPostTP()

	def correctPreTP( self ):
		tp = self.preTP
		x0 = -100.0
		x1 = 0.0
		if self.prevVert:
			x0 = - ( ( self.x() - self.prevVert.x() ) - self.prevVert.postTP.x()  )
		tp.setFlag( self.ItemSendsGeometryChanges, False )
		x = max( x0, min( x1, tp.x() ) )
		tp.setX( x )
		tp.setFlag( self.ItemSendsGeometryChanges, True )

	def correctPostTP( self ):
		tp = self.postTP
		x0 = 0.0
		x1 = 100.0
		if self.nextVert:
			x1 = ( self.nextVert.x() - self.x() ) + self.nextVert.preTP.x()
		tp.setFlag( self.ItemSendsGeometryChanges, False )
		x = max( x0, min( x1, tp.x() ) )
		tp.setX( x )
		tp.setFlag( self.ItemSendsGeometryChanges, True )

	def updateSpan( self ):
		if self.span:
			self.span.updateShape()

		if self.prevVert and self.prevVert.span:
			self.prevVert.span.updateShape()

		bx = ( self.preTP.x(), self.postTP.x(), 0.0 )
		by = ( self.preTP.y(), self.postTP.y(), 0.0 )
		x0 = min( bx )
		y0 = min( by )
		x1 = max( bx )
		y1 = max( by )
		self.setRect( x0,y0,x1-x0,y1-y0 )		

	def paint( self, painter, option, widget ):
		applyStyle( 'tp', painter)
		if self.preTP.isVisible():
			painter.drawLine( 0,0, self.preTP.x(), self.preTP.y() )
		if self.postTP.isVisible():
			painter.drawLine( 0,0, self.postTP.x(), self.postTP.y() )

	def setSpanMode( self, mode ):
		self.spanMode = mode
		# self.updateSpan()

class CurveItem( QtGui.QGraphicsRectItem ):
	def __init__(self):
		super(CurveItem, self).__init__()
		self.zx = 1
		self.zy = 1
		self.verts = []
		self.startVert = self.createVert()
		self.endVert   = self.startVert


	def createVert( self ):
		vert = CurveVertItem( self )
		vert.updateZoom( self.zx, self.zy )
		return vert

	def appendVert( self ):
		vert = self.createVert()
		vert0 = self.endVert
		vert0.nextVert = vert
		vert.prevVert = vert0
		self.endVert = vert
		vert0.createSpan()
		return vert

	def sortVerts( self ):
		pass

	def setZoom( self, x, y ):
		self.zx = x
		self.zy = y
		trans = QTransform()
		trans.scale( self.zx, self.zy )
		self.setTransform( trans )
		vert = self.startVert
		while vert:
			vert.updateZoom( self.zx, self.zy )
			vert = vert.nextVert

##----------------------------------------------------------------##
class CurveView( GLGraphicsView ):
	scrollXChanged = pyqtSignal( float )
	scrollYChanged = pyqtSignal( float )
	zoomXChanged   = pyqtSignal( float )
	zoomYChanged   = pyqtSignal( float )
	def __init__(self, *args, **kwargs ):
		super(CurveView, self).__init__( *args, **kwargs )
		self.updating = False
		self.setScene( QtGui.QGraphicsScene() )
		self.setBackgroundBrush( _DEFAULT_BG )
		self.curves = []
		self.gridBackground = AxisGridBackground()
		self.scene().addItem( self.gridBackground )
		self.scene().sceneRectChanged.connect( self.onRectChanged )
		
		#components
		self.cursorLine = CursorLine()
		self.cursorLine.setLine( 0,-10000, 0, 20000 )
		self.cursorLine.setZValue( 1000 )
		self.scene().addItem( self.cursorLine )

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

	def onRectChanged( self, rect ):
		self.gridBackground.setRect( rect )

	def setAxisShown( self, xAxis, yAxis ):
		self.gridBackground.showXAxis = xAxis
		self.gridBackground.showYAxis = yAxis

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

	def addCurve( self ):
		curve = CurveItem()
		self.scene().addItem( curve )
		self.curves.append( curve )
		curve.setZoom( self.zoomX, self.zoomY )
		return curve

	def setCursorX( self, vx ):
		self.cursorX = vx
		self.cursorLine.setX( self.valueToX( vx ) )

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
		for curve in self.curves:
			curve.setZoom( self.zoomX, self.zoomY )
		self.gridBackground.setZoom( self.zoomX, self.zoomY )
		self.updateTransfrom()
		self.cursorLine.setX( self.valueToX( self.cursorX ) )

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
				# self.setCursor( Qt.ArrowCursor )

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

##----------------------------------------------------------------##
class CurveWidget( QtGui.QWidget ):
	def __init__( self, *args, **kwargs ):
		super( CurveWidget, self ).__init__( *args, **kwargs )		
		layout = QtGui.QVBoxLayout( self )
		self.view = CurveView()
		layout.addWidget( self.view )

		c = self.view.addCurve()
		c.startVert.setPos( 100, 50 )
		v = c.appendVert()
		v.setPos( 150,  50 )
		v.setSpanMode( SPAN_MODE_BEZIER )
		v = c.appendVert()
		v.setPos( 250,  50 )
		v.setSpanMode( SPAN_MODE_BEZIER )
		v = c.appendVert()
		v.setPos( 350,  120 )

	def closeEvent( self, event ):
		self.view.deleteLater()

if __name__ == '__main__':
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
