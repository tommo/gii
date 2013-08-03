import logging
import json

def saveJSON( data, path ):
	outputString = json.dumps( data , 
			indent=2, sort_keys=True, ensure_ascii=False).encode('utf-8')
	fp = open( path, 'w' )
	fp.write( outputString )
	fp.close()
	return True

def loadJSON( path ):
	fp = file(path)
	data = json.load( fp, 'utf-8' )
	fp.close()
	return data

def trySaveJSON( data, path, dataName = None ):
	try:
		saveJSON( data, path )
		return True
	except Exception, e:
		logging.warn( 'failed to save %s: %s' % ( dataName or 'JSON', repr(e) ) )
		return False


def tryLoadJSON( path, dataName = None ):
	try:
		data = loadJSON( path )
		return data
	except Exception, e:
		logging.warn( 'failed to load %s: %s' % ( dataName or 'JSON', repr(e) ) )
		return False
