import os
import stat
import logging

from Device import DeviceItem
from gii.core import app

import MobileDevice
import subprocess

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
		self._device   = dev = MobileDevice.AMDevice( devId )
		dev.connect()
		name = ''
		try:
			name = dev.get_value( name = u'DeviceName' )
		except Exception, e :
			logging.exception( e )
		self.name = name
		self.id   = dev.get_deviceid()
		self.connected = connected

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
			return self._deployDataFiles( appName, localDataPath, remoteDataPath, **option )
		except Exception, e:
			logging.exception( e )
			return False

	def disconnect( self ):
		if self.connected:
			self._device.disconnect()
			self._deviceId = None
			self._device   = None
			self.connected = False

	def clearData( self ):
		appName        = 'com.hatrixgames.yaka'
		dev   = self._device
		remoteDataPath = 'Documents/game'
		if not self.isConnected():
			logging.warn( 'device not connected' )
			return False

		dev.refresh_session()		
		afc = getAppAFC( dev, appName )
		cleanDirFromDevice( afc, remoteDataPath )
		afc.disconnect()
		# dev.disconnect()

	def startDebug( self ):
		self.debugSession = IOSDeviceDebugSession( self )

	def _deployDataFiles( self, appName, localDataPath, remoteDataPath, **option ):
		# devices = MobileDevice.list_devices()
		if not self.isConnected():
			logging.warn( 'device not connected' )
			return False
		dev   = self._device
		dev.refresh_session()
		afc = getAppAFC( dev, appName )
		# cleanDirFromDevice( afc, 'Documents' )
		copyTreeToDevice( afc, localDataPath, remoteDataPath, **option )	
		afc.disconnect()
		return True

class IOSDeviceDebugSession(object):
	def __init__( self, deviceItem ):
		tool = app.getPath( 'support/deploy/ios-deploy' )
		arglist = [ tool ]
		localPath = app.getProject().getHostPath( 'ios/build/Release-iphoneos/YAKA.app' )
		arglist += ['--id', deviceItem.getId() ]
		arglist += ['--bundle', localPath ]
		arglist += ['--debug']
		try:
			code = subprocess.call( arglist )
			if code!=0: return code
		except Exception, e:
			logging.error( 'error in debugging device: %s ' % e)
			return -1		

# class IOSDeviceDebugSession(object):
# 	def __init__(self, dev):
# 		self.dev = dev
# 		self.load_developer_dmg()
# 		localPath = app.getProject().getHostPath( 'ios/build/Release-iphoneos/YAKA.app' )
# 		print localPath
# 		self.gdb = MobileDevice.GDB( dev, None, localPath )
# 		self.gdb.set_run()
# 		self.gdb.run()

# 	def load_developer_dmg( self ):
# 		dev = self.dev
# 		try:
# 			applist = MobileDevice.DebugAppList(dev)
# 			applist.disconnect()
# 		except:
# 			im = MobileDevice.ImageMounter(dev)
# 			imagepath = dev.find_developer_disk_image_path()
# 			im.mount(imagepath)
# 			im.disconnect()
