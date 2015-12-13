import re, fnmatch
from util.BracketTree import *

_REObjectCache = {}
def _wildcard2RO( pattern ):
	ro = _REObjectCache.get( pattern, None )
	if not ro:
		regex = fnmatch.translate( pattern )
		ro = re.compile( regex )
		_REObjectCache[ pattern ] = ro
	return ro

##----------------------------------------------------------------##
class TagMatchNode(object):
	def evaluate( self, data ):
		return False

class TagMatchNodeAND( TagMatchNode ):
	def __init__( self, childNodes ):
		self.childNodes = childNodes

	def evaluate( self, data ):
		for node in self.childNodes:
			if not node.evaluate( data ): return False
		return True

class TagMatchNodeOR( TagMatchNode ):
	def __init__( self, childNodes ):
		self.childNodes = childNodes

	def evaluate( self, data ):
		for node in self.childNodes:
			if node.evaluate( data ): return True
		return False

class TagMatchNodePattern( TagMatchNode ):
	def __init__( self, pattern, matchAll = False ):
		self.pattern = pattern
		self.matchAll = matchAll

	def getEvaluateTargets( self, data ):
		return []

	def evaluate( self, data ):
		ro = _wildcard2RO( self.pattern )
		if self.matchAll:
			for target in self.getEvaluateTargets( data ):
				if not isinstance( target, str ): return False
				if not ro.match( target ): return False
			return True
		else:
			for target in self.getEvaluateTargets( data ):
				if not isinstance( target, str ): continue
				if ro.match( target ): return True
			return False

class TagMatchNodeTag( TagMatchNodePattern ):
	def getEvaluateTargets( self, data ):
		v = data.get( 'tag' )
		if isinstance( v, list ): return v
		return [ v ]

class TagMatchNodeName( TagMatchNodePattern ):
	def getEvaluateTargets( self, data ):
		v = data.get( 'name' )
		if isinstance( v, list ): return v
		return [ v ]

class TagMatchNodeType( TagMatchNodePattern ):
	def getEvaluateTargets( self, data ):
		v = data.get( 'type' )
		if isinstance( v, list ): return v
		return [ v ]

class TagMatchRule(object):
	def __init__( self ):
		self.rootNode = None
		
		
class TagMatch(object):
	"""docstring for TagMatch"""
	def __init__(self, arg):
		super(TagMatch, self).__init__()
		self.arg = arg


def matchWildcard( pattern, tags ):
	ro = _wildcard2RO( pattern )
	for tag in tags:
		if ro.match( tag ): return True
	return False


def processTreeNode( treeNode, overridedTag = None ):
	nodeTag = treeNode.getTag()
	if overridedTag:
		nodeTag = overridedTag

	if nodeTag == 'tag':
		return TagMatchNodeTag( str(treeNode.getChildValue( 0 )) )

	elif nodeTag == 'type':
		return TagMatchNodeType( str(treeNode.getChildValue( 0 )) )

	elif nodeTag == 'name':
		return TagMatchNodeName( str(treeNode.getChildValue( 0 )) )

	elif nodeTag == 'or':
		return TagMatchNodeOR( [ processTreeNode( childNode ) for childNode in treeNode.getChildren() ] )

	elif nodeTag == 'and':
		return TagMatchNodeAND( [ processTreeNode( childNode ) for childNode in treeNode.getChildren() ] )
	
	else:
		if treeNode.isValue(): return TagMatchNodeName( str(treeNode.getValue()) )

		raise Exception( 'unkown criteria tag' )

##----------------------------------------------------------------##
def bracketTree2TagMatch( src, **kwargs ):
	root = parseBracketTree( src )
	# print root.toData()
	children = root.getChildren()
	size = len( children )
	if size > 1:
		if kwargs.get( 'match_all', True ):
			return processTreeNode( root, 'and' )
		else:
			return processTreeNode( root, 'or' )

	elif size == 1:
		return processTreeNode( children[0] )

	else:
		return None

##----------------------------------------------------------------##
def matchTag( pattern, data, **kwargs ):
	matchNode = bracketTree2TagMatch( pattern, **kwargs )
	return matchNode.evaluate( data )

##----------------------------------------------------------------##
##TEST
##----------------------------------------------------------------##	
if __name__ == '__main__':
	# matchNode = bracketTree2TagMatch( 'or( tag(damhill), tag(common) )' )
	pattern = 'and( or( tag(damhill), tag(common) ), tag(furniture) )'
	
	print 'matching pattern:', pattern
	matchNode = bracketTree2TagMatch( pattern )

	testDataSet = [
		{ "tag" : ['damhill', 'furniture'], "type" : "proto" },
		{ "tag" : ['common', 'furniture'],  "type" : "proto" },
		{ "tag" : ['common', 'tool'],       "type" : "texture" },
		{ "tag" : ['damhill', 'NPC'],       "type" : "texture" },
	]

	for data in testDataSet:
		print data, matchNode.evaluate( data )

	print matchTag( 'and( tag(damhill), type(texture) )', testDataSet[ 3 ] )
