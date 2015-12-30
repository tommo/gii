# -*- coding: utf-8 -*-
import sys
import math

from gii.qt.controls.GenericTreeWidget     import GenericTreeWidget, GenericTreeFilter
from gii.qt.controls.GenericListWidget     import GenericListWidget
from gii.qt.controls.PropertyEditor        import PropertyEditor
from gii.qt.IconCache                      import getIcon
from gii.qt.helpers                        import addWidgetWithLayout, QColorF, unpackQColor

from gii.qt.controls.ToolBar               import wrapToolBar
from gii.SearchView import requestSearchView

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QColor, QTransform

##----------------------------------------------------------------##
from mock import _MOCK, _MOCK_EDIT, isMockInstance

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

SQScriptEditorForm,BaseClass = uic.loadUiType( _getModulePath('SQScriptEditorWidget.ui') )



##----------------------------------------------------------------##
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import \
	QStyle, QStyleOptionViewItemV4, QApplication, QTextDocument, QAbstractTextDocumentLayout, QPalette, \
	QColor

##----------------------------------------------------------------##
_htmlRole = Qt.UserRole + 1

class HTMLTreeItem( QtGui.QTreeWidgetItem ):
	def __init__( self, *args ):
		super( HTMLTreeItem, self ).__init__( *args )
		self.docsObjects = {}
		self.commonDefaultStyleSheet = None

	def affirmDocObject( self, column ):
		doc = self.docsObjects.get( column, 0 )
		if not doc:
			doc = QtGui.QTextDocument( None )
			self.docsObjects[ column ] = doc
			self.setData( column, _htmlRole, doc )	
			if self.commonDefaultStyleSheet:
				doc.setDefaultStyleSheet( self.commonDefaultStyleSheet )
		return doc

	def setHtml( self, column, html ):
		doc = self.affirmDocObject( column )
		doc.setHtml( html )
		self.setText( column, doc.toPlainText() )

	def setDefaultStyleSheet( self, column, sheet ):
		if column < 0:
			self.commonDefaultStyleSheet = sheet
		else:
			doc = self.affirmDocObject( column )
			doc.setDefaultStyleSheet( sheet )

##----------------------------------------------------------------##
class HTMLItemDelegate(QtGui.QStyledItemDelegate):
	def paint(self, painter, option, index):
		doc = index.data( _htmlRole )
		if not doc:
			return super( HTMLItemDelegate, self ).paint( painter, option, index )

		self.initStyleOption(option,index)

		style = option.widget.style() or QApplication.style()

		#draw icon
		option.text = ""
		style.drawControl( QStyle.CE_ItemViewItem, option, painter,option.widget)

		ctx = QAbstractTextDocumentLayout.PaintContext()
		textRect = style.subElementRect( QStyle.SE_ItemViewItemText, option )

		# painter.setBrush( option.backgroundBrush )
		# painter.setPen( Qt.NoPen )
		# painter.drawRect( textRect )

		# Highlighting text if item is selected
		# if option.state & QStyle.State_Selected :
		# 	painter.setBrush( QColor( 0,180,0,30 ) )
		# 	painter.setPen( Qt.NoPen )
		# 	painter.drawRect( textRect )

		# elif option.state & QStyle.State_MouseOver :
		# 	painter.setBrush( QColor( 0,255,0,10 ) )
		# 	painter.setPen( Qt.NoPen )
		# 	painter.drawRect( textRect )

		# painter.setPen( QColor( 0,0,0,10 ) )
		# painter.drawLine( textRect.bottomLeft(), textRect.bottomRight() )

		painter.save()
		painter.translate(textRect.topLeft())
		painter.setClipRect(textRect.translated(-textRect.topLeft()))
		doc.documentLayout().draw(painter, ctx)

		painter.restore()

	def sizeHint(self, option, index):
		self.initStyleOption( option, index )
		doc = index.data( _htmlRole )
		if doc:
			doc.setTextWidth( option.rect.width() )
		return QtCore.QSize( doc.idealWidth(), doc.size().height() )


##----------------------------------------------------------------##
class RoutineListWidget( GenericListWidget ):
	def getDefaultOptions( self ):
		return {
			'editable' : True
		}

	def getNodes( self ):
		return self.owner.getRoutines()

	def updateItemContent( self, item, node, **option ):
		name = node.getName( node )
		item.setText( name )
		item.setIcon( getIcon( 'sq_routine' ) )

	def onItemSelectionChanged( self ):
		self.owner.onRoutineSelectionChanged()

	def onItemChanged( self, item ):
		self.owner.renameRoutine( item.node, item.text() )


##----------------------------------------------------------------##
class RoutineNodeTreeFilter( GenericTreeFilter ):
	pass

