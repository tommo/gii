import cli
import gii

def main( argv ):
	args = cli.parse( argv )
	gii.app.openProject()
	if args.update:
		#DO_THE_UPDATE_JOBS()
		return True
	#start GUI editor
	from gii import QtAssetBrowser
	import QtTextureManager
	gii.app.run()
