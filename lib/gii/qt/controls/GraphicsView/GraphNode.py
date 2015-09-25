# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform

from GraphicsViewHelper import *

import sys
import math


##----------------------------------------------------------------##
class GraphNodeGroup( QtGui.QGraphicsRectItem ):
	_pen   = makePen( color = '#808080', style = Qt.DashLine )
	_brush = makeBrush( color = '#1a1a1a' )
	def __init__( self ):
		super(GraphNodeGroup, self).__init__()
		self.title = 'Group'
		self.setRect( 0,0, 400, 400 )
		self.setFlag( self.ItemIsSelectable, True )
		self.setFlag( self.ItemIsMovable, True )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.setFlag( self.ItemClipsChildrenToShape, True )
		self.setZValue( -100 )

	def getTitle( self ):
		return self.title

	def setTitle( self, title ):
		self.title = title

	def paint( self, painter, option, widget ):
		painter.setPen( GraphNodeGroup._pen )
		painter.setBrush( GraphNodeGroup._brush )
		rect = self.rect()
		painter.drawRoundedRect( rect, 10, 10 )
		trect = rect.adjusted( 10, 10, -4, -4 )
		painter.drawText( trect, Qt.AlignLeft|Qt.AlignTop, self.getTitle() )


##----------------------------------------------------------------##
class GraphNodePort( QtGui.QGraphicsRectItem ):
	_pen = makePen( color = '#a4a4a4' )
	_brush = makeBrush( color = '#000000' )
	_pen_text = makePen( color = '#ffffff' )

	_pen_hover = makePen( color = '#ffffff' )
	_brush_hover = makeBrush( color = '#000000' )

	_pen_fill = Qt.NoPen
	_brush_fill = makeBrush( color = '#ffffff' )

	def __init__( self ):
		super( GraphNodePort, self ).__init__()
		size = 16
		self.dir = -1
		self.setRect( -size/2, -size/2, size, size )
		self.setCursor( Qt.PointingHandCursor )
		self.connections = {}
		self._pen = GraphNodePort._pen
		self._brush = GraphNodePort._brush
		self.setAcceptHoverEvents( True )

	def getText( self ):
		return 'X'
	
	def clearConnections( self ):
		for conn in self.connections:
			if conn.srcPort == self:
				conn.setSrcPort( None )
			if conn.dstPort == self:
				conn.setDstPort( None )

	def updateConnections( self ):
		for conn in self.connections:
			conn.updatePath()

	def hasConnection( self ):
		if self.connections:
			return True
		else:
			return False

	def hoverEnterEvent( self, event ):
		self._pen = GraphNodePort._pen_hover
		self._brush = GraphNodePort._brush_hover
		self.update()
		return super( GraphNodePort, self ).hoverEnterEvent( event )

	def hoverLeaveEvent( self, event ):
		self._pen = GraphNodePort._pen
		self._brush = GraphNodePort._brush
		self.update()
		return super( GraphNodePort, self ).hoverLeaveEvent( event )

	def paint( self, painter, option, widget ):
		painter.setPen( self._pen )
		painter.setBrush( self._brush )
		rect = self.rect()
		painter.drawEllipse( rect.adjusted(  2,2,-2,-2 ) )
		if self.hasConnection():
			painter.setPen( GraphNodePort._pen_fill )
			painter.setBrush( GraphNodePort._brush_fill )
			painter.drawEllipse( -3,-3,6,6 )
		text = self.getText()
		painter.setPen( GraphNodePort._pen_text )
		if self.dir == -1: #in
			trect = QRect( rect.right() + 2, rect.top(), 100, 20 )
			painter.drawText( trect, Qt.AlignLeft|Qt.AlignVCenter, text )
		elif self.dir == 1: #out
			trect = QRect( rect.left() - 2 -100, rect.top(), 100, 20 )
			painter.drawText( trect, Qt.AlignRight|Qt.AlignVCenter, text )


	def CPNormal( self ):
		p0 = self.scenePos()
		if self.dir == -1: #in node
			return QPointF( -1, 0 )
		elif self.dir == 1: #out node
			return QPointF( 1, 0 )
		else:
			raise Exception( 'invalid port dir: %d' % self.dir )


##----------------------------------------------------------------##
class GraphNodeHeader( QtGui.QGraphicsRectItem ):
	_pen = Qt.NoPen
	_textPen = makePen( color = '#ffffff' )
	_brush = makeBrush( color = '#3a3a3a' )
	def __init__( self ):
		super( GraphNodeHeader, self ).__init__()
		self.headerText = u'アバンシュPeut-être'
		self.headerHeight = 20
		self.setCursor( Qt.PointingHandCursor )


	def setText( self, t ):
		self.headerText = t

	def getText( self ):
		return self.headerText

	def updateShape( self ):
		rect = self.parentItem().rect()
		rect.setHeight( self.headerHeight )
		rect.adjust( 1,1,-1,0)
		self.setRect( rect )

	def paint( self, painter, option, widget ):
		painter.setPen( Qt.NoPen )
		painter.setBrush( GraphNodeHeader._brush )
		rect = self.rect()
		painter.drawRect( rect )
		trect = rect.adjusted( 4, 2, 0, 0 )
		painter.setPen( GraphNodeHeader._textPen )
		painter.drawText( trect, Qt.AlignLeft|Qt.AlignVCenter, self.getText() )



##----------------------------------------------------------------##
_GraphNodeZValue = 10
class GraphNode( QtGui.QGraphicsRectItem ):
	_pen = QtGui.QPen( QColor( '#a4a4a4' ) )
	_brush = makeBrush( color = '#676767' )
	def __init__( self ):
		super( GraphNode, self ).__init__()
		self.inPortDict = {}
		self.outPortDict = {}
		self.inPorts  = []
		self.outPorts = []
		self.header = self.createHeader()
		self.header.setParentItem( self )
		self.setCacheMode( QtGui.QGraphicsItem.ItemCoordinateCache )
		self.setRect( 0, 0, 100, 120 )
		self.setFlag( self.ItemIsSelectable, True )
		self.setFlag( self.ItemIsMovable, True )
		self.setFlag( self.ItemSendsGeometryChanges, True )
		self.setAcceptHoverEvents( True )
		self.setCursor( Qt.PointingHandCursor )
		self.buildPorts()
		self.setZValue( _GraphNodeZValue )
		self.updateShape()

	def createHeader( self ):
		return GraphNodeHeader()

	def getHeader( self ):
		return self.header

	def getInPort( self, id ):
		return self.inPortDict.get( id, None )

	def getOutPort( self, id ):
		return self.outPortDict.get( id, None )

	def addInPort( self, key, port ):
		port.dir = -1
		port.setParentItem( self )
		port.key = key
		self.inPortDict[ key ] = port
		self.inPorts.append( port )

	def addOutPort( self, key, port ):
		port.dir = 1
		port.setParentItem( self )
		port.key = key
		self.outPortDict[ key ] = port
		self.outPorts.append( port )

	def buildPorts( self ):
		#input
		for i in range( 4 ):
			port = GraphNodePort()
			self.addInPort( 'p%d'%i, port )
		#output
		for i in range( 2 ):
			port = GraphNodePort()
			self.addOutPort( 'p%d'%i, port )

	def updateShape( self ):
		h = self.rect().height()
		row = max( len(self.inPorts), len(self.outPorts) )
		rowSize = 20
		headerSize = 20
		headerMargin = 10
		footerMargin = 10
		minHeight = 20
		nodeWidth = 120
		totalHeight = max( row * rowSize, minHeight ) + headerMargin + headerSize + footerMargin
		y0 = headerMargin + headerSize
		self.setRect( 0,0, nodeWidth, totalHeight )

		for i, port in enumerate( self.inPorts ):
			port.setPos( 1, y0 + i*rowSize + rowSize/2 )

		for i, port in enumerate( self.outPorts ):
			port.setPos( nodeWidth - 1, y0 + i*rowSize + rowSize/2 )

		self.header.updateShape()

	def delete( self ):
		for port in self.inPorts:
			port.clearConnections()
		for port in self.outPorts:
			port.clearConnections()
		self.scene().removeItem( self )

	def itemChange( self, change, value ):
		if change == self.ItemPositionChange or change == self.ItemPositionHasChanged:
			for port in self.inPorts:
				port.updateConnections()
			for port in self.outPorts:
				port.updateConnections()

		return QtGui.QGraphicsRectItem.itemChange( self, change, value )

	def mousePressEvent( self, ev ):
		global _GraphNodeZValue 
		_GraphNodeZValue += 0.000001 #shitty reordering
		self.setZValue( _GraphNodeZValue )
		return super( GraphNode, self ).mousePressEvent( ev )

	def paint( self, painter, option, widget ):
		rect = self.rect()
		painter.setPen( GraphNode._pen )
		painter.setBrush( GraphNode._brush )
		painter.drawRoundedRect( rect, 3,3 )


##----------------------------------------------------------------##
class GraphNodeConnection( QtGui.QGraphicsPathItem ):
	_pen                  = makePen( color = '#ffffff', width = 1 )
	_brush_arrow          = makeBrush( color = '#ffffff' )
	_pen_selected         = makePen( color = '#ff4700', width = 2 )
	_brush_arrow_selected = makeBrush( color = '#ff4700' )
	_polyTri = QtGui.QPolygonF([
			QPointF(  0,   0 ),
			QPointF( -12, -6 ),
			QPointF( -12,  6 ),
			])
	def __init__( self, srcPort, dstPort ):
		super( GraphNodeConnection, self ).__init__()
		self.useCurve = True
		self.srcPort = None
		self.dstPort = None
		self.setSrcPort( srcPort )
		self.setDstPort( dstPort )
		self.setZValue( -1 )
		self.updatePath()
		self.setPen( GraphNodeConnection._pen )
		self.setCursor( Qt.PointingHandCursor )
		self.setAcceptHoverEvents( True )
		self.selected = False

	def setSrcPort( self, port ):
		if self.srcPort:
			self.srcPort.update()
			if self in self.srcPort.connections:
				del self.srcPort.connections[ self ]
		self.srcPort = port
		if port:
			port.connections[ self ] = True
			port.update()
		self.updatePath()

	def setDstPort( self, port ):
		if self.srcPort == port: return False
		if self.dstPort:
			self.dstPort.update()
			if self in self.dstPort.connections:
				del self.dstPort.connections[ self ]
		self.dstPort = port
		if port:
			port.connections[ self ] = True
			port.update()
		self.updatePath()
		return True

	def delete( self ):
		if self.srcPort:
			del self.srcPort.connections[ self ]

		if self.dstPort:
			del self.dstPort.connections[ self ]

		self.scene().removeItem( self )


	def updatePath( self ):
		if not ( self.srcPort and self.dstPort ):
			path = QtGui.QPainterPath() #empty
			self.setPath( path )
			return

		pos0 = self.srcPort.scenePos()
		pos1 = self.dstPort.scenePos()
		n0 = self.srcPort.CPNormal()
		n1 = self.dstPort.CPNormal()
		self.setPos( pos0 )
		pos1 = self.mapFromScene( pos1 )
		path = QtGui.QPainterPath()
		path.moveTo( 0, 0 )		
		dx = pos1.x()

		if self.useCurve:
			diff = abs(dx) * 0.7
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

	def paint( self, painter, option, widget ):
		if self.selected:
			self.setPen( GraphNodeConnection._pen_selected )
		else:
			self.setPen( GraphNodeConnection._pen )

		super( GraphNodeConnection, self ).paint( painter, option, widget )
		#draw arrow
		path = self.path()
		midDir   = path.angleAtPercent( 0.7 )
		midPoint = path.pointAtPercent( 0.7 )
		trans = QTransform()
		trans.translate( midPoint.x(), midPoint.y() )
		trans.rotate( -midDir )
		painter.setTransform( trans, True )
		if self.selected:
			painter.setBrush( GraphNodeConnection._brush_arrow_selected )
		else:
			painter.setBrush( GraphNodeConnection._brush_arrow )
		painter.drawPolygon( GraphNodeConnection._polyTri )

	def mousePressEvent( self, ev ):
		if ev.button() == Qt.LeftButton:
			self.selected = True
			self.update()
		return super( GraphNodeConnection, self ).mousePressEvent( ev )

	def mouseReleaseEvent( self, ev ):
		if ev.button() == Qt.LeftButton:
			self.selected = False
			self.update()
		return super( GraphNodeConnection, self ).mouseReleaseEvent( ev )



if __name__ == '__main__':
	import TestGraphView
	