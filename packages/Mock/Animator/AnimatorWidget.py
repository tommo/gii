import sys
import math

from gii.qt.controls.Timeline.TimelineView import TimelineView
from gii.qt.controls.GenericTreeWidget     import GenericTreeWidget
from gii.qt.controls.PropertyEditor        import PropertyEditor
from gii.qt.IconCache                      import getIcon
from gii.qt.helpers                        import addWidgetWithLayout, QColorF, unpackQColor

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QColor, QTransform

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance


_TRACK_SIZE = 20

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

AnimatorWidgetUI,BaseClass = uic.loadUiType( _getModulePath('animator.ui') )

class AnimatorTrackTreeItemDelegate( QtGui.QStyledItemDelegate ):
	def sizeHint( self, option, index ):
		return QSize( 10, _TRACK_SIZE )

##----------------------------------------------------------------##
class AnimatorTrackTree( GenericTreeWidget ):
	def __init__( self, *args, **option ):
		super( AnimatorTrackTree, self ).__init__( *args, **option )
		self.setItemDelegate( AnimatorTrackTreeItemDelegate() )
		self.setVerticalScrollMode( QtGui.QAbstractItemView.ScrollPerPixel )
		self.adjustingRange = False
		self.verticalScrollBar().rangeChanged.connect( self.onScrollRangeChanged )

	def getHeaderInfo( self ):
		return [ ('Name',80), ('Key', 20) ]

	def getRootNode( self ):
		return self.owner.getClipRoot()

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		return node.parent

	def getNodeChildren( self, node ):
		return [ clip for clip in node.children.values() ]

	def updateItemContent( self, item, node, **option ):
		pal = self.palette()
		defaultBrush = QColorF( .8,.8,.8 )
		name = None
		if isMockInstance( node, 'AnimatorTrackGroup' ):
			item.setText( 0, node.name )
			item.setIcon( 0, getIcon('track_group') )
		else:
			item.setText( 0, node.name )
			item.setIcon( 0, getIcon('track_number') )
			item.setIcon( 1, getIcon('track_key_0') )
		
	def onItemSelectionChanged(self):
		self.owner.onSelectionChanged( self.getSelection(), 'track' )

	def onItemChanged( self, item, col ):
		node = self.getNodeByItem( item )

	def resizeEvent( self, event ):
		super( AnimatorTrackTree, self ).resizeEvent( event )
		width = self.width() - 4
		self.setColumnWidth ( 0, width - 30 )
		self.setColumnWidth ( 1, 30 )

	def onItemExpanded( self, item ):
		node = item.node
		self.parentView.onTrackFolded( node, False )

	def onItemCollapsed( self, item ):
		node = item.node
		self.parentView.onTrackFolded( node, True )

	def onScrollRangeChanged( self, min, max ):
		if self.adjustingRange: return
		self.adjustingRange = True
		self.verticalScrollBar().setRange( min, max + self.height() - 25 )
		self.adjustingRange = False



