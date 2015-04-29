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
		option['editable']  = True
		option['drag_mode'] = 'internal'
		super( AnimatorTrackTree, self ).__init__( *args, **option )
		self.setItemDelegate( AnimatorTrackTreeItemDelegate() )
		self.setVerticalScrollMode( QtGui.QAbstractItemView.ScrollPerPixel )
		self.adjustingRange = False
		self.verticalScrollBar().rangeChanged.connect( self.onScrollRangeChanged )		
		self.setIndentation( 10 )

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

	def getItemFlags( self, node ):
		flags = {}
		if isMockInstance( node, 'AnimatorTrackGroup' ):
			flags['editable'] = True
		else:
			flags['editable'] = False
		return flags

	def updateItemContent( self, item, node, **option ):
		pal = self.palette()
		defaultBrush = QColorF( .8,.8,.8 )
		name = None

		if isMockInstance( node, 'AnimatorTrackGroup' ):
			item.setText( 0, node.name )
			item.setIcon( 0, getIcon('track_group') )
		elif isMockInstance( node, 'AnimatorClipSubNode' ):
			item.setText( 0, node.toString( node ) )
			item.setIcon( 0, getIcon('track_number') )
			item.setIcon( 1, getIcon('track_key_0') )
		
	def onItemSelectionChanged(self):
		self.owner.onSelectionChanged( self.getSelection(), 'track' )

	def onItemChanged( self, item, col ):
		node = self.getNodeByItem( item )

	def resizeEvent( self, event ):
		super( AnimatorTrackTree, self ).resizeEvent( event )
		width = self.width() - 4
		self.setColumnWidth ( 0, width - 25 )
		self.setColumnWidth ( 1, 25 )

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

	def mousePressEvent( self, ev ):
		item = self.itemAt( ev.pos() )
		if not item:
			self.clearSelection()
		else:
			return super( AnimatorTrackTree, self ).mousePressEvent( ev )

	def dropEvent( self, ev ):		
		p = self.dropIndicatorPosition()
		pos = False
		if p == QtGui.QAbstractItemView.OnItem: #reparent
			pos = 'on'
		elif p == QtGui.QAbstractItemView.AboveItem:
			return False
		elif p == QtGui.QAbstractItemView.BelowItem:
			return False
		else:
			pos = 'viewport'

		target = self.itemAt( ev.pos() )
		if pos == 'on':
			# self.owner.doCommand( 'animator/reparent_track',  )
			# self.module.doCommand( 'scene_editor/reparent_entity', target = target.node )
			pass
		elif pos == 'viewport':
			# self.module.doCommand( 'scene_editor/reparent_entity', target = 'root' )
			pass


		super( GenericTreeWidget, self ).dropEvent( ev )


##----------------------------------------------------------------##
class AnimatorClipListTree( GenericTreeWidget ):
	def __init__( self, *args, **kwargs ):
		super( AnimatorClipListTree, self ).__init__( *args, **kwargs )
		self.setIndentation( 0 )
		self.option['editable'] = True

	def getHeaderInfo( self ):
		return [ ('Name',50) ]

	def getRootNode( self ):
		return self.owner

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		if node == self.owner:
			return None
		return self.owner

	def getNodeChildren( self, node ):
		if node == self.owner:
			return self.owner.getClipList()
		else:
			return []

	def updateItemContent( self, item, node, **option ):
		pal = self.palette()
		defaultBrush = QColorF( .8,.8,.8 )
		name = None
		item.setText( 0, node.name )
		item.setIcon( 0, getIcon('clip') )
		
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
		return keyNode.getPos( keyNode ), length, resizable 

	def onTrackDClicked( self, track, pos ):
		pass

		# clipTrack = track.node
		# self.module.addEvent( clipTrack, pos, None )
		# eventTypes = clipTrack.getEventTypes( clipTrack )
		# if not eventTypes:			
		# else:
		# 	self.module.promptAddEvent( clipTrack, pos )

	def onSelectionChanged( self, selection ):
		if selection:
			self.parentView.setPropertyTarget( selection[0] )
		else:
			self.parentView.setPropertyTarget( None )

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
		self.propertyEditor.propertyChanged.connect( self.onPropertyChanged )
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
		self.timeline.keyChanged.connect( self.onKeyChanged )

	def rebuild( self ):
		self.treeTracks.rebuild()
		self.treeClips.rebuild()
		self.timeline.rebuild()

	def rebuildTimeline( self ):
		self.timeline.rebuild()
		self.treeTracks.rebuild()

	def createClip( self ):
		pass

	def addClip( self, clip, focus = False ):
		self.treeClips.addNode( clip )
		if focus:
			self.treeClips.selectNode( clip )

	def addKey( self, key, focus = False ):
		self.addTrack( key.parent )
		self.timeline.addKey( key )

	def addTrack( self, track ):
		self.treeTracks.addNode( track )
		self.timeline.rebuild()

	def removeClip( self, clip ):
		self.treeClips.removeNode( clip )

	def removeTrack( self, track ):
		self.treeTracks.removeNode( track )
		self.timeline.removeTrack( track )

	def setPropertyTarget( self, target ):
		self.propertyEditor.setTarget( target )

	def isTrackVisible( self, trackNode ):
		return self.treeTracks.isNodeVisible( trackNode )

	def getTrackPos( self, trackNode ):
		rect = self.treeTracks.getNodeVisualRect( trackNode )
		return rect.y() + 2

	def onTrackTreeScroll( self, v ):
		self.timeline.setTrackViewScroll( -v )

	def onTrackFolded( self, track, folded ):
		self.timeline.updateTrackLayout()
		self.timeline.clearSelection()

	def onKeyChanged( self, key, pos, length ):
		self.propertyEditor.refreshFor( key )
		self.owner.onTimelineKeyChanged( key, pos, length )

	def onKeyRemoving( self, key ):
		return self.owner.removeKey( key )

	def onPropertyChanged( self, obj, fid, value ):
		if fid == 'pos' or fid == 'length':
			self.timeline.refreshKey( obj )

	def setEnabled( self, enabled ):
		super( AnimatorWidget, self ).setEnabled( enabled )
		self.timeline.setEnabled( enabled )
