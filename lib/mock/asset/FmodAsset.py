import os.path
import logging
import subprocess
import shutil

from gii.core import AssetManager, AssetLibrary, getProjectPath, app
# import xml.parsers.expat
import xml.etree.ElementTree as ET

##----------------------------------------------------------------##
def parseFDP( path ):
	try:
		fp = file( path, 'r' )
		data = fp.read()
		fp.close()
	except Exception, e :
		return False
	root = ET.fromstring( data )
	groups = {}
	for groudItem in root.iterfind( 'eventgroup' ):
		name = groudItem.find('name').text
		g = {}
		groups[ name ] = g
		events = {}
		g['events'] = events
		for eventItem in groudItem.iterfind( 'event' ):
			eventName = eventItem.find('name').text
			events[ eventName ] = {
				'mode'    : eventItem.find('mode').text,
				'oneshot' : eventItem.find('oneshot').text,
			}
		for simpleEventItem in groudItem.iterfind( 'simpleevent' ):
			eventItem = simpleEventItem.find('event')
			eventName = eventItem.find('name').text
			events[ eventName ] = {
				'mode'    : eventItem.find('mode').text,
				'oneshot' : eventItem.find('oneshot').text,
			}

	banks = {}
	for bankItem in root.iterfind( 'soundbank' ):
		name = bankItem.find('name').text
		banks[ name ] = {}

	return {
		'groups' : groups,
		'banks'  : banks
	}

	
##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class FmodAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.fmod'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name, ext = os.path.splitext(filepath)
		if not ext in ['.fdp']: return False
		return True

	def importAsset(self, node, reload = False ):
		node.assetType = 'fmod_project'		
		
		project = parseFDP( node.getAbsFilePath() )

		fmodDesignerPath = '/Users/tommo/dev/fmod/FMOD Designer'
		output = node.getCacheFile( 'export', is_dir = True )
		node.setObjectFile( 'export', output )
		# target = '-ios'
		target = '-pc'
		arglist = [ 
				fmodDesignerPath+'/fmod_designercl',
				target,
				'-p',
				'-b', output,
				node.getAbsFilePath()
			]
		try:
			subprocess.call( arglist )
		except Exception, e:
			logging.exception( e )

		#TODO:check bank files( delete banks unavailable )
		banks = project['banks']
		for name, bank in banks.items():
			pass

		groups = project['groups']
		for name, group in groups.items():
			groupNode = node.createChildNode( name, 'fmod_group', manager = self )
			events    = group['events']
			for name, event in events.items():
				eventNode = groupNode.createChildNode( name, 'fmod_event', manager = self )

		return True

FmodAssetManager().register()

AssetLibrary.get().setAssetIcon( 'fmod_project',   'fmod' )
AssetLibrary.get().setAssetIcon( 'fmod_group',     'fmod_group' )
AssetLibrary.get().setAssetIcon( 'fmod_event',     'audio' )
