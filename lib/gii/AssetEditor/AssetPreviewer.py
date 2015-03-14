import random
from abc import ABCMeta, abstractmethod

from gii.core         import *
from gii.qt.dialogs   import requestString
from gii.qt.controls.AssetTreeView import AssetTreeView

from AssetEditor      import AssetEditorModule


from PyQt4            import QtCore, QtGui, uic
from PyQt4.QtCore     import Qt

##----------------------------------------------------------------##
class ModAssetPreviewer( AssetEditorModule ):
	def getName( self ):
		return 'asset_previewer'

	def getDependency( self ):
		return ['asset_browser']

	def __init__(self):
		super(ModAssetPreviewer, self).__init__()
		self.previewers        = []
		self.activePreviewer   = None		
		self.target = None

	def onLoad( self ):
		self.container = self.requestDockWindow('AssetPreview',
				title   = 'Asset View',
				dock    = 'left',
				minSize = (100,100)
			)

		self.previewerContainer = QtGui.QStackedWidget()
		self.previewerContainer.setSizePolicy(
				QtGui.QSizePolicy.Expanding, 
				QtGui.QSizePolicy.Expanding
			)
		self.previewerContainer.setMinimumSize(100,100)
		self.container.addWidget( self.previewerContainer, expanding=False )
		self.nullPreviewer = self.registerPreviewer( NullAssetPreviewer() )		

		signals.connect( 'selection.changed', self.onSelectionChanged )
		signals.connect( 'asset.modified', self.onAssetModified )


	def onStart( self ):
		for previewer in self.previewers:
			self._loadPreviewer(previewer)

	def onSelectionChanged( self, selection, key ):
		if key != 'asset': return
		if self.activePreviewer:
			self.activePreviewer.onStop()
			self.target = None

		if selection and isinstance( selection[0], AssetNode ) :
			target = selection[0]
			for previewer in self.previewers:
				if previewer.accept(target):
					self._startPreview(previewer, target)
					return

		self._startPreview(self.nullPreviewer, None)

	def onAssetModified( self, assetNode ):
		if assetNode == self.target:
			self.refreshPreviewr()

	def refreshPreviewr( self ):
		if self.activePreviewer:
			self.activePreviewer.onStop()
			self._startPreview( self.activePreviewer, self.target )

	def _startPreview(self, previewer, selection):
		idx = previewer._stackedId
		self.target = selection
		self.previewerContainer.setCurrentIndex(idx)
		self.activePreviewer=previewer		
		previewer.onStart(selection)


	def _loadPreviewer(self, previewer):
		widget = previewer.createWidget(self.previewerContainer)
		assert isinstance(widget,QtGui.QWidget), 'widget expected from previewer'
		idx = self.previewerContainer.addWidget(widget)
		previewer._stackedId=idx
		previewer._widget=widget

	def registerPreviewer(self, previewer):
		self.previewers.insert(0, previewer) #TODO: use some dict?
		if self.alive: self._loadPreviewer(previewer)		
		return previewer


##----------------------------------------------------------------##
class AssetPreviewer(object):
	def register( self ):
		return app.getModule('asset_previewer').registerPreviewer( self )

	def accept(self, selection):
		return False

	def createWidget(self):
		return None

	def onStart(self, selection):
		pass

	def onStop(self):
		pass

##----------------------------------------------------------------##		
class NullAssetPreviewer(AssetPreviewer):
	def createWidget(self,container):
		self.label = QtGui.QLabel(container)
		self.label.setAlignment(QtCore.Qt.AlignHCenter)
		self.label.setText('NO PREVIEW')
		self.label.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Expanding
				)
		return self.label

	def onStart(self, selection):
		pass
		# self.label.setParent(container)

	def onStop(self):
		pass
##----------------------------------------------------------------##

ModAssetPreviewer().register()
