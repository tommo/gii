from util import TagMatch

##----------------------------------------------------------------##
class AssetFilterItem( object ):
	def __init__( self ):
		self.locked  = False
		self.active  = True
		self.alias   = ''
		self.citeria = ''
		self.rule    = None

	def setLocked( self, locked ):
		self.locked = locked

	def isLocked( self ):
		return self.locked

	def setAlias( self, alias ):
		self.alias = alias

	def getAlias( self ):
		return self.alias

	def toString( self ):
		if self.alias: return self.alias
		return self.citeria

	def setCiteria( self, citeria ):
		self.citeria = citeria
		self.rule = TagMatch.parseTagMatch( citeria, uppercase = True )

	def getCiteria( self ):
		return self.citeria

	def evaluateInfo( self, info ):
		if not self.rule: return False
		return self.rule.evaluate( info )

	def evaluateAsset( self, assetNode ):
		info = assetNode.buildSearchInfo( uppercase = True )
		return self.evaluateInfo( info )

##----------------------------------------------------------------##
class AssetFilterNode( object ):
	def __init__( self ):
		self.children = []
		self.parent = None
	
	def getParent( self ):
		return self.parent

	def addChild( self, node ):
		if node.parent:
			node.remove()
		self.children.append( node )
		node.parent = self

	def getChildren( self ):
		return children

	def removeChild( self, node ):
		self.children.remove( node )
		node.parent = None

	def remove( self ):
		if self.parent:
			return self.parent.removeChild( self )

##----------------------------------------------------------------##
def AssetFilterGroup( AssetFilterNode ):
		pass

##----------------------------------------------------------------##
class AssetFilter( AssetFilterNode ):
	def __init__( self ):
		super( AssetFilter, self ).__init__()
		self.items = []
	
	def evaluate( self, assetNode ):
		info = assetNode.buildSearchInfo( uppercase = True )
		result = None
		for item in self.items:
			if item.active:
				r = item.evaluateInfo( info )
				if result == None:
					result = r
				else:
					result = result and r
		return result

	def addItem( self, item ):
		self.items.append( item )
		item.parent = self

	def removeItem( self, item ):
		self.items.remove( item )
		item.parent = None

	def getItems( self ):
		return self.items

