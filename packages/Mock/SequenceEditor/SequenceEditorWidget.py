# -*- coding: utf-8 -*-
import sys
import math

from gii.qt.controls.GenericTreeWidget     import GenericTreeWidget, GenericTreeFilter
from gii.qt.controls.GenericListWidget     import GenericListWidget
from gii.qt.controls.PropertyEditor        import PropertyEditor
from gii.qt.IconCache                      import getIcon
from gii.qt.helpers                        import addWidgetWithLayout, QColorF, unpackQColor

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QColor, QTransform

##----------------------------------------------------------------##
# from mock import _MOCK, isMockInstance

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

SequenceEditorForm,BaseClass = uic.loadUiType( _getModulePath('SequenceEditorWidget.ui') )



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
	def getNodes( self ):
		return self.parent().getRoutines()

	def updateItemContent( self, item, node, **option ):
		item.setText( self.parent().getRoutineName( node ) )


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
		super( RoutineNodeTreeWidget, self ).__init__( *args, **option )
		self.setObjectName( 'RoutineNodeTreeWidget' )
		self.setHeaderHidden( True )
		self.setIndentation( 12 )
		
		self.setStyleSheet( '''
			QWidget{ background:#ffffef; }
			:branch{ border-image:none; }
			:item{ border-bottom: 1px solid #eec }
			:item:hover{ background:#f6ffc8 }
			:item:selected{ background:#fff095 }
		''' )

		self.itemStyleSheet = '''
		body{
			font-size:12px;
		}
		command{
			color: #900;
		}
		data{
			color: #555;
		}
		value{
			color: #090;
		}
		'''

	def getHeaderInfo( self ):
		return [ ('Event',-1) ]
	
	def getRootNode( self ):
		return self.parent().getRootNode()

	def getNodeParent( self, node ):
		return node.getParent()

	def getNodeChildren( self, node ):
		return node.getChildren()

	def updateItemContent( self, item, node, **option ):
		if item == self.invisibleRootItem(): return
		#mark
		# item.setText( 0, node.getMarkText() )
		item.setIcon( 0, getIcon( 'sq_node_normal' ) )
		#event
		item.setHtml( 0, '<body><command>%s</command> <data>%s</data></body>' % ( node.getTag(), node.getDesc() ) )
		# item.setText( 0, node.getTag() + node.getDesc() )
	
	def getDefaultItemDelegate( self ):
		return RoutineNodeTreeItemDelegate( self )

	def createItem( self, node ):
		item = HTMLTreeItem()
		item.setDefaultStyleSheet( -1, self.itemStyleSheet )
		return item



##----------------------------------------------------------------##
class RoutineEditor( QtGui.QWidget ):
	def __init__( self, *args ):
		super( RoutineEditor, self ).__init__( *args )
		layout = QtGui.QVBoxLayout( self )
		layout.setSpacing( 0 )
		layout.setMargin( 0 )
		
		self.tree = RoutineNodeTreeWidget( self )
		self.targetRoutine = None

		layout.addWidget( self.tree )

	def setTargetRoutine( self, routine ):
		self.targetRoutine = routine
		self.tree.rebuild()

	def getTargetRoutine( self ):
		return self.targetRoutine

	def getRootNode( self ):
		return self.targetRoutine.getRootNode()


##----------------------------------------------------------------##
class SequenceEditorWidget( QtGui.QWidget ):
	def __init__( self, *args, **kwargs ):
		super( SequenceEditorWidget, self ).__init__( *args, **kwargs )
		self.initData()		
		self.initUI()

	def initData( self ):
		self.routineEditors = {}

	def initUI( self ):
		self.setObjectName( 'SequenceEditorWidget' )
		self.ui = SequenceEditorForm()
		self.ui.setupUi( self )
		self.listRoutine = addWidgetWithLayout( RoutineListWidget( self.ui.containerRoutine ) )
		self.toolbar = addWidgetWithLayout( QtGui.QToolBar( self.ui.containerToolbar ) )

	def addRoutine( self, routine ):
		editor = RoutineEditor( self )
		self.routineEditors[ routine ] = editor
		editor.setTargetRoutine( routine )
		self.ui.tabRoutine.addTab( editor, 'Routine #1' )

	def getRoutineEditor( self, routine ):
		return self.routineEditors.get( routine, None )

	def getRoutines( self ):
		return [] #TODO

	def getRoutineName( self, routine ):
		return routine.getName() #TODO

##----------------------------------------------------------------##
if __name__ == '__main__':
	# class TestFrame( QtGui.QFrame ):
	# 	def __init__(self, *args):
	# 		super(TestFrame, self).__init__( *args )
	# 		self.
	import gii.core
	import sys
	app = QtGui.QApplication( sys.argv )
	gii.core.app.registerDataPath( '/Users/tommo/prj/gii/data' )
	
	QtCore.QDir.setSearchPaths( 'theme', [ '/Users/tommo/prj/gii/data/theme' ] )
	QtGui.QFontDatabase.addApplicationFont( '/Users/tommo/prj/gii/data/default_font.ttf' )

	styleSheetName = 'gii.qss'
	app.setStyleSheet(
			open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
		)

	widget = SequenceEditorWidget()
	widget.show()
	widget.raise_()

	class TestRoutineNode(object):
		def __init__( self, parent ):
			self.parent = parent
			self.children = []
			self.mark = None
			self.index = 0

		def getParent( self ):
			return self.parent

		def getChildren( self ):
			return self.children

		def getTag( self ):
			testTag = [
				'SAY',
				'ANIM',
				'SPAWN'
			]
			return testTag[ self.index % len( testTag ) ]

		def getDesc( self ):
			testDesc = [
				u'这是一条测试用的消息',
				u'胡子可以变形的大叔，除了标志性的<value>胡子</value>，他还穿着一身紫色披风',
				u'在吧台后配酒手法娴熟',
				u'为兄弟会提供强力火力支援。本身是优秀的狙击手，但负伤后转为武器研究。',
				u'Good job!',
				u'コレハナントモイエマセンネー！',
			]
			testDesc1 = [
				"The <b>Dock Widgets</b> example demonstrates how to use ",
				"Qt's dock widgets. You can enter your own text, click a ",
				"customer to add a customer name and address, and click ",
				"standard paragraphs to add them.",
				"THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS",
				"* Neither the name of Nokia Corporation and its Subsidiary(-ies) nor"
			]

			return testDesc[ self.index % 6 ]

		def getMark( self ):
			return self.mark

		def getIndex( self ):
			return self.index

		def getMarkText( self ):
			if self.mark: return '<%s>' % self.mark
			return '%d' % self.index

		def addChild( self, node ):
			self.children.append( node )
			node.parent = self
			node.index = len( self.children )
			return node

	class TestRoutine(object):
		def __init__( self ):
			self.rootNode = TestRoutineNode( None )

		def getRootNode( self ):
			return self.rootNode



	testRoutine = TestRoutine()
	root = testRoutine.rootNode
	for k in range( 20 ):
		node = root.addChild(
			TestRoutineNode( None )
		)
		if k == 5:
			for j in range( 5 ):
				node.addChild(
					TestRoutineNode( None )
				)

	widget.addRoutine( testRoutine )

	app.exec_()

