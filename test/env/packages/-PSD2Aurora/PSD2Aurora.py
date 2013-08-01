
class PSD2AuroraManager( AssetManager ):
	def getName( self ):
		return 'asset_manager.psd2aurora'

	def acceptAssetFile( self, filepath ):
		if not os.path.isfile(filepath): return False		
		name, ext = os.path.splitext(filepath)
		return ext in ( '.png', '.psd', '.jpg', '.bmp', '.jpeg' )

