import os.path
import subprocess
import shutil

from gii.core import *

from tools.ml2fsm import convertGraphMLToFSM

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path
	
##----------------------------------------------------------------##
class FSMSchemeAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.fsm_scheme'

	def acceptAssetFile( self, filePath ):
		if not os.path.isfile(filePath): return False		
		if not filePath.endswith( '.fsm.graphml' ): return False
		return True

	def importAsset( self, node, reload = False ):
		node.setObjectFile( 'def', node.getCacheFile( 'def' ) )
		convertGraphMLToFSM(
			node.getAbsFilePath(), #input file
			node.getAbsObjectFile( 'def' ) #output file
		)
		node.assetType = 'fsm_scheme'
		return True
	
# ##----------------------------------------------------------------##
# class FSMSchemeCreator(AssetCreator):
# 	def getAssetType( self ):
# 		return 'fsm_scheme'

# 	def getLabel( self ):
# 		return 'FSMScheme'

# 	def createAsset( self, name, contextNode, assetType ):
# 		ext = '.fsm_scheme'
# 		filename = name + ext
# 		if contextNode.isType('folder'):
# 			nodepath = contextNode.getChildPath( filename )
# 		else:
# 			nodepath = contextNode.getSiblingPath( filename )

# 		fullpath = AssetLibrary.get().getAbsPath( nodepath )
# 		data={
# 			'_assetType' : 'fsm_scheme', #checksum
# 			'map'     :{},
# 			'entities':[]
# 		}
# 		if os.path.exists(fullpath):
# 			raise Exception('File already exist:%s'%fullpath)
# 		fp = open(fullpath,'w')
# 		json.dump( data, fp, sort_keys=True, indent=2 )
# 		fp.close()
# 		return nodepath

# ##----------------------------------------------------------------##
# FSMSchemeCreator().register()

FSMSchemeAssetManager().register()
AssetLibrary.get().setAssetIcon( 'fsm_scheme',    'scheme' )
