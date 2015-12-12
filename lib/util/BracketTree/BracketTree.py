import re
'''
A dead simple ( Lisp like ) bracketed tree parser
TODO: bracket matching
'''

##----------------------------------------------------------------##
def strToNum( v ):
	try:
		number_float = float(v)
		number_int = int(v)
		return number_int if number_float == number_int else number_float
	except ValueError:
		return v


##----------------------------------------------------------------##
class BracketTreeNode( object ):
	def __init__( self, parent ):
		self.parent = parent
		self.tag    = None
		self.value  = None
		self.children = None
		
	def initValue( self, v ):
		self.value = strToNum( v )

	def initObject( self, tag, children ):
		self.tag = tag
		self.children = children

	def isValue( self ):
		return not( self.value is None )
	
	def isObject( self ):
		return not( self.tag is None )

	def getValue( self ):
		return self.value

	def getChildren( self ):
		return self.children

	def getTag( self ):
		return self.tag
	
	def getParent( self ):
		return self.parent

	def toData( self ):
		if self.isValue():
			return self.getValue()
		else:
			return {
				'tag': self.tag,
				'children': [ child.toData() for child in self.children ]
			}

##----------------------------------------------------------------##
ROBracket = re.compile( '\s*(\w+)\s*\(\s*(.*)\s*\)\s*' )
def _parseBracketNode( src, parentNode ):
		mo = ROBracket.match( src )
		if mo:
			tag = mo.group( 1 )
			content = mo.group( 2 )
			node = BracketTreeNode( parentNode )
			children = _parseList( content, node )
			node.initObject( tag, children )
			return node

		else:
			node = BracketTreeNode( parentNode )
			node.initValue( src )
			return node

def _parseList( src, parentNode ):
	output = []
	datas = src.split( ',' )
	for data in datas:
		data = data.strip()
		node = _parseBracketNode( data, parentNode )
		output.append( node )
	return output

##----------------------------------------------------------------##
def parseBracketTree( src ):
	node = _parseBracketNode( src, None )
	return node



##----------------------------------------------------------------##
##TEST
##----------------------------------------------------------------##	
if __name__ == '__main__':
	tree = parseBracketTree( 'and( tag( damhill ), tag( common ) )' )
	print tree.toData()
