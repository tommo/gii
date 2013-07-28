from gii import app
from abc import ABCMeta, abstractmethod

##----------------------------------------------------------------##
class AssetCreator(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def getAssetType( self ):
		return 'name'

	@abstractmethod
	def getLabel( self ):
		return 'Label'

	def register( self ):
		return app.getModule('asset_browser').registerAssetCreator( self )

	def createAsset(self, name, contextNode, assetType):
		return False

