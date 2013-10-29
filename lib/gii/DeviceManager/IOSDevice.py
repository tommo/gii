import os
import stat
import logging

from Device import DeviceItem

import MobileDevice

##----------------------------------------------------------------##
def copyToDevice( afc, srcFile, tgtFile, **option ):	
	force = option.get( 'force', False )
	
	try:
		tgtInfo = afc.lstat( tgtFile )
		tgtMTime = int( tgtInfo.st_mtime )
	except Exception, e:
		tgtMTime = 0

	if tgtMTime < os.path.getmtime( srcFile ):
		logging.info( 'copy new version: %s ' % srcFile )
		tgtFP = afc.open( tgtFile, u'w' )
		srcFP = open( srcFile, u'r' )
		tgtFP.write( srcFP.read() )
		srcFP.close()
		tgtFP.close()
	# else:
	# 	print 'no newer file, skip', tgtFile

##----------------------------------------------------------------##
def fileTypeOnDevice( afc, path ):
	try:
		info = afc.lstat( path )
	except Exception, e:
		return None
	return info.st_ifmt

##----------------------------------------------------------------##
def cleanDirFromDevice( afc, path ):
	if fileTypeOnDevice( afc, path ) != stat.S_IFDIR: return False
	for fileName in afc.listdir( path ):
		fullPath = path + '/' + fileName
		info = afc.lstat( fullPath )
		if info.st_ifmt == stat.S_IFDIR:
			removeTreeFromDevice( afc, fullPath )
		else:
			logging.info( 'remove file :%s ' % fullPath )
			afc.unlink( fullPath )
	return True

##----------------------------------------------------------------##
def removeTreeFromDevice( afc, path ):
	if not cleanDirFromDevice( afc, path ): return False
	afc.unlink( path )
	return True

##----------------------------------------------------------------##
def affirmDirOnDevice( afc, path ):
	ft = fileTypeOnDevice( afc, path )
	if ft == stat.S_IFDIR: return True
	if ft: return False #File Type
	try:
		afc.mkdir( path )
	except Exception, e:
		return False
	return True	

##----------------------------------------------------------------##
def copyTreeToDevice( afc, srcDir, tgtDir, **option ):
	if not os.path.isdir( srcDir ): raise Exception('dir expected')
	for currentDir, dirs, files in os.walk( srcDir ):
		relDir = os.path.relpath( currentDir, srcDir )
		if relDir == '.':
			currentTgtDir = tgtDir
		else:
			currentTgtDir = tgtDir + '/' + relDir			
		if not affirmDirOnDevice( afc, currentTgtDir ): raise Exception('invalid target directory')
		for f in files:
			#TODO:ignore pattern
			srcFile = currentDir + '/' + f
			tgtFile = currentTgtDir + '/' + f
			copyToDevice( afc, srcFile, tgtFile, **option)
		#todo:remove file not found in source

##----------------------------------------------------------------##
def getAppAFC( dev, appName ):
	return  MobileDevice.AFCApplicationDirectory( dev, appName.decode( u'utf-8' ) )

##----------------------------------------------------------------##
class IOSDeviceItem( DeviceItem ):
	def __init__( self, devId, connected = True ):
		self._deviceId = devId

		dev = MobileDevice.AMDevice( devId )
		dev.connect()

		name = ''
		try:
			name = dev.get_value( name = u'DeviceName' )
		except Exception, e :
			logging.exception( e )
		self.name = name
		self.id   = dev.get_deviceid()
		self.connected = connected
		dev.disconnect()

	def getName( self ):
		return self.name

	def getType( self ):
		return 'ios'

	def getId( self ):
		return self.id
	
	def isConnected( self ):
		return self.connected

	def deploy( self, deployContext, **option ):
		appName        = 'com.hatrixgames.yaka'
		localDataPath  = deployContext.getPath()
		remoteDataPath = 'Documents/game'
		try:
			return self.deployDataFiles( appName, localDataPath, remoteDataPath, **option )
		except Exception, e:
			logging.exception( e )
			return False

	def disconnect( self ):
		if self.connected:
			self._deviceId = None
			self.connected = False

	def clearData( self ):
		appName        = 'com.hatrixgames.yaka'
		devId = self._deviceId
		dev = MobileDevice.AMDevice( devId )
		dev.connect()
		remoteDataPath = 'Documents/game'
		if not self.isConnected():
			logging.warn( 'device not connected' )
			return False
		afc = getAppAFC( dev, appName )
		cleanDirFromDevice( afc, remoteDataPath )
		afc.disconnect()
		dev.disconnect()


	def deployDataFiles( self, appName, localDataPath, remoteDataPath, **option ):
		# devices = MobileDevice.list_devices()
		if not self.isConnected():
			logging.warn( 'device not connected' )
			return False
		devId = self._deviceId
		dev = MobileDevice.AMDevice( devId )
		dev.connect()
		afc = getAppAFC( dev, appName )
		# cleanDirFromDevice( afc, 'Documents' )
		copyTreeToDevice( afc, localDataPath, remoteDataPath, **option )	
		afc.disconnect()
		dev.disconnect()
		return True

# name = u''
	# try:
	# 	name = dev.get_value(name=u'DeviceName')
	# except:
	# 	pass
	# print( u'%s - "%s"' % ( dev.get_deviceid(), name.decode(u'utf-8') ) )
	# localPath  = None
	# remotePath = None
	# # remotePath = '/private/var/mobile/Applications/A9BB6740-D016-4800-A345-CBF0B909EBA7/YAKA.app'

	# localPath = '../../moai/yaka/bin/ios/YAKA.app'

	# gdb = MobileDevice.GDB( dev, None, localPath, remotePath )
	# gdb.set_run()
	# gdb.run()