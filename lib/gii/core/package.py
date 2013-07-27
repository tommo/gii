import sys
import os
import os.path
import imp
import logging

_GII_PACKAGE_PREFIX = '[gii-package]'

##----------------------------------------------------------------##
def _clearSysModule( prefix ):
	toremove = []
	for k in sys.modules:
		if k.startswith( prefix ):
			toremove.append( k )

	for k in toremove:
		del sys.modules[ k ]

##----------------------------------------------------------------##
class PackageManager( object ):
	def __init__( self ):
		self.packagePaths = []
		self.packages = {}

	def addPackagePath( self, path ):
		self.packagePaths.append( path )

	def loadPackage( self, name, path ):
		prev = self.getPackage( name )
		if prev:
			logging.warn( 'duplicated package: %s \n\tfound:\t%s\n\tfound:\t%s' % ( name, prev.path, path ) )
			return False
		package = Package( name, path )
		self.packages[ name ] = package
		package.load()
		return package

	def getPackage( self, name ):
		return self.packages.get( name, None )

	def scanPackages( self ):
		for path in self.packagePaths:
			if not os.path.exists( path ): continue
			logging.info( 'scanning package in:' + path )
			for currentDir, dirs, files in os.walk( unicode(path) ):
				for dirname in dirs:
					fullpath = currentDir + '/' + dirname
					if os.path.exists( fullpath + '/__init__.py' ) \
					or os.path.exists( fullpath + '/__init__.pyc' ):
						self.loadPackage( dirname, fullpath )

##----------------------------------------------------------------##
class Package(object):
	def __init__( self, name, path ):
		self.name   = name
		self.path   = path
		self.moduleName = _GII_PACKAGE_PREFIX + name
		self.loadedModule = None

	def reload( self ):
		self.unload()
		self.load()

	def load( self ):
		self.loadedModule = imp.load_module( self.moduleName, None, self.path, ('', '', 5) )

	def unload( self ):
		if self.loadedModule:
			_clearSysModule( self.moduleName )
			self.loadedModule = None
		#TODO: package callback?
		#TODO: unload dylib?
