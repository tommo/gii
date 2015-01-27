import signals
import weakref

_SelectionManagerRegistry = {
	
}

def getSelectionManager( key ):
	return _SelectionManagerRegistry.get( key, None )

class SelectionManager(object):	
	def __init__( self, key ):
		assert not _SelectionManagerRegistry.has_key( key ), 'duplicated Manager ' + key
		_SelectionManagerRegistry[ key ] = self
		self.currentSelection = []
		self.history = []
		self.historyPos = 0
		self.maxHistorySize = 32
		self.key = key

	def clearHistory(self):
		self.history = []
		self.historyPos = 0

	def clearSelection(self):
		self.changeSelection([])

	def changeSelection( self, selection ):
		#todo: use weakref to hold selection		
		if selection:			
			if not isinstance(selection, list): selection = [ selection ]
			hisSize = len(self.history)
			self.history = self.history[:hisSize - self.historyPos]
			self.history.append(selection)
			self.history = self.history[0:self.maxHistorySize]
			self.historyPos = 0
		if selection is None:
			selection = []
		self.currentSelection = selection
		signals.emitNow('selection.changed', selection, self.key )

	def addSelection( self, selection ):
		if not selection: return
		if not isinstance(selection, list): selection = [ selection ]
		return self.changeSelection( self.currentSelection + selection )

	def historyBack(self):
		hisSize = len(self.history)
		if self.historyPos < hisSize:
			self.historyPos += 1
			selection=self.history[hisSize - self.historyPos]
			self.currentSelection=selection
			signals.emitNow('selection.changed', selection, self.key )

	def historyForward(self):
		hisSize = len(self.history)
		if self.historyPos > 0:
			self.historyPos -= 1
			selection=self.history[hisSize - self.historyPos]
			self.currentSelection=selection
			signals.emitNow('selection.changed', selection, self.key )

	def getSelection(self):
		return self.currentSelection or []

	def getSingleSelection(self):
		return self.currentSelection and self.currentSelection[0] or None

