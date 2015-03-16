from gii import app
from mock import _MOCK

if app.getModule('asset_browser'): 

	from gii.AssetEditor import AssetPreviewer
	from PyQt4 import QtGui, QtCore
	from gii.qt.controls.PropertyEditor  import PropertyEditor

	##----------------------------------------------------------------##		
	class SerializableAssetPreviewer(AssetPreviewer):
		def createWidget(self,container):
			self.editor = PropertyEditor( container )
			return self.editor

		def accept(self, assetNode):
			return assetNode.getManager().getMetaType() in [ 'serializable' ]

		def onStart(self, selection):
			data = _MOCK.loadAsset( selection.getPath() )
			if data:
				asset, luaAssetNode = data
				self.editor.setTarget( asset )
			else:
				self.editor.setTarget( None )

		def onStop(self):
			self.editor.setTarget( None )

	SerializableAssetPreviewer().register();
