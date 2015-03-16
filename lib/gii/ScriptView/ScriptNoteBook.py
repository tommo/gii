import json
import os

from PyQt4      import QtGui, QtCore

from gii.core   import app
from gii.qt.controls.CodeBox import CodeBox

class ScriptPage( CodeBox ):
	def __init__(self, *args ):
		super(ScriptPage, self).__init__( *args )
		
##----------------------------------------------------------------##
class ScriptNoteBook(QtGui.QTabWidget):
	"""docstring for ScriptNoteBook"""
	def __init__(self, parent):
		super(ScriptNoteBook, self).__init__(parent)
		self.setDocumentMode(True)
		self.pages={}
		self.defaultSetting=json.load(
				file( app.getPath('data/script_settings.json'), 'r' )
			)

	def getPageByFile(self, path, createIfNotFound=True):
		path=path.encode('utf-8')
		if not os.path.exists(path): return None

		page=self.pages.get(path, False)
		if not page:
			if not createIfNotFound: return None
			#create
			page = ScriptPage(self)
			self.addTab(page, path)
			page.applySetting(self.defaultSetting)
			page.setReadOnly(True)
			page.path=path
			page.refreshCode()
			self.pages[path]=page
		else:
			page.checkFileModified()
		return page

	def selectPage(self, page):
		idx=self.indexOf(page)
		if idx>=0:
			self.setCurrentIndex(idx)

	def clearAllPages(self):
		for k in self.pages:
			p=self.pages[k]
			idx=self.indexOf(p)
			if idx>0:
				self.removeTab(idx)
			p.deleteLater()
		self.pages={}

	def clearHilight(self, hilightType):
		_hilight=None
		if hilightType=='normal': 
			_hilight=MARKER_HILIGHT_NORMAL
		elif hilightType=='serious': 
			_hilight=MARKER_HILIGHT_SERIOUS

		for k in self.pages:
			p=self.pages[k]
			p.markerDeleteAll(_hilight)

		