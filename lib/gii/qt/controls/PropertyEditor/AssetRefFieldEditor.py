from gii.core import *
from gii.core.model import *

from PropertyEditor import FieldEditor, registerSimpleFieldEditorFactory
from SearchFieldEditor import SearchFieldEditorBase

import os.path

##----------------------------------------------------------------##
class AssetRefFieldEditor( SearchFieldEditorBase ):	
	def getValueRepr( self, value ): #virtual
		lib = AssetLibrary.get()
		if value:
			node = lib.getAssetNode( value )
			if node:
				icon = lib.getAssetIcon( node.getType() )
				return ( value, icon )
		return value #str

	def getSearchType( self ): #virtual
		t = self.field.getType()
		return t.assetType

	def getSearchContext( self ): #virtual
		return "asset"

	def getSearchInitial( self ): #virtual
		return self.target and AssetLibrary.get().getAssetNode( self.target ) or None

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
	
	def formatRefName( self, name )	:
		if isinstance( name, ( str, unicode ) ):
			return os.path.basename( name )
		else:
			return name

##----------------------------------------------------------------##

registerSimpleFieldEditorFactory( AssetRefType, AssetRefFieldEditor )
