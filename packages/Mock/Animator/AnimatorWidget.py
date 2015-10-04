import sys
import math

from gii.qt.controls.GraphicsView.TimelineView import *
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

class AnimatorTrackTreeItem(QtGui.QTreeWidgetItem):
	def __lt__(self, other):
		node0 = self.node
		node1 = hasattr(other, 'node') and other.node or None
		if not node1:
			return True
		tree = self.treeWidget()

		# if not tree:
		# 	col = 0
		# else:
		# 	col = tree.sortColumn()
		t0 = isMockInstance( node0, 'AnimatorTrackGroup' ) and 'group' or 'node'
		t1 = isMockInstance( node1, 'AnimatorTrackGroup' ) and 'group' or 'node'

		if t1!=t0:			
			if tree.sortOrder() == 0:
				if t0 == 'group': return True
				if t1 == 'group': return False
			else:
				if t0 == 'group': return False
				if t1 == 'group': return True
		return super( AnimatorTrackTreeItem, self ).__lt__( other )
		# return node0.getName().lower()<node1.getName().lower()

##----------------------------------------------------------------##
class AnimatorTrackTree( GenericTreeWidget ):
	layoutChanged = pyqtSignal()
	def __init__( self, *args, **option ):
		option['editable']  = True
		option['drag_mode'] = 'internal'
		option['multiple_selection'] = True
		# option['alternating_color'] = True
		super( AnimatorTrackTree, self ).__init__( *args, **option )
		self.setItemDelegate( AnimatorTrackTreeItemDelegate() )
		self.setVerticalScrollMode( QtGui.QAbstractItemView.ScrollPerPixel )
		self.adjustingRange = False
		self.verticalScrollBar().rangeChanged.connect( self.onScrollRangeChanged )		
		self.setIndentation( 14 )
		self.setAttribute(Qt.WA_MacShowFocusRect, False)
		self.setTextElideMode( Qt.ElideMiddle )

	def event( self, ev ):
		if ev.type() == 26:
			self.parentView.updateTrackLayout()
		# print ev.type(), ev
		return super( AnimatorTrackTree, self ).event( ev )
	# def paintEvent( self, ev ):
	# 	super( AnimatorTrackTree, self ).paintEvent( ev )
	# 	self.layoutChanged.emit()

	def getHeaderInfo( self ):
		return [ ('Name',80), ('Key', 20) ]

	def getRootNode( self ):
		return self.owner.getClipRoot()

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		for node, item in self.nodeDict.items():
			if not item: continue
			expanded = not node._folded
			item.setExpanded( expanded )

	def createItem( self, node ):
		return AnimatorTrackTreeItem()

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
			item.setText( 0, node.toString( node ) )
			item.setIcon( 0, getIcon('track_group') )
		elif isMockInstance( node, 'AnimatorClipSubNode' ):
			item.setText( 0, node.toString( node ) )
			item.setIcon( 0, getIcon(node.getIcon( node )) )
			item.setIcon( 1, getIcon('track_key_0') )
		
	def onItemSelectionChanged(self):
		self.parentView.onTrackSelectioChanged()

	def onItemChanged( self, item, col ):
		self.owner.renameTrack( item.node, item.text(0) )

	def resizeEvent( self, event ):
		super( AnimatorTrackTree, self ).resizeEvent( event )
		width = self.width() - 4
		self.setColumnWidth ( 0, width - 25 )
		self.setColumnWidth ( 1, 25 )

	def onItemExpanded( self, item ):
		if self.rebuilding: return
		node = item.node
		self.parentView.onTrackFolded( node, False )

	def onItemCollapsed( self, item ):
		if self.rebuilding: return
		node = item.node
		self.parentView.onTrackFolded( node, True )

	def onScrollRangeChanged( self, min, max ):
		if self.adjustingRange: return
		self.adjustingRange = True
		maxRange = max + self.height() - 25
		self.verticalScrollBar().setRange( min, maxRange )
		self.parentView.setTrackViewScrollRange( maxRange )
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
			pos = 'above'
		elif p == QtGui.QAbstractItemView.BelowItem:
			pos = 'below'
		else:
			pos = 'viewport'
		
		if pos == 'above' or pos =='below':
			#TODO: reorder
			ev.setDropAction( Qt.IgnoreAction )
			return

		target = self.itemAt( ev.pos() )
		source = self.getSelection()

		if pos == 'on':
			targetTrack = target.node
		else:
			targetTrack = 'root'

		succ = self.owner.doCommand( 
			'scene_editor/animator_reparent_track', 
			source = source,
			target = targetTrack
		)
		
		if not succ:
			ev.setDropAction( Qt.IgnoreAction )
		return super( AnimatorTrackTree, self ).dropEvent( ev )


##----------------------------------------------------------------##
class AnimatorClipListTree( GenericTreeWidget ):
	def __init__( self, *args, **kwargs ):
		super( AnimatorClipListTree, self ).__init__( *args, **kwargs )
		self.setIndentation( 10 )
		self.option['editable'] = True

	def getHeaderInfo( self ):
		return [ ('Name',50) ]

	def getRootNode( self ):
		return self.owner.getRootClipGroup()

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		return node.parentGroup

	def getNodeChildren( self, node ):
		if isMockInstance( node, 'AnimatorClipGroup' ):
			children = node.getChildNodes( node )
			return [ child for child in children.values() ]
		else:
			return []

	def updateItemContent( self, item, node, **option ):
		if isMockInstance( node, 'AnimatorClipGroup' ):
			# pal = self.palette()
			# defaultBrush = QColorF( .8,.8,.8 )
			# name = None
			item.setText( 0, node.name )
			item.setIcon( 0, getIcon('folder') )
		else:
			item.setText( 0, node.name )
			item.setIcon( 0, getIcon('clip') )
		
	def onItemSelectionChanged(self):
		self.parentView.onClipSelectioChanged()

	def onItemChanged( self, item, col ):
		self.owner.renameClip( item.node, item.text(0) )


##----------------------------------------------------------------##
class AnimatorTimelineWidget( TimelineView ):
	def getTrackNodes( self ):
		return self.owner.getTrackList()

	def getMarkerNodes( self ):
		return self.owner.getMarkerList()

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

	def updateMarkerContent( self, marker, markerNode, **option ):
		name = markerNode.getName( markerNode )
		marker.setText( name )

	def updateKeyContent( self, key, keyNode, **option ):
		text = keyNode.toString( keyNode )
		key.setText( text )

	def getMarkerParam( self, markerNode ):
		return markerNode.getPos( markerNode )

	def getKeyParam( self, keyNode ):
		resizable = keyNode.isResizable( keyNode )
		length    = resizable and keyNode.length or 0
		return keyNode.getPos( keyNode ), length, resizable

	def onSelectionChanged( self, selection ):
		if selection:
			self.parentView.setPropertyTarget( selection[0] )
		else:
			self.parentView.setPropertyTarget( None )

	def onMarkerSelectionChanged( self, markerSelection ):
		if markerSelection:
			self.parentView.setPropertyTarget( markerSelection[0] )
		else:
			self.parentView.setPropertyTarget( None )

	def formatPos( self, pos ):
		i = int( pos/1000 )
		f = int( pos - i*1000 )
		return '%d:%02d' % ( i, f/10 )

	def getRulerParam( self ):
		return dict( zoom = 0.1, pos_step = 1000, sub_step = 100 )

	def createTrackItem( self, trackNode, **options ):
		if isMockInstance( trackNode, 'AnimatorEventTrack' ):
			return TimelineEventTrackItem()
		else:
			return TimelineTrackItem()

	def onEditTool( self, toolName ):
		self.owner.onTimelineEditTool( toolName )	

	def onTrackClicked( self, track, pos ):
		trackNode = track.node
		self.parentView.selectTrack( trackNode )
		
	def onKeyRemoving( self, keyNode ):
		return self.parentView.onKeyRemoving( keyNode )

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

		self.timeline.toolbuttonCurveModeLinear   .setIcon( getIcon( 'curve_mode_linear'   ) )
		self.timeline.toolbuttonCurveModeConstant .setIcon( getIcon( 'curve_mode_constant' ) )
		self.timeline.toolbuttonCurveModeBezier   .setIcon( getIcon( 'curve_mode_bezier'   ) )
		self.timeline.toolbuttonCurveModeBezierS  .setIcon( getIcon( 'curve_mode_bezier_s' ) )

		self.timeline.toolbuttonAddMarker .setIcon( getIcon( 'marker' ) )
		self.timeline.toolbuttonAddKey    .setIcon( getIcon( 'add'    ) )
		self.timeline.toolbuttonRemoveKey .setIcon( getIcon( 'remove' ) )
		self.timeline.toolbuttonCloneKey  .setIcon( getIcon( 'clone'  ) )

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
		playToolLayout.addStretch( )

		trackToolLayout = QtGui.QVBoxLayout(self.containerTrackTool) 
		trackToolLayout.setSpacing( 0 )
		trackToolLayout.setMargin( 0 )
		trackToolLayout.addWidget( self.toolbarTrack )		

		bottomToolHeight = 20
		self.containerTrackTool.setFixedHeight( bottomToolHeight )
		self.toolbarTrack.setFixedHeight( bottomToolHeight )
		
		topToolHeight = self.timeline.getRulerHeight()
		self.containerPlayTool.setFixedHeight( topToolHeight )
		self.toolbarPlay.setFixedHeight( topToolHeight )
		self.toolbarClips.setFixedHeight( topToolHeight )
		self.treeTracks.header().hide()

		self.treeTracks.setObjectName( 'AnimatorTrackTree' )
		self.treeClips.setObjectName( 'AnimatorClipListTree' )
		self.toolbarPlay.setObjectName( 'TimelineToolBarPlay')
		self.toolbarTrack.setObjectName( 'TimelineToolBarTrack')

		#signals
		self.treeTracks.verticalScrollBar().valueChanged.connect( self.onTrackTreeScroll )
		self.timeline.cursorPosChanged.connect( self.onCursorPosChanged )
		self.timeline.trackView.scrollYChanged.connect( self.onTrackViewScrollDragged )
		self.treeTracks.layoutChanged.connect( self.updateTrackLayout )
		self.cursorMovable  = True
		self.updatingScroll = False

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
		self.timeline.markerChanged.connect( self.onMarkerChanged )

	def rebuild( self ):
		self.treeTracks.rebuild()
		self.treeClips.rebuild()
		self.timeline.rebuild()

	def rebuildTimeline( self ):
		self.timeline.rebuild()
		self.treeTracks.rebuild()

	def updateTrackLayout( self ):
		self.timeline.updateTrackLayout()

	def createClip( self ):
		pass

	def addClip( self, clip, focus = False ):
		self.treeClips.addNode( clip )
		if focus:
			self.treeClips.selectNode( clip )
			self.treeClips.editNode( clip )

	def addKey( self, key, focus = False ):
		self.addTrack( key.parent )
		self.timeline.addKey( key )
		if focus:
			#TODO: select key
			pass

	def addTrack( self, track, focus = False ):
		self.treeTracks.addNode( track )
		self.timeline.addTrack( track )
		if focus:
			self.treeTracks.editNode( track )
			self.timeline.setTrackSelection( [track] )

	def addMarker( self, marker, focus = False ):
		self.timeline.addMarker( marker )
		if focus:
			#TODO: select marker
			pass

	def selectTrack( self, trackNode ):
		self.treeTracks.selectNode( trackNode )

	def removeClip( self, clip ):
		self.treeClips.removeNode( clip )

	def removeTrack( self, track ):
		self.treeTracks.removeNode( track )
		self.timeline.removeTrack( track )

	def removeKey( self, key ):
		self.timeline.removeKey( key )

	def setPropertyTarget( self, target ):
		self.propertyEditor.setTarget( target )

	def isTrackVisible( self, trackNode ):
		return self.treeTracks.isNodeVisible( trackNode )

	def getTrackPos( self, trackNode ):
		rect = self.treeTracks.getNodeVisualRect( trackNode )
		scrollY = self.treeTracks.verticalScrollBar().value()
		pos = rect.y() + 3 + scrollY
		return pos

	def onTrackViewScrollDragged( self, y ):
		if self.updatingScroll: return
		self.updatingScroll = True
		self.treeTracks.verticalScrollBar().setValue( -y )
		self.updatingScroll = False

	def setTrackViewScrollRange( self, maxRange ):
		self.timeline.setTrackViewScrollRange( maxRange )

	def onTrackTreeScroll( self, v ):
		self.timeline.setTrackViewScroll( -v )

	def onTrackFolded( self, track, folded ):
		track._folded = folded
		self.timeline.updateTrackLayout()
		self.timeline.clearSelection()

	def onMarkerChanged( self, marker, pos ):
		self.propertyEditor.refreshFor( marker )
		self.owner.onTimelineMarkerChanged( marker, pos )

	def onKeyChanged( self, key, pos, length ):
		self.propertyEditor.refreshFor( key )
		self.owner.onTimelineKeyChanged( key, pos, length )

	def onKeyRemoving( self, key ):
		return self.owner.onKeyRemoving( key )

	def onPropertyChanged( self, obj, fid, value ):
		if isMockInstance( obj, 'AnimatorKey' ):
			if fid == 'pos' or fid == 'length':
				self.timeline.refreshKey( obj )
		elif isMockInstance( obj, 'AnimatorClipMarker' ):
			if fid == 'name' or fid =='pos':
				self.timeline.refreshMarker( obj )
		self.owner.onObjectEdited( obj )

	def setEnabled( self, enabled ):
		super( AnimatorWidget, self ).setEnabled( enabled )
		self.timeline.setEnabled( enabled )

	def startPreview( self ):
		# self.timeline.setCursorDraggable( False )
		pass

	def stopPreview( self ):
		# self.timeline.setCursorDraggable( True )
		pass

	def setCursorMovable( self, movable ):
		self.cursorMovable = movable
		self.timeline.setCursorDraggable( movable )		

	def onCursorPosChanged( self, pos ):
		if self.cursorMovable:
			self.owner.applyTime( pos )

	def setCursorPos( self, pos, focus = False ):
		self.timeline.setCursorPos( pos, focus )

	def getCursorPos( self ):
		return self.timeline.getCursorPos()

	def onTrackSelectioChanged( self ):
		selection = self.treeTracks.getSelection()
		self.timeline.setTrackSelection( selection )
		if selection:
			track = selection[0]
		else:
			track = None
		self.owner.setCurrentTrack( track )
		
	def onClipSelectioChanged( self ):
		selection = self.treeClips.getSelection()
		if selection:
			clip = selection[0]
		else:
			clip = None
		if isMockInstance( clip, 'AnimatorClip' ):
			self.owner.setTargetClip( clip )
		else:
			#TODO
			pass

	def getTrackSelection( self ):
		return self.timeline.getTrackSelection()

	def getClipSelection( self ):
		return self.treeClips.getSelection()

	def getKeySelection( self ):
		return self.timeline.getSelection()

	def getCurrentClipGroup( self ):
		selection = self.treeClips.getSelection()
		if selection:
			node = selection[ 0 ]
			while node:
				if isMockInstance( node, 'AnimatorClipGroup' ):
					return node
				node = node.parentGroup
		return None
