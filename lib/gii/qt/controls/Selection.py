import signals
import weakref

class SelectionManager(object):
	_singleton=None

	@staticmethod
	def get():
		return SelectionManager._singleton

	def __init__(self):
		assert not SelectionManager._singleton
		SelectionManager._singleton=self

		self.currentSelection=None
		self.history=[]
		self.historyPos=0
		self.maxHistorySize=32

	def clearHistory(self):
		self.history=[]
		self.historyPos=0

	def clearSelection(self):
		self.changeSelection(None)

	def changeSelection(self, selection):		
		#todo: use weakref to hold selection		
		if selection:			
			if not isinstance(selection, list): selection=[selection]
			hisSize=len(self.history)
			self.history=self.history[:hisSize-self.historyPos]
			self.history.append(selection)
			self.history=self.history[0:self.maxHistorySize]
			self.historyPos=0
		self.currentSelection=selection
		signals.emit('selection.changed', selection)

	def historyBack(self):
		hisSize=len(self.history)
		if self.historyPos < hisSize:
			self.historyPos+=1
			selection=self.history[hisSize-self.historyPos]
			self.currentSelection=selection
			signals.emit('selection.changed', selection)

	def historyForward(self):
		hisSize=len(self.history)
		if self.historyPos >0:
			self.historyPos-=1
			selection=self.history[hisSize-self.historyPos]
			self.currentSelection=selection
			signals.emit('selection.changed', selection)

	def getSelection(self):
		return self.currentSelection

	def getSingleSelection(self):
		return self.currentSelection and self.currentSelection[0] or None


SelectionManager()
