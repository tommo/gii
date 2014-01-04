from gii.core import *
from gii.core.model import *

from PropertyEditor import FieldEditor, registerFieldEditor
from SearchFieldEditor import SearchFieldEditorBase


##----------------------------------------------------------------##
class AssetRefFieldEditor( SearchFieldEditorBase ):	
	def getValueRepr( self, value ): #virtual
		return value #str

	def getSearchType( self ): #virtual
		t = self.field.getType()
		return t.assetType

	def getSearchContext( self ): #virtual
		return "asset"

	def getSearchInitial( self ): #virtual
		return self.target and AssetLibrary.get().getAssetNode( self.target ) or None

	def gotoObject( self ): #virutal
		signals.emit( 'selection.hint', self.target )

	def setValue( self, node ): #virtual
		if node:
			value = node.getNodePath()
		else:
			value = None
		super( AssetRefFieldEditor, self ).setValue( value )

	def gotoObject( self ):
		assetBrowser = app.getModule( 'asset_browser' )
		if assetBrowser:
			assetBrowser.locateAsset( self.target )

##----------------------------------------------------------------##

registerFieldEditor( AssetRefType, AssetRefFieldEditor )