##----------------------------------------------------------------##
# class RoutineNodeTreeItemDelegate( QtGui.QStyledItemDelegate ):
class RoutineNodeTreeItemDelegate( HTMLItemDelegate ):
	pass

##----------------------------------------------------------------##
class RoutineNodeTreeWidget( GenericTreeWidget ):
	def __init__( self, *args, **option ):
		option['sorting'] = False
		option['drag_mode'] = 'internal'
		super( RoutineNodeTreeWidget, self ).__init__( *args, **option )
		self.setObjectName( 'RoutineNodeTreeWidget' )
		self.setHeaderHidden( True )
		self.setIndentation( 18 )
		
		self.setStyleSheet( '''
			QWidget{ background:#fffff3; }
			:branch{ border-image:none; }
			:item{ border-bottom: 1px solid #eee }
			:item:hover{ background:#f6ffc8 }
			:item:selected{ background:#fff095 }
		''' )

		self.itemStyleSheet = '''
		body{
			font-size:13px;
			color: #bb9;
		}
		cmd{
			font-size:10px;
			font-weight:bold;
			color: #747474;
		}
		comment{
			color: #b2b09d;
		}
		data{
			color: #555;
		}
		number{
			font-size:12px;
			color: #c89948;
		}
		string{
			color: #2f3cff;
		}
		signal{
			color: #f933ff;
		}
		flag{
			font-size:10px;
			font-weight:bold;
			color: #3c9100;
		}
		label{
			font-size:12px;
			color: #0080f8;
			font-weight:bold;
		}

		group{
			font-size:12px;
			color:#444444;
		}

		end{
			font-size:12px;
			color: #c50000;
			font-weight:bold;
		}

		'''

	def getHeaderInfo( self ):
		return [ ('Event',-1) ]
	
	def getRootNode( self ):
		routine = self.owner.getTargetRoutine()
		return routine and routine.getRootNode( routine )

	def getNodeParent( self, node ):
		return node.getParent( node )

	def getNodeChildren( self, node ):
		return [ child for child in node.getChildren( node ).values() ]

	def updateItemContent( self, item, node, **option ):
		if item == self.invisibleRootItem(): return
		iconName = node.getIcon( node )
		richText = node.getRichText( node )
		#mark
		# item.setText( 0, node.getMarkText() )
		item.setIcon( 0, getIcon( iconName or 'sq_node_normal', 'sq_node_normal' ) )
		#event
		item.setHtml( 0, '<body>%s</body>' % richText )
		# item.setText( 0, node.getTag() + node.getDesc() )
	
	def getDefaultItemDelegate( self ):
		return RoutineNodeTreeItemDelegate( self )

	def createItem( self, node ):
		item = HTMLTreeItem()
		item.setDefaultStyleSheet( -1, self.itemStyleSheet )
		return item

	def onItemSelectionChanged( self ):
		self.owner.onNodeSelectionChanged()

	def onDeletePressed( self ):
		self.owner.onNodeTreeDeletePressed()


##----------------------------------------------------------------##
class SQScriptEditorWidget( QtGui.QWidget ):
	def __init__( self, *args, **kwargs ):
		super( SQScriptEditorWidget, self ).__init__( *args, **kwargs )
		self.owner = None
		self.targetRoutine = None
		self.targetNode    = None
		self.initData()		
		self.initUI()

	def initData( self ):
		self.routineEditors = {}

	def initUI( self ):
		self.setObjectName( 'SQScriptEditorWidget' )
		self.ui = SQScriptEditorForm()
		self.ui.setupUi( self )
		self.listRoutine = addWidgetWithLayout( RoutineListWidget( self.ui.containerRoutine ) )
		self.listRoutine.owner = self

		self.toolbarMain = wrapToolBar(
			'main',
			addWidgetWithLayout( QtGui.QToolBar( self.ui.containerToolbar ) ),
			owner = self
		)

		self.toolbarMain.addTools([
			dict( name = 'save',   label = 'Save',   icon = 'save' ),
			dict( name = 'locate', label = 'Locate', icon = 'search-2' ),
			'----',
			dict( name = 'add_routine', label = 'Add', icon = 'add' ),
			dict( name = 'del_routine', label = 'Del', icon = 'remove' ),
		])
		
		self.treeRoutineNode = addWidgetWithLayout( RoutineNodeTreeWidget( self.ui.containerContent ) )
		self.treeRoutineNode.owner = self

		self.scrollProperty = scroll = addWidgetWithLayout( QtGui.QScrollArea( self.ui.containerProperty ) )
		scroll.verticalScrollBar().setStyleSheet('width:4px')
		scroll.setWidgetResizable( True )
		self.propertyEditor = PropertyEditor( scroll )
		scroll.setWidget( self.propertyEditor )

		self.propertyEditor.propertyChanged.connect( self.onPropertyChanged )

		#setup shortcuts
		self.addShortcut( self.treeRoutineNode, 'Tab', self.promptAddNode )
		self.addShortcut( self, 'Ctrl+1', self.focusContentTree )


	def addShortcut( self, contextWindow, keySeq, target, *args, **option ):
		contextWindow = contextWindow or self
		shortcutContext = Qt.WidgetWithChildrenShortcut

		action = QtGui.QAction( contextWindow )
		action.setShortcut( QtGui.QKeySequence( keySeq ) )
		action.setShortcutContext( shortcutContext )
		contextWindow.addAction( action )

		if isinstance( target, str ): #command
			def onAction():
				self.doCommand( target, **option )
			action.triggered.connect( onAction )
		else: #callable
			def onAction():
				target( *args, **option )
			action.triggered.connect( onAction )

		return action

	def setTargetRoutine( self, routine ):
		self.targetRoutine = routine
		self.propertyEditor.setTarget( self.targetRoutine )
		self.treeRoutineNode.rebuild()

	def getTargetRoutine( self ):
		return self.targetRoutine

	def setTargetNode( self, node ):
		self.targetNode = node
		self.propertyEditor.setTarget( node )

	def getTargetNode( self ):
		return self.targetNode

	def rebuild( self ):
		self.listRoutine.rebuild()
		self.treeRoutineNode.rebuild()
		script = self.getTargetScript()
		firstRoutine = script.getRoutines( script )[ 1 ] #lua
		if firstRoutine:
			self.listRoutine.selectNode( firstRoutine )

	def getRoutineEditor( self, routine ):
		return self.routineEditors.get( routine, None )

	def getTargetScript( self ):
		return self.owner.getTargetScript()

	def getRoutines( self ):
		targetScript = self.getTargetScript()
		if not targetScript:
			return []
		else:
			routines = targetScript.routines
			return [ routine for routine in routines.values() ]

	def getRoutineName( self, routine ):
		return routine.getName() #TODO

	def addRoutine( self ):
		script = self.getTargetScript()
		newRoutine = script.addRoutine( script ) #lua
		self.listRoutine.addNode( newRoutine )
		self.listRoutine.editNode( newRoutine )
		self.listRoutine.selectNode( newRoutine )

	def delRoutine( self ):
		script = self.getTargetScript()
		for routine in self.listRoutine.getSelection():
			script.removeRoutine( script, routine ) #lua
			self.listRoutine.removeNode( routine )

	def renameRoutine( self, routine, name ):
		routine.setName( routine, name )

	def promptAddNode( self ):
		requestSearchView( 
			info         = 'adding SQScript node...',
			context      = 'sq_script_editor',
			type         = None,
			multiple_selection = False,
			on_selection = self.createNode,
			on_search    = self.listNodeTypes
		)

	def cloneNode( self ):
		pass

	def createNode( self, nodeTypeName ):
		contextNode = self.treeRoutineNode.getFirstSelection()
		node = _MOCK_EDIT.createSQNode( nodeTypeName, contextNode, self.targetRoutine )
		if node:
			self.treeRoutineNode.rebuild()
			self.treeRoutineNode.selectNode( node )

	def listNodeTypes( self, typeId, context, option ):
		res = _MOCK_EDIT.requestAvailSQNodeTypes( self.treeRoutineNode.getFirstSelection() )
		entries = []
		for n in res.values():
			entry = ( n, n, 'SQ Node', 'sq_script/'+n )
			entries.append( entry )
		return entries


	def onRoutineSelectionChanged( self ):
		for routine in self.listRoutine.getSelection():
			self.setTargetRoutine( routine )
			break
			# self.listRoutine.removeNode( routine)		

	def onNodeSelectionChanged( self ):
		for node in self.treeRoutineNode.getSelection():
			self.setTargetNode( node )
			break
			# self.listRoutine.removeNode( routine)		

	def onNodeTreeDeletePressed( self ):
		selection = self.treeRoutineNode.getSelection()
		for node in selection:
			parent = node.getParent( node )
			if parent:
				parent.removeChild( parent, node ) #lua
				self.treeRoutineNode.removeNode( node )

	def onPropertyChanged( self, obj, fid, value ):
		if isMockInstance( obj, 'SQNode' ):
			self.treeRoutineNode.refreshNodeContent( obj )
		elif isMockInstance( obj, 'SQRoutine' ):
			pass

	def focusContentTree( self ):
		self.treeRoutineNode.setFocus()
	
	def onTool( self, tool ):
		name = tool.getName()
		if name == 'add_routine':
			self.addRoutine()

		elif name == 'del_routine':
			self.delRoutine()

		elif name == 'save':
			self.owner.saveAsset()

		elif name == 'locate':
			self.owner.locateAsset()