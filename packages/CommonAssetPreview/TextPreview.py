from gii import app

if app.getModule('asset_browser'): 

	from gii.AssetEditor import AssetPreviewer
	from PyQt4 import QtGui, QtCore
	
	class TextPreviewer( AssetPreviewer ):
		def createWidget(self, container):
			self.textBrowser = QtGui.QTextBrowser(container)
			self.textBrowser.setLineWrapMode(0)
			self.textBrowser.setTabStopWidth(20)
			return self.textBrowser

		def accept(self, assetNode):
			return assetNode.isType( 'lua','script', 'text' )

		def onStart(self, assetNode):
			try:
				fp=open(assetNode.getAbsFilePath(),'r')
				text=fp.read().decode('utf8')
				self.textBrowser.setText(text)
				fp.close()
			except Exception, e:
				return False

		def onStop(self):
			pass

	TextPreviewer().register()
