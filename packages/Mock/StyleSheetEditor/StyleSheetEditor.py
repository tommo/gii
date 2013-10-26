import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor

from gii.AssetEditor  import AssetEditorModule

from gii.moai.MOAIEditCanvas import  MOAIEditCanvas

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


def _fixDuplicatedName( names, name, id = None ):
	if id:
		testName = name + '_%d' % id
	else:
		id = 0
		testName = name
	#find duplicated name
	if testName in names:
		return _fixDuplicatedName( names, name, id + 1)
	else:
		return testName
##----------------------------------------------------------------##

_LOREM = '''Lorem ipsum dolor sit amet, consectetur adipisicing elit, '''

##----------------------------------------------------------------##
class MockStyleSheetEditor( AssetEditorModule ):
	"""docstring for MockStyleSheetEditor"""
	def __init__(self):
		super(MockStyleSheetEditor, self).__init__()
		self.editingAsset = None
		self.styleList={}
		self.styleSheetData = None
		self.currentStyle   = None
	
	def getName(self):
		return 'mock.stylesheet_editor'

	def getDependency(self):
		return [ 'qt', 'moai' ]

	def onLoad(self):
		self.container = self.requestDocumentWindow( 'MockStyleSheetEditor',
				title       = 'Style Sheet Editor',
				size        = (500,300),
				minSize     = (500,300),
				dock        = 'right'
				# allowDock = False
			)

		self.window = window = self.container.addWidgetFromFile(
			_getModulePath('styleEditor.ui')
		)
		
		self.previewCanvas = addWidgetWithLayout(
			MOAIEditCanvas(window.canvasContainer),
			window.canvasContainer
		)

		self.previewCanvas.loadScript( _getModulePath('StyleSheetPreview.lua') )

		self.singlePreviewCanvas = addWidgetWithLayout(
			MOAIEditCanvas(window.singlePreviewContainer),
			window.singlePreviewContainer
		)

		self.singlePreviewCanvas.loadScript( _getModulePath('SingleStylePreview.lua') )

		window.listStyles.itemSelectionChanged.connect(self.onItemSelectionChanged)
		window.listStyles.setSortingEnabled(True)

		window.toolAdd.clicked.connect(self.onAddStyle)
		window.toolRemove.clicked.connect(self.onRemoveStyle)
		window.toolClone.clicked.connect(self.onCloneStyle)
		
		window.buttonColor.clicked.connect( 
			lambda : self.onPickColor( 
					requestColor( 'Font Color', 
						QColorF( *self.currentStyle.get('color', [1,1,1,1]) ),
						onColorChanged = self.onPickColor
						)
				)
			)
		window.spinFontSize.valueChanged.connect(self.onSizeChanged)
		window.comboFont.currentIndexChanged.connect(self.onFontChanged)
		window.checkAllowScale.stateChanged.connect(self.onAllowScaleChanged)

		window.textPreview.textChanged.connect( self.onPreviewTextChanged )

		window.comboAlign.addItems(['Align Left','Align Center','Align Right'])
		window.comboAlign.currentIndexChanged.connect( self.onAlignChanged )

		signals.connect('asset.modified', self.onAssetModified)
		self.container.setEnabled( False )

	def refreshFontNames(self):
		self.window.comboFont.clear()
		for node in AssetLibrary.get().enumerateAsset( ( 'font_ttf', 'font_bmfont' ) ):
			self.window.comboFont.addItem( node.getPath(), node )		
		
	def onSetFocus(self):
		self.container.show()
		self.container.raise_()
		self.container.activateWindow()
		self.container.setFocus()

	def startEdit( self, node, subnode=None ):
		self.setFocus()

		if node == self.editingAsset: return
		self.saveAsset()
		self.container.setEnabled( True )
		
		self.editingAsset = node
		self.container.setDocumentName( node.getPath() )

		self.window.settingPanel.setEnabled( False )
		self.previewText = node.getMetaData( 'previewText', _LOREM )
		listStyles = self.window.listStyles
		self.window.textPreview.setPlainText( self.previewText )

		self.styleSheetData = node.loadAsJson()
		listStyles.clear()
		for style in self.styleSheetData.get('styles', []):
			listStyles.addItem( style.get('name','unamed') )

		self.previewCanvas.safeCall('setStyleSheet', self.styleSheetData)

	def stopEdit( self ):
		if self.editingAsset:
			self.saveAsset()
			self.container.setEnabled( False )
			self.editingAsset = None
			self.listStyles.clear()

	def saveAsset(self):
		if not self.styleSheetData: return
		self.editingAsset.saveAsJson(self.styleSheetData)

	def findStyle(self, name):
		if not self.styleSheetData: return None
		for style in self.styleSheetData.get('styles', []):
			if style.get('name') == name : return style
		return None

	def addStyle( self, name, item ):
		styleItems = self.styleSheetData['styles']
		names = [ item0['name'] for item0 in styleItems ]
		name = _fixDuplicatedName( names , item['name'] )
		item['name'] = name
		styleItems.append( item )
		
		self.saveAsset()

		listItem = QtGui.QListWidgetItem( name )
		self.window.listStyles.addItem( listItem )
		listItem.setSelected( True )

	def onStart( self ):
		self.refreshFontNames()
		pass

	def onStop( self ):
		self.saveAsset()

	def onAddStyle( self ):
		name = requestString('Creating Text Style', 'Enter style name')
		if not name: return 
		item = { 'name':name, 'font':None, 'size':12, 'color':[1,1,1,1], 'allowScale':True }
		self.addStyle( name, item )

	def onRemoveStyle( self ):
		listStyles=self.window.listStyles
		selected=listStyles.selectedItems()
		if not selected: return
		items = self.styleSheetData.get('styles',[])
		for item in selected:
			name = item.text()
			sp = self.findStyle( name )
			assert sp
			idx =  items.index( sp )
			items.pop(idx)
			row = listStyles.row( item )
			listStyles.takeItem( row )
		self.saveAsset()
		pass

	def onCloneStyle( self ):
		if not self.currentStyle: return
		newStyle = self.currentStyle.copy()
		self.addStyle( newStyle['name'], newStyle )

	def updateCurrentStyle( self ):
		self.previewCanvas.safeCall( 'updateStyle', self.currentStyle )
		self.singlePreviewCanvas.safeCall( 'updatePreview' )

	def onAssetModified( self, asset ):
		pass

	def onItemSelectionChanged( self ):
		for item in self.window.listStyles.selectedItems():
			style = self.findStyle( item.text() )
			self.currentStyle = style
			break

		if style:
			self.window.settingPanel.setEnabled( True )			
			fontIdx = self.window.comboFont.findText( style['font'] )
			if fontIdx < 0: fontIdx = 0 #TODO: use default?
			self.window.comboFont.setCurrentIndex( -1 )
			self.window.comboFont.setCurrentIndex( fontIdx )
			self.window.spinFontSize.setValue( style.get('size', 12) )
			self.window.checkAllowScale.setChecked( style.get('allowScale', True) )
			color = style.get('color', [1,1,1,1])
			self.onPickColor( QColorF( *color ) )
			self.singlePreviewCanvas.safeCall( 'updatePreview' )		

	def onSizeChanged(self, size):
		self.singlePreviewCanvas.safeCall( 'setFontSize', size )
		self.currentStyle['size'] = size

		self.updateCurrentStyle()
		pass


	def onPickColor( self, col ):
		if not col: return
		self.updateCurrentStyle()
		self.window.buttonColor.setStyleSheet('''
			background-color: %s;
			border: 1px solid rgb(179, 179, 179);
			''' % col.name()
			)
		self.currentStyle[ 'color' ] = list( unpackQColor(col) )
		self.singlePreviewCanvas.safeCall( 'setFontColor', *unpackQColor(col) )
		self.updateCurrentStyle()

	def onFontChanged( self, index ):
		fontNode = self.window.comboFont.itemData(index)
		if self.currentStyle and fontNode:
			self.singlePreviewCanvas.safeCall( 'setFont', fontNode.getPath().encode('utf-8') )
			self.currentStyle['font'] = fontNode.getPath()
			self.updateCurrentStyle()

	def onAllowScaleChanged( self, state ):
		checked = self.window.checkAllowScale.isChecked() 
		self.singlePreviewCanvas.safeCall( 'setAllowScale', checked )
		self.currentStyle['allowScale'] = checked 
		self.updateCurrentStyle()

	def onAlignChanged( self, index ):
		text = self.window.comboAlign.itemText( index )
		if text:
			self.previewCanvas.safeCall('setAlign', text.encode('utf-8'))

	def onPreviewTextChanged( self ):
		self.previewText = self.window.textPreview.toPlainText() 
		self.previewCanvas.safeCall( 'setText',  self.previewText )
		self.editingAsset.setMetaData('previewText', self.previewText )


##----------------------------------------------------------------##

MockStyleSheetEditor().register()