##----------------------------------------------------------------##
class AnimatorClipListTree( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name',50) ]

	def getRootNode( self ):
		return self.owner

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		return None

	def getNodeChildren( self, node ):
		if node == self.owner:
			return self.owner.getClipList()
		else:
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
		self.owner.onSelectionChanged( self.getSelection(), 'clip' )

	def onItemChanged( self, item, col ):
		node = self.getNodeByItem( item )


##----------------------------------------------------------------##
class AnimatorTimelineWidget( TimelineView ):
	def getTrackNodes( self ):
		return self.owner.getTrackList()

	def getKeyNodes( self, trackNode ):
		keys = trackNode['keys']
		if keys:
			return [ key for key in keys.values() ]
		else:
			return []

	def getParentTrackNode( self, keyNode ):
		return keyNode['parent']

	def getTrackPos( self, trackNode ):
		return self.parentView.getTrackPos( trackNode )

	def isTrackVisible( self, trackNode ):
		return self.parentView.isTrackVisible( trackNode )

	def updateTrackContent( self, track, trackNode, **option ):
		# trackType = trackNode.getType( trackNode )
		# iconName = 'track_%s' % trackType
		# icon = getIcon( iconName ) or getIcon( 'obj' )
		# track.getHeader().setText( trackNode.name )
		# track.getHeader().setIcon( icon )
		pass

	def updateKeyContent( self, key, keyNode, **option ):
		# key.setText( keyNode.toString( keyNode ) )
		pass

	def getKeyParam( self, keyNode ):
		resizable = keyNode.isResizable( keyNode )
		length = resizable and keyNode.length or 0
		return float(keyNode.getPos( keyNode ))/1000.0, length, resizable 

	def onTrackDClicked( self, track, pos ):
		pass

		# clipTrack = track.node
		# self.module.addEvent( clipTrack, pos, None )
		# eventTypes = clipTrack.getEventTypes( clipTrack )
		# if not eventTypes:			
		# else:
		# 	self.module.promptAddEvent( clipTrack, pos )

	def formatPos( self, pos ):
		i = int( pos/1000 )
		f = int( pos - i*1000 )
		return '%d:%02d' % ( i, f/10 )

	def getRulerParam( self ):
		return dict( zoom = 0.1, pos_step = 1000, sub_step = 100 )
	

##----------------------------------------------------------------##
class AnimatorWidget( QtGui.QWidget, AnimatorWidgetUI ):
	"""docstring for AnimatorWidget"""
	def __init__( self, *args, **kwargs ):
		super(AnimatorWidget, self).__init__( *args, **kwargs )
		self.setupUi( self )

		self.treeTracks     = AnimatorTrackTree( parent = self )
		self.timeline       = AnimatorTimelineWidget( parent = self )
		self.treeClips      = AnimatorClipListTree( parent = self )
		self.propertyEditor = PropertyEditor( self )
		# self.treeTracks.setRowHeight( _TRACK_SIZE )

		self.treeTracks.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.treeTracks.verticalScrollBar().setStyleSheet('width:4px')
		self.treeTracks.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )

		self.toolbarClips = QtGui.QToolBar()
		self.toolbarPlay  = QtGui.QToolBar()
		self.toolbarTrack = QtGui.QToolBar()
		self.toolbarEdit  = self.timeline.toolbarEdit

		treeLayout = QtGui.QVBoxLayout(self.containerTree) 
		treeLayout.setSpacing( 0 )
		treeLayout.setMargin( 0 )
		treeLayout.addWidget( self.treeTracks )

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
		self.treeClips.verticalScrollBar().setStyleSheet('width:4px')

		propLayout = QtGui.QVBoxLayout(self.containerProperty) 
		propLayout.setSpacing( 0 )
		propLayout.setMargin( 0 )
		propLayout.addWidget( self.propertyEditor )

		# headerHeight = self.treeTracks.header().height()
		playToolLayout = QtGui.QVBoxLayout(self.containerPlayTool) 
		playToolLayout.setSpacing( 0 )
		playToolLayout.setMargin( 0 )
		playToolLayout.addWidget( self.toolbarPlay )		

		trackToolLayout = QtGui.QVBoxLayout(self.containerTrackTool) 
		trackToolLayout.setSpacing( 0 )
		trackToolLayout.setMargin( 0 )
		trackToolLayout.addWidget( self.toolbarTrack )		

		toolHeight = 20
		self.containerTrackTool.setFixedHeight( toolHeight )
		self.toolbarTrack.setFixedHeight( toolHeight )
		
		toolHeight = self.timeline.getRulerHeight()
		self.containerPlayTool.setFixedHeight( toolHeight )
		self.toolbarPlay.setFixedHeight( toolHeight )
		self.toolbarClips.setFixedHeight( toolHeight )
		self.treeTracks.header().hide()

		self.treeTracks.setObjectName( 'AnimatorTrackTree' )
		self.treeClips.setObjectName( 'AnimatorClipListTree' )
		self.toolbarPlay.setObjectName( 'TimelineToolBarPlay')
		self.toolbarTrack.setObjectName( 'TimelineToolBarTrack')

		#signals
		self.treeTracks.verticalScrollBar().valueChanged.connect( self.onTrackTreeScroll )


	def setOwner( self, owner ):
		self.owner = owner
		self.treeTracks.parentView = self
		self.treeClips.parentView = self
		self.timeline.parentView = self
		self.treeTracks.owner = owner
		self.treeClips.owner = owner
		self.timeline.owner = owner

		#signals
		self.timeline.keyChanged.connect( owner.onTimelineKeyChanged )

	def rebuild( self ):
		self.treeTracks.rebuild()
		self.treeClips.rebuild()
		self.timeline.rebuild()

	def isTrackVisible( self, trackNode ):
		return self.treeTracks.isNodeVisible( trackNode )

	def getTrackPos( self, trackNode ):
		rect = self.treeTracks.getNodeVisualRect( trackNode )
		return rect.y() + 2

	def onTrackTreeScroll( self, v ):
		self.timeline.setTrackViewScroll( -v )

	def onTrackFolded( self, track, folded ):
		self.timeline.updateTrackLayout()
