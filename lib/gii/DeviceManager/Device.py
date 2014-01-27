import MobileDevice
import logging

##----------------------------------------------------------------##
class DeviceItem():	
	def getName( self ):
		return 'device'
	
	def getType( self ):
		return 'device '

	def getId( self ):
		return 0

	def isConnected( self ):
		return False

	def setActive( self, act ):
		self.active = act

	def isActive( self ):
		return self.active

	def deploy( self, deployContext ):
		pass

	def clearData( self ):
		pass

	def startDebug( self ):
		pass

	def stopDebug( self ):
		pass

	def disconnect( self ):
		pass

	def __repr__( self ):
		return self.getType()
		# return u'{0}({1})'.format( self.getName(), self.getType() )
