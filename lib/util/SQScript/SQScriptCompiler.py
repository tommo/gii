# -*- coding: utf-8 -*-
import re
from parsimonious.grammar import Grammar, TokenGrammar
from parsimonious.exceptions import ParseError, IncompleteParseError
import io

##----------------------------------------------------------------##
class SQNode( object ):
	def __init__( self ):
		self.nodeType = None
		self.children = []
		self.parent   = None
		self.indent   = -1
		self.depth    = 0

	def addChild( self, n ):
		n.parent = self
		self.children.append( n )
		n.depth	 = self.depth + 1
		return n

	def toJSON( self ):
		return {
			'type' : self.getType(),
			'children' : [ child.toJSON() for child in self.children ],
		}

	def getType( self ):
		return 'SQNode'

##----------------------------------------------------------------##
class SQRootNode( SQNode ):
	def getType( self ):
		return 'root'

##----------------------------------------------------------------##
class SQLabelNode( SQNode ):
	def __init__( self ):
		super( SQLabelNode, self ).__init__()
		self.id = ''

	def toJSON( self ):
		data = super( SQLabelNode, self ).toJSON()
		data[ 'id' ] = self.id
		return data

	def getType( self ):
		return 'label'

##----------------------------------------------------------------##
class SQContextNode( SQNode ):
	def __init__( self ):
		super( SQContextNode, self ).__init__()
		self.names = []		

	def toJSON( self ):
		data = super( SQContextNode, self ).toJSON()
		data[ 'names' ] = self.names
		return data

	def getType( self ):
		return 'context'

##----------------------------------------------------------------##
class SQTagNode( SQNode ):
	def __init__( self ):
		super( SQTagNode, self ).__init__()
		self.tags = []		

	def toJSON( self ):
		data = super( SQTagNode, self ).toJSON()
		data[ 'tags' ] = self.tags
		return data

	def getType( self ):
		return 'tag'

##----------------------------------------------------------------##
class SQActionNode( SQNode ):
	def __init__( self ):
		super( SQActionNode, self ).__init__()
		self.name = ''
		self.args = []

	def toJSON( self ):
		data = super( SQActionNode, self ).toJSON()
		data[ 'name' ] = self.name
		data[ 'args' ] = self.args
		return data

	def getType( self ):
		return 'action'

##----------------------------------------------------------------##
def _getNodeTexts( n, tt ):
	l = []
	for child in n.children:
		if child.expr_name == tt:
			l.append( child.text )
		else:
			if child.children:
				for cc in child.children:
					l += _getNodeTexts( cc, tt )
	return l


##----------------------------------------------------------------##
class SQScriptCompiler(object):
	LineGrammar = Grammar(
		'''
		line                = comment_line / stmt_line
		comment_line        = ws comment
		stmt_line           = indentation stmt ws comment?
		stmt                = context / tag / label / node_long / node
		context             = "@" (ws identifier)+
		tag                 = "#" (ws identifier)+
		label               = "!" identifier
		node_long           = identifier ws ":" trail
		node                = identifier (ws span)*
		indentation         = ~"\t*"
		identifier          = ~"[A-Z_]+[A-Z0-9_]*"i
		ws                  = ~"[\s]*"
		span                = ~"[^\s]+"
		comment             = ~"//.*"
		trail               = ~".*"
		'''
	)


	def __init__( self ):
		pass

	def parseFile( self, path ):
		fp = io.open( path, 'rt', encoding = 'utf-8' )
		source = fp.read()
		fp.close()
		return self.parse( source )

	def reset( self ):
		self.parsingLongNode = False
		self.rootNode = SQRootNode()
		self.rootNode.indent = -1
		self.contextNode = self.rootNode
		self.prevNode    = None
		self.lineId      = 0

	def parse( self, source ):
		self.reset()
		try:
			for line in source.split( '\n' ):
				self.lineId += 1
				if self.parsingLongNode:
					if self.parseLongNodeLine( line ):
						continue
				self.parseStmtLine( line )

		except ParseError, e:
			e.line_offset = self.lineId - 1
			print e.line(), e.column()
			raise e

		except IncompleteParseError, e:
			e.line_offset = self.lineId - 1
			raise e

		return self.rootNode

	def parseLongNodeLine( self, line ):
		indentSize = 0
		for i, c in enumerate( line ):
			if c == '\t':
				indentSize += 1
			else:
				break
		if indentSize > self.prevNode.indent:
			text = line[ indentSize: ]
			self.prevNode.args.append( text )
			return True
		else:
			self.parsingLongNode = False
			return False

	def parseStmtLine( self, line ):
		indentSize = 0
		if not line.strip(): return False
		lineNode = SQScriptCompiler.LineGrammar.parse( line ).children[ 0 ]
		if lineNode.expr_name == 'comment_line':
			return False
		indentNode = lineNode.children[ 0 ]
		stmtNode   = lineNode.children[ 1 ].children[ 0 ]
		indentSize   = indentNode.end - indentNode.start
		stmtNodeType = stmtNode.expr_name
		
		if self.prevNode:
			if indentSize == self.prevNode.indent:
				pass #do nothing

			elif indentSize > self.contextNode.indent: #INCINDENT
				self.contextNode = self.prevNode

			else:
				while indentSize <= self.contextNode.indent:
					self.contextNode = self.contextNode.parent

		if stmtNodeType == 'node_long':
			self.parsingLongNode = True
		node = self.loadNode( stmtNodeType, stmtNode )
		node.indent = indentSize
		self.contextNode.addChild( node )
		self.prevNode = node

	def loadNode( self, nodeType, stmtNode ):
		if nodeType == 'node':
			node = SQActionNode()
			node.name = _getNodeTexts( stmtNode, 'identifier' )[0]
			node.args += _getNodeTexts( stmtNode, 'span' )

		elif nodeType == 'node_long':
			node = SQActionNode()
			node.name = _getNodeTexts( stmtNode, 'identifier' )[0]
			trails = _getNodeTexts( stmtNode, 'trail' )
			if trails and trails[0]:
				node.args += trails

		elif nodeType == 'context':
			node = SQTagNode()
			node.names = _getNodeTexts( stmtNode, 'identifier' )

		elif nodeType == 'tag':
			node = SQTagNode()
			tags = _getNodeTexts( stmtNode, 'identifier' )
			node.tags = tags

		elif nodeType == 'label':
			node = SQLabelNode()
			node.id = _getNodeTexts( stmtNode, 'identifier' )[0]
		
		return node

__all__ = [
	'SQNode',
	'SQLabelNode',
	'SQContextNode',
	'SQTagNode',
	'SQActionNode',
	'SQScriptCompiler',
]


if __name__ == '__main__':
	text = u'''
//sqscript
!start
@Jasper
	say:
		今天天气真好啊！
'''
	
	import logging
	import json

	def saveJSON( data, path, **option ):
		outputString = json.dumps( data , 
				indent    = option.get( 'indent' ,2 ),
				sort_keys = option.get( 'sort_keys', True ),
				ensure_ascii=False
			).encode('utf-8')
		fp = open( path, 'w' )
		fp.write( outputString )
		fp.close()
		return True

	node = SQScriptCompiler().parse( text )
	data = node.toJSON()

	saveJSON( data, 'test.json' )

