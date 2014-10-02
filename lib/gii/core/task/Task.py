##----------------------------------------------------------------##
class Task(object):
	def __init__( self ):
		self._state = 

	def isDone( self ):
		return self._done

	def markDone( self ):
		self._done = True

	def canPause( self ):
		return False

	def pause( self ):
		if not self._paused:
			self._paused = True
			self.onPause()

	def resume( self ):
		if self._paused:
			self._paused = False
			self.onResume()

	def log( self ):
		pass

	def reportProgress( self, progress ):
		pass

	def onStart( self ):
		pass

	def onStop( self ):
		pass

	def onDone( self ):
		pass

	def onPaused( self ):
		pass

	def onResume( self ):
		pass


##----------------------------------------------------------------##
class TaskCenter(object):
	def __init__( self ):
		self._tasks = {}
	
	def update( self ):
		pass

