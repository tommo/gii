from Service import Service, ServiceInstance

##----------------------------------------------------------------##
class Center(object):
	def __init__( self ):
		self.serviceRegistry = ServiceRegistry()


##----------------------------------------------------------------##
class ServiceRegistry(object):
	def __init__( self, center ):
		self.center = center
		self.services = {}

	def register( self, service ):
		id = service.getId()
		if self.services.has_key( id ):
			raise Exception ('duplicated service id: %s' % id)
		self.services[ id ] = service
		service.onRegister( self.center )
	
	def getService( self, id ):
		return self.services.get( id )

