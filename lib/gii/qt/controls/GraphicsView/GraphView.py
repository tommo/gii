# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor

from GraphicsViewHelper import *

import sys
import math

class GraphViewNodeSlot( QtGui.QGraphicsRectItem ):
	_pen = makePen( color = '#3780ff' )
	_brush = QtGui.QBrush( QColor( '#dddf09' ) )

	_pen_hover = makePen( color = '#ffffff' )
	_brush_hover = QtGui.QBrush( QColor( '#dddf09' ) )

	def __init__( self ):
		super( GraphViewNodeSlot, self ).__init__()
		size = 15
		self.dir = 1
		self.setRect( -size/2, -size/2, size, size )
		self.setCursor( Qt.PointingHandCursor )
		self.connections = {}
		self._pen = GraphViewNodeSlot._pen
		self._brush = GraphViewNodeSlot._brush
		self.setAcceptHoverEvents( True )
	
	def clearConnections( self ):
		for conn in self.connections:
			if conn.srcSlot == self:
				conn.setSrcSlot( None )
			if conn.dstSlot == self:
				conn.setDstSlot( None )

	def updateConnections( self ):
		for conn in self.connections:
			conn.updatePath()

	def hoverEnterEvent( self, event ):
		self._pen = GraphViewNodeSlot._pen_hover
		self._brush = GraphViewNodeSlot._brush_hover
		self.update()
		return super( GraphViewNodeSlot, self ).hoverEnterEvent( event )

	def hoverLeaveEvent( self, event ):
		self._pen = GraphViewNodeSlot._pen
		self._brush = GraphViewNodeSlot._brush
		self.update()
		return super( GraphViewNodeSlot, self ).hoverLeaveEvent( event )

	def paint( self, painter, option, widget ):
		painter.setPen( self._pen )
		painter.setBrush( self._brush )
		rect = self.rect().adjusted(  2,2,-2,-2 )
		painter.drawEllipse( rect )

	def CPNormal( self ):
		p0 = self.scenePos()
		if self.dir == 1: #in node
			return QPointF( -1, 0 )
		elif self.dir == 2:
			return QPointF( 1, 0 )


class GraphViewNode( QtGui.QGraphicsRectItem ):
	_pen = QtGui.QPen( QColor( '#ffffff' ) )
	_brush = QtGui.QBrush( QColor( '#89b3df' ) )
	def __init__( self ):
		super( GraphViewNode, self ).__init__()
		self.slots = {}
		self.setCacheMode( QtGui.QGraphicsItem.ItemCoordinateCache )
		self.setRect( 0, 0, 100, 120 )
		self.setFlag( self.ItemIsSelectable, True )
		self.setFlag( self.ItemIsMovable, True )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.setCursor( Qt.PointingHandCursor )
		self.buildSlots()

	def getSlot( self, id ):
		return self.slots.get( id, None )

	def buildSlots( self ):
		#input
		y = 60
		for i in range( 3 ):
			slot = GraphViewNodeSlot()
			slot.setParentItem( self )
			slot.setPos( 0, y + i*20 )
			slot.dir = 1
			self.slots[ 'in-%d' % i ] = slot
		#output
		for i in range( 3 ):
			slot = GraphViewNodeSlot()
			slot.setParentItem( self )
			slot.setPos( 100, y + i*20 )
			slot.dir = 2
			self.slots[ 'out-%d' % i ] = slot

	def delete( self ):
		for slot in self.slots.values():
			slot.clearConnections()
		self.scene().removeItem( self )

	def itemChange( self, change, value ):
		if change == self.ItemPositionChange or change == self.ItemPositionHasChanged:
			for slot in self.slots.values():
				slot.updateConnections()
		return QtGui.QGraphicsRectItem.itemChange( self, change, value )

	def paint( self, painter, option, widget ):
		painter.setPen( GraphViewNode._pen )
		painter.setBrush( GraphViewNode._brush )
		rect = self.rect()
		painter.drawRoundedRect( rect, 5, 5 )
		painter.drawText( rect.translated( 1, 1 ), Qt.AlignLeft|Qt.AlignTop, 'Animation' )


