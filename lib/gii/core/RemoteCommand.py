import logging

class RemoteCommandMeta( type ):
	def __init__( cls, name, bases, dict ):
		super( RemoteCommandMeta, cls ).__init__( name, bases, dict )
		fullname = dict.get( 'name', None )
		if not fullname: return
		RemoteCommandRegistry.get().registerCommand( fullname, cls )

##----------------------------------------------------------------##

##----------------------------------------------------------------##
class RemoteCommand( object ):
	__metaclass__ = RemoteCommandMeta
	def run( argv ):
		pass

##----------------------------------------------------------------##
class RemoteCommandRegistry( object ):
	_singleton = None

	@staticmethod
	def get():
		if not RemoteCommandRegistry._singleton:
			return RemoteCommandRegistry()
		return RemoteCommandRegistry._singleton

	def __init__( self ):
		RemoteCommandRegistry._singleton = self
		self.commands = {}

	def registerCommand( self, name, cmdClas ):
		self.commands[ name ] = cmdClas

	def doCommand( self, argv, output ):
		if argv:
			cmdName = argv[0]
			clas = self.commands.get( cmdName, None )
			if clas:
				cmd = clas()
				if len( argv ) > 1 :
					args = argv[1:]
				else:
					args = []
				try:
					cmd.run( *args )
				except Exception, e:
					logging.exception( e )
			else:
				logging.warning( 'no remote command found:' + cmdName )


RemoteCommandRegistry()
