import sys
import math

from gii.qt.controls.Timeline.TimelineView import TimelineView
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.qt.controls.PropertyEditor import PropertyEditor

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

AnimatorWidgetUI,BaseClass = uic.loadUiType( _getModulePath('animator.ui') )
##----------------------------------------------------------------##
class AnimatorTrackTree( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name',150), ('Key', 30), ('',-1) ]

	def getRootNode( self ):
		return None

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		return None

	def getNodeChildren( self, node ):
		if isMockInstance( node, 'Game' ):
			result = []
			for item in node.layers.values():
				if item.name == '_GII_EDITOR_LAYER': continue
				result.append( item )
			return reversed( result )
		return []

	def updateItemContent( self, item, node, **option ):
		pal = self.palette()
		defaultBrush = QColorF( .8,.8,.8 )
		name = None
		if isMockInstance( node, 'AnimatorTrackGroup' ):
			item.setText( 0, node.name )
			item.setIcon( 0, getIcon('folder') )
		else:
			item.setText( 0, node.name )
			item.setIcon( 0, getIcon('normal') )
		
	def onItemSelectionChanged(self):
		selections = self.getSelection()

	def onItemChanged( self, item, col ):
		node = self.getNodeByItem( item )
		# app.getModule('layer_manager').changeLayerName( layer, item.text(0) )
		#TODO

	# def onClicked(self, item, col):
	# 	if col == 1: #editor view toggle
	# 		app.getModule('layer_manager').toggleEditVisible( self.getNodeByItem(item) )
	# 	elif col == 2: #lock toggle
	# 		app.getModule('layer_manager').toggleLock( self.getNodeByItem(item) )
	# 	elif col == 3:
	# 		app.getModule('layer_manager').toggleSolo( self.getNodeByItem(item) )


##----------------------------------------------------------------##
class AnimatorClipListTree( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name',150), ('Key', 30), ('',-1) ]

	def getRootNode( self ):
		return None

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		return None

	def getNodeChildren( self, node ):
		if isMockInstance( node, 'Game' ):
			result = []
			for item in node.layers.values():
				if item.name == '_GII_EDITOR_LAYER': continue
				result.append( item )
			return reversed( result )
		return []

	def updateItemContent( self, item, node, **option ):
		pal = self.palette()
		defaultBrush = QColorF( .8,.8,.8 )
		name = None
		if isMockInstance( node, 'AnimatorTrackGroup' ):
			item.setText( 0, node.name )
			item.setIcon( 0, getIcon('folder') )
		else:
			item.setText( 0, node.name )
			item.setIcon( 0, getIcon('normal') )
		
	def onItemSelectionChanged(self):
		selections = self.getSelection()

	def onItemChanged( self, item, col ):
		node = self.getNodeByItem( item )

##----------------------------------------------------------------##
class AnimatorWidget( QtGui.QWidget, AnimatorWidgetUI ):
	"""docstring for AnimatorWidget"""
	def __init__( self, *args, **kwargs ):
		super(AnimatorWidget, self).__init__( *args, **kwargs )
		self.setupUi( self )
		

		self.tree      = AnimatorTrackTree( parent = self )
		self.timeline  = self.createTimelineView()
		self.treeClips = AnimatorClipListTree( parent = self )
		self.propertyEditor = PropertyEditor( self )
		
		self.toolbarClips = QtGui.QToolBar()
		self.toolbarPlay  = QtGui.QToolBar()
		self.toolbarEdit  = self.timeline.toolbarEdit

		treeLayout = QtGui.QVBoxLayout(self.containerTree) 
		treeLayout.setSpacing( 0 )
		treeLayout.setMargin( 0 )
		treeLayout.addWidget( self.tree )

		rightLayout = QtGui.QVBoxLayout(self.containerRight) 
		rightLayout.setSpacing( 0 )
		rightLayout.setMargin( 0 )
		rightLayout.addWidget( self.timeline )

		treeClipsLayout = QtGui.QVBoxLayout(self.containerClips) 
		treeClipsLayout.setSpacing( 0 )
		treeClipsLayout.setMargin( 0 )
		treeClipsLayout.addWidget( self.toolbarClips )
		treeClipsLayout.addWidget( self.treeClips )
		self.treeClips.setHeaderHidden( True )

		propLayout = QtGui.QVBoxLayout(self.containerProperty) 
		propLayout.setSpacing( 0 )
		propLayout.setMargin( 0 )
		propLayout.addWidget( self.propertyEditor )

		# headerHeight = self.tree.header().height()
		toolHeight = self.timeline.getRulerHeight()
		playToolLayout = QtGui.QVBoxLayout(self.containerPlayTool) 
		playToolLayout.setSpacing( 0 )
		playToolLayout.setMargin( 0 )
		playToolLayout.addWidget( self.toolbarPlay )		
		self.containerPlayTool.setFixedHeight( toolHeight )
		self.toolbarPlay.setFixedHeight( toolHeight )
		self.toolbarClips.setFixedHeight( toolHeight )
		self.tree.header().hide()

	def createTimelineView( self ):
		return TimelineView( parent = self )	

	def rebuild( self ):
		self.timeline.rebuild()


# if __name__ == '__main__':
# 	from random import random

# 	_keyid = 1
# 	class TestKey():
# 		def __init__( self, track ):
# 			global _keyid
# 			_keyid += 1
# 			self.name = 'key - %d' % _keyid
# 			# self.length = random()*500/1000.0
# 			self.length = 0.0
# 			self.pos    = ( random()*1000 + 50 ) /1000.0
# 			self.track  = track

# 	class TestTrack():
# 		def __init__( self, name ):
# 			self.name = name
# 			self.keys = [
# 				TestKey( self ),
# 				TestKey( self ),
# 				TestKey( self ),
# 				TestKey( self )
# 			]

# 	class TestEvent():
# 		def __init__( self ):
# 			self.name = 'event'

# 	dataset = [
# 		TestTrack( 'track' ),
# 		TestTrack( 'track0' ),
# 		TestTrack( 'track1' ),
# 		TestTrack( 'track2' ),
# 		TestTrack( 'track3' ),
# 		TestTrack( 'track1' ),
# 		TestTrack( 'track2' ),
# 		TestTrack( 'track3' ),
# 		TestTrack( 'track1' ),
# 		TestTrack( 'track2' ),
# 		TestTrack( 'track3' )
# 	]

# 	class TestTimeline( TimelineView ):
# 		def getTrackNodes( self ):
# 			return dataset

# 		def getKeyNodes( self, trackNode ):
# 			return trackNode.keys

# 		def getKeyParam( self, keyNode ): #pos, length, resizable
# 			return keyNode.pos, keyNode.length, True

# 		def getParentTrackNode( self, keyNode ):
# 			return keyNode.track

# 		def updateTrackContent( self, track, trackNode, **option ):
# 			# track.getHeaderItem().setText( trackNode.name )
# 			pass

# 		def updateKeyContent( self, key, keyNode, **option ):
# 			pass

# 		def formatPos( self, pos ):
# 			i = int( pos/1000 )
# 			f = int( pos - i*1000 )
# 			return '%d:%02d' % ( i, f/10 )

# 		def getRulerParam( self ):
# 			return dict( zoom = 1 )
# 			# return dict( zoom = 5 )

# 	class TestAnimatorWidget(AnimatorWidget):
# 		def createTimelineView( self ):
# 			return TestTimeline( parent = self )
			
# 	app = QtGui.QApplication( sys.argv )
# 	styleSheetName = 'gii.qss'
# 	app.setStyleSheet(
# 			open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
# 		)
# 	demo = TestAnimatorWidget()
# 	demo.resize( 600, 300 )
# 	demo.show()
# 	demo.raise_()
# 	demo.rebuild()
# 	c = demo.timeline.curveView.addCurve()
# 	c.startVert.setPos( 100, 50 )
# 	v = c.appendVert()
# 	v.setPos( 150,  50 )
# 	# v.setSpanMode( SPAN_MODE_BEZIER )
# 	v = c.appendVert()
# 	v.setPos( 250,  50 )
# 	# v.setSpanMode( SPAN_MODE_BEZIER )
# 	v = c.appendVert()
# 	v.setPos( 350,  120 )
# 	# # timeline.setZoom( 10 )
# 	# # timeline.selectTrack( dataset[1] )
# 	# timeline.selectKey( dataset[1].keys[0] )

# 	app.exec_()
