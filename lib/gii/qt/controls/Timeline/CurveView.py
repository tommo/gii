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

	# def paint( self, painter, option, widget ):
	# 	painter.setRenderHint( QtGui.QPainter.Antialiasing, True )
	# 	applyStyle( 'curve', painter)
	# 	path = self.path()
	# 	painter.drawPath( path )


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
		self.spanMode = SPAN_MODE_BEZIER
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
				self.correctTP()
				self.updateSpan()
				self.updating = False

		return QtGui.QGraphicsRectItem.itemChange( self, change, value )

	def onTPUpdate( self, tp ):
		self.correctTP()
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
		self.verts = []
		self.startVert = self.createVert()
		self.endVert   = self.startVert

	def createVert( self ):
		vert = CurveVertItem( self )
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


class CurveView( GLGraphicsView ):
	def __init__(self):
		super(CurveView, self).__init__()
		self.setScene( QtGui.QGraphicsScene() )
		self.setBackgroundBrush( _DEFAULT_BG )
		self.curves = []
		self.gridBackground = GridBackground()
		self.scene().addItem( self.gridBackground )
		self.scene().sceneRectChanged.connect( self.onRectChanged )
	
	def onRectChanged( self, rect ):
		self.gridBackground.setRect( rect )

	def addCurve( self ):
		curve = CurveItem()
		self.scene().addItem( curve )
		self.curves.append( curve )
		return curve


class CurveWidget( QtGui.QWidget ):
	def __init__( self, *args, **kwargs ):
		super( CurveWidget, self ).__init__( *args, **kwargs )		
		layout = QtGui.QVBoxLayout( self )
		self.view = CurveView()
		self.view.setSceneRect( QRectF( 0,0, 10000, 10000 ) )
		layout.addWidget( self.view )

		c = self.view.addCurve()
		c.setPos( 20, 50 )
		v = c.appendVert()
		v.setPos( 150,  50 )
		v = c.appendVert()
		v.setPos( 250,  20 )
		v.setSpanMode( SPAN_MODE_LINEAR )
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
