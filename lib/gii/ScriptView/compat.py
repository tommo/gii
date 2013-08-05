from PyQt4 import Qsci,QtCore,QtGui
from PyQt4.Qsci import QsciScintilla as Sci


def convertColor(c):
	if isinstance(c, dict):
		return QtGui.QColor(c.get('r',1)*255,c.get('g',1)*255,c.get('b',1)*255)
	else:
		return QtGui.QColor(c)

class ScintillaCompat:
	def gotoLine(self, line, pos = 1):	
		self.setCursorPosition(line - 1, pos - 1)
		self.ensureLineVisible(line)

	def setProperty(self, id, *args):
		self._send(Sci.SCI_SETPROPERTY, id, *args)

	def getProperty(self, id, *args):
		self._send(Sci.SCI_GETPROPERTY, id, *args)

	# def setMarginType(self, marginId, typeId):
	# 	self._send(Sci.SCI_SETMARGINTYPEN, typeId)

	def markerDefine(self, markerId, styleId):
		self._send(Sci.SCI_MARKERDEFINE, markerId, styleId)

	def markerSetBackground(self, markerId, color):
		if not isinstance(color, QtGui.QColor):
			color=convertColor(color)
		self.setMarkerBackgroundColor(color ,markerId)

	def markerSetForeground(self, markerId, color):
		if not isinstance(color, QtGui.QColor):
			color=convertColor(color)
		self.setMarkerForegroundColor(color ,markerId)

	def markerSetAlpha(self, markerId, alpha):
		self._send(Sci.SCI_MARKERSETALPHA,alpha)

	def setCaretLineBackAlpha(self, alpha):
		self._send(Sci.SCI_SETCARETLINEBACKALPHA, alpha)

	def setLayoutCache(self, cacheMode):
		self._send(Sci.SCI_SETLAYOUTCACHE, cacheMode)

	def setBufferedDraw(self, enabled):
		self._send(Sci.SCI_SETBUFFEREDDRAW, enabled)

	def setUsePopUp(self, use):
		self._send(Sci.SCI_USEPOPUP, use)

	def setVisiblePolicy(self, a,b):
		self._send(Sci.SCI_SETVISIBLEPOLICY, a, b)


	def _send(self,*args):
		return self.SendScintilla(*args)