class GraphViewConnection( QtGui.QGraphicsPathItem ):
	_pen = makePen( color = '#e3ff00', width = 2, style=Qt.SolidLine )
	def __init__( self, srcSlot, dstSlot ):
		super( GraphViewConnection, self ).__init__()
		self.useCurve = True
		self.srcSlot = None
		self.dstSlot = None
		self.setSrcSlot( srcSlot )
		self.setDstSlot( dstSlot )
		self.setZValue( -1 )
		self.updatePath()
		self.setPen( GraphViewConnection._pen )

	def setSrcSlot( self, slot ):
		if self.srcSlot:
			if self in self.srcSlot.connections:
				del self.srcSlot.connections[ self ]
		self.srcSlot = slot
		if slot:
			slot.connections[ self ] = True
		self.updatePath()

	def setDstSlot( self, slot ):
		if self.dstSlot:
			if self in self.dstSlot.connections:
				del self.dstSlot.connections[ self ]
		self.dstSlot = slot
		if slot:
			slot.connections[ self ] = True
		self.updatePath()

	def delete( self ):
		if self.srcSlot:
			del self.srcSlot.connections[ self ]

		if self.dstSlot:
			del self.dstSlot.connections[ self ]

		self.scene().removeItem( self )


	def updatePath( self ):
		if not ( self.srcSlot and self.dstSlot ):
			path = QtGui.QPainterPath() #empty
			self.setPath( path )
			return

		pos0 = self.srcSlot.scenePos()
		pos1 = self.dstSlot.scenePos()
		n0 = self.srcSlot.CPNormal()
		n1 = self.dstSlot.CPNormal()
		self.setPos( pos0 )
		pos1 = self.mapFromScene( pos1 )
		path = QtGui.QPainterPath()
		path.moveTo( 0, 0 )		
		dx = pos1.x()

		if self.useCurve:
			diff = abs(dx) / 2
			cpos0 = n0 * diff
			cpos1 = pos1 + n1 * diff
			path.cubicTo( cpos0, cpos1, pos1 )
		else:
			diff = dx / 4
			cpos0 = n0 * diff
			cpos1 = pos1 + n1 * diff
			path.lineTo( cpos0 )
			path.lineTo( cpos1 )
			path.lineTo( pos1 )				

		self.setPath( path )


class GraphScene( QtGui.QGraphicsScene ):
	def __init__( self, parent ):
		super( GraphScene, self ).__init__( parent = parent )
		dummySlot = GraphViewNodeSlot()
		dummySlot.setFlag( dummySlot.ItemHasNoContents, True )
		dummySlot.hide()
		self.dummySlot = dummySlot
		self.addItem( dummySlot )
		self.connecting = None
		self.gridBackground = GridBackground()
		self.addItem( self.gridBackground )
		self.sceneRectChanged.connect( self.onRectChanged )

	def onRectChanged( self, rect ):
		self.gridBackground.setRect( rect )

	def tryStartConnection( self, slot ):
		targetSlot = self.dummySlot
		conn = GraphViewConnection( slot, targetSlot )
		if slot.dir == 1:
			targetSlot.dir = 2
		else:
			targetSlot.dir = 1
		self.addItem( conn )
		self.connecting = conn
		return True

	def mousePressEvent( self, event ):
		item = self.itemAt( event.scenePos() )
		if not item: return
		if isinstance( item, GraphViewNodeSlot ):
			self.dummySlot.setPos( event.scenePos() )
			if self.tryStartConnection( item ): return
		super( GraphScene, self ).mousePressEvent( event )

	def mouseMoveEvent( self, event ):
		if self.connecting:
			if event.scenePos().x() > self.connecting.srcSlot.scenePos().x():
				self.dummySlot.dir = 1
			else:
				self.dummySlot.dir = 2
			self.dummySlot.setPos( event.scenePos() )
			self.dummySlot.updateConnections()
		super( GraphScene, self ).mouseMoveEvent( event )

	def mouseReleaseEvent( self, event ):
		if self.connecting:
			self.dummySlot.setPos( event.scenePos() )
			item = self.itemAt( event.scenePos() )
			if isinstance( item, GraphViewNodeSlot ):
				self.connecting.setDstSlot( item )
			else:
				self.connecting.delete()
			self.connecting = None
		super( GraphScene, self ).mouseReleaseEvent( event )

class GraphView( GLGraphicsView ):
	def __init__( self, *args, **kwargs ):
		super( GraphView, self ).__init__( *args, **kwargs )
	

class GraphWidget( QtGui.QWidget ):
	def __init__( self, *args, **kwargs ):
		super( GraphWidget, self ).__init__( *args, **kwargs )		
		layout = QtGui.QVBoxLayout( self )

		self.scene = GraphScene( parent = self )
		self.scene.setBackgroundBrush( Qt.black );
		self.view = GraphView( self.scene, parent = self )
		self.view.setSceneRect( QRectF( 0,0, 10000, 10000 ) )
		layout.addWidget( self.view )
		self.testData()

	def testData( self ):
		node1 = GraphViewNode()
		self.scene.addItem( node1 )
		node2 = GraphViewNode()
		self.scene.addItem( node2 )
		node3 = GraphViewNode()
		self.scene.addItem( node3 )
		node1.setPos( 200, 100 )
		conn = GraphViewConnection( node1.getSlot( 'out-1' ), node2.getSlot( 'in-0' ) )
		self.scene.addItem( conn )
		conn = GraphViewConnection( node2.getSlot( 'out-1' ), node3.getSlot( 'in-0' ) )
		self.scene.addItem( conn )

	def closeEvent( self, event ):
		self.view.deleteLater()

	def __del__( self ):
		self.deleteLater()


if __name__ == '__main__':
	app = QtGui.QApplication( sys.argv )
	styleSheetName = 'gii.qss'
	app.setStyleSheet(
			open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
		)

	g = GraphWidget()
	g.resize( 600, 300 )
	g.show()
	g.raise_()
	# Graph.setZoom( 10 )
	# Graph.selectTrack( dataset[1] )

	app.exec_()
