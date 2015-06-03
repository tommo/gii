from xml.dom import minidom, Node

def _getFirstNodeOfTag( xmlNode, tagName ):
	nodes = xmlNode.getElementsByTagName( tagName )
	return nodes and nodes[0]

##----------------------------------------------------------------##
class YEdGraph():
	def __init__( self ):
		self.nodes = {}
		self.edges = {}

	def addNode( self, id, groupNode ):
		node = YEdGraphNode()
		node.graph = self
		node.id = id
		if groupNode:
			node.group = groupNode
			groupNode.children.append( node )
		self.nodes[ id ] = node
		return node

	def addGroup( self, id, groupNode ):
		group = YEdGraphGroup()
		group.graph = self
		group.id = id
		self.nodes[ id ] = group
		if groupNode:
			group.group = groupNode
			groupNode.children.append( group )
		return group

	def addEdgeByNodeId( self, nodeIdSrc, nodeIdDst ):
		fullname = '%s>%s' % ( nodeIdSrc, nodeIdDst )
		nodeSrc = self.nodes[ nodeIdSrc ]
		nodeDst = self.nodes[ nodeIdDst ]
		edge = YEdGraphEdge(nodeSrc, nodeDst)
		self.edges[ fullname ] = edge
		return edge

##----------------------------------------------------------------##
class YEdGraphItem( object ):
	def __init__( self ):
		self.attrs = {}

	def getAttr( self, key, default = None ):
		return self.attrs.get( key, default )

	def setAttr( self, key, value ):
		# print key, value
		self.attrs[ key ] = value

##----------------------------------------------------------------##
class YEdGraphNode( YEdGraphItem ):
	def __init__( self ):
		super( YEdGraphNode, self ).__init__()
		self.graph = None
		self.group = None
		self.edgesSelf  = []
		self.edgesOther = []

##----------------------------------------------------------------##
class YEdGraphGroup( YEdGraphNode ):
	def __init__( self ):
		super( YEdGraphGroup, self ).__init__()
		self.children = []

##----------------------------------------------------------------##
class YEdGraphEdge( YEdGraphItem ):
	def __init__( self, nodeSrc, nodeDst ):
		super( YEdGraphEdge, self ).__init__()
		self.nodeSrc = nodeSrc
		self.nodeDst = nodeDst
		nodeSrc.edgesSelf.append( self )
		nodeDst.edgesOther.append( self )

##----------------------------------------------------------------##
class YEdGraphMLParser( object ):
	def parseItemData( self, item, domNode ):
		keyInfos = self.keyInfos
		for childNode in domNode.childNodes:
			if childNode.nodeType != Node.ELEMENT_NODE : continue
			if childNode.tagName != 'data': continue
			keyId = childNode.getAttribute("key")
			keyInfo = keyInfos.get( keyId, None )
			if not keyInfo: continue
			kt = keyInfo['type']
			if kt == '_RES_':
				rt = keyInfo['res_type']
				if rt == 'nodegraphics':
					self.parseNodeGraphics( item, childNode )
				elif rt == 'edgegraphics':
					self.parseEdgeGraphics( item, childNode )
			else:
				name = keyInfo['name']
				if kt == 'string':
					item.setAttr( name, childNode.firstChild and unicode( childNode.firstChild.data ) or '' )
				else:
					pass

	def parseGroup( self, g, graph, groupNode ):
		name = graph.getAttribute('id')
		for childNode in graph.childNodes:
			if childNode.nodeType != Node.ELEMENT_NODE: continue
			if childNode.tagName != 'node': continue
			nodeId = childNode.getAttribute('id')
			if childNode.getAttribute('yfiles.foldertype') == 'group':
				n = g.addGroup( nodeId, groupNode )
				self.parseItemData( n, childNode )
				subGraph = childNode.getElementsByTagName("graph")[0]
				self.parseGroup( g, subGraph, n )
			else:
				n = g.addNode( nodeId, groupNode )
				self.parseItemData( n, childNode )

	def parse( self, path ):
		dom   = minidom.parse(open(path, 'r'))
		root  = dom.getElementsByTagName("graphml")[0]

		g = YEdGraph()

		keyInfos = {}
		self.keyInfos = keyInfos

		for keyData in root.getElementsByTagName( "key" ):
			id  = keyData.getAttribute('id')
			use = keyData.getAttribute('for')
			if keyData.hasAttribute('attr.name'):
				keyName = keyData.getAttribute( 'attr.name' )
				keyType = keyData.getAttribute( 'attr.type' )
				keyInfos[ id ] = {
					'name': keyName,
					'type': keyType,
					'use' : use
				}
			elif keyData.hasAttribute('yfiles.type'):
				fileType = keyData.getAttribute( 'yfiles.type' )
				keyInfos[ id ] = {
					'name': id,
					'type': '_RES_',
					'res_type': fileType,
					'use' : use
				}

		graphs = root.getElementsByTagName("graph")
		topGraph = graphs[0]
		self.parseGroup( g, topGraph, None )
		
		for graph in graphs:	# Get edges
			for childNode in graph.childNodes:
				if childNode.nodeType != Node.ELEMENT_NODE: continue
				if childNode.tagName != 'edge': continue
				source = childNode.getAttribute('source')
				dest   = childNode.getAttribute('target')
				e = g.addEdgeByNodeId(source, dest)
				self.parseItemData( e, childNode )

		return g

	def parseNodeGraphics( self, node, attr ):
		if isinstance( node, YEdGraphGroup ):
			shapeNode = attr.getElementsByTagName('y:GroupNode')[0]
		else:
			shapeNode = attr.childNodes[1]
			#label
		labelNode = _getFirstNodeOfTag( shapeNode, 'y:NodeLabel' )
		if labelNode : self.parseLabelNode( node, labelNode )

		geomNode = _getFirstNodeOfTag( shapeNode, 'y:Geometry' )
		if geomNode : self.parseGeometryNode( node, geomNode )
		

	def parseEdgeGraphics( self, edge, attr ):
		edgeNode = attr.childNodes[1]

		labelNode = _getFirstNodeOfTag( edgeNode, 'y:NodeLabel' )
		if labelNode : self.parseLabelNode( edge, labelNode )

		pathNode = _getFirstNodeOfTag( edgeNode, 'y:Path' )
		if pathNode: self.parsePathNode( edge, pathNode )

		styleNode = _getFirstNodeOfTag( edgeNode, 'y:LineStyle' )
		if styleNode: self.parseLineStyleNode( edge, styleNode )

	def parseLabelNode( self, item, labelNode ):
		x = float( labelNode.getAttribute('x') )
		y = float( labelNode.getAttribute('y') )
		w = float( labelNode.getAttribute('width') )
		h = float( labelNode.getAttribute('height') )
		fsize = float( labelNode.getAttribute('fontSize') )
		item.setAttr( 'label.geometry', (x,y,w,h) )
		item.setAttr( 'label.font-size', fsize )
		item.setAttr( 'label', unicode(labelNode.firstChild.data) )

	def parseGeometryNode( self, item, geomNode ):
		x = float( geomNode.getAttribute('x') )
		y = float( geomNode.getAttribute('y') )
		w = float( geomNode.getAttribute('width') )
		h = float( geomNode.getAttribute('height') )
		item.setAttr( 'geometry', (x,y,w,h) )

	def parseLineStyleNode( self, item, styleNode ):
		color = styleNode.getAttribute( 'color' )
		width = float( styleNode.getAttribute( 'width' ) )
		style = styleNode.getAttribute( 'type' )
		item.setAttr( 'color', color )
		item.setAttr( 'width', width )
		item.setAttr( 'style', style )


	def parsePathNode( self, edge, pathNode ):
		sx = float( pathNode.getAttribute('sx') )
		sy = float( pathNode.getAttribute('sy') )
		tx = float( pathNode.getAttribute('tx') )
		ty = float( pathNode.getAttribute('ty') )
		edge.setAttr( 'path-start', (sx,sy) )
		edge.setAttr( 'path-end', (tx,ty) )
		geomS = edge.nodeSrc.getAttr( 'geometry' )
		geomT = edge.nodeDst.getAttr( 'geometry' )
		sx += geomS[0]
		sy += geomS[1]
		tx += geomT[0]
		ty += geomT[1]
		points = []
		points.append( (sx,sy) )
		for subPointNode in pathNode.getElementsByTagName('y:Point'):
			x = float( subPointNode.getAttribute('x') )
			y = float( subPointNode.getAttribute('y') )
			points.append( (x,y) )
		points.append( (tx,ty) )
		edge.setAttr( 'path', points )

if __name__ == '__main__':
	from gii.qt.controls.GraphicsView.GraphicsViewHelper import *
	from PyQt4 import QtGui, QtCore, QtOpenGL, uic
	import sys

	class TestFrame( QtGui.QFrame ):
		def __init__( self ):
			super( TestFrame, self ).__init__()
			parser = YedGraphMLParser()
			g = parser.parse( 'pizza.graphml' )
			print g

	app = QtGui.QApplication( sys.argv )
	styleSheetName = 'gii.qss'
	app.setStyleSheet(
			open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
		)
	frame = TestFrame()

	frame.resize( 600, 300 )
	frame.show()
	frame.raise_()

	app.exec_()

	


