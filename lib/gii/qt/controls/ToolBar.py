import logging

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMenu, QMenuBar, QToolBar, QAction

from gii.core import signals

from Menu import MenuManager

class ToolBarItem(object):
	def __init__( self, name, option ):
		option = option or {}
		self.name     = name.lower()
		self.label    = option.get( 'label', name )	
		self.priority = option.get( 'priority', 0 )
		
		self.onClick = None
		self.signal  = None
		self.itemType = False

		menuLink = option.get( 'menu_link')
		if menuLink:
			m = MenuManager.get().find( menuLink )
			if m and hasattr( m, 'qtaction' ):
				self.qtaction = m.qtaction
			else:
				logging.error( 'not valid menu link:' + self.menuLink )
				self.qtaction = QtGui.QAction( self.label, None )			
		else:
			self.itemType = option.get( 'type', False )
			self.onClick  = option.get( 'on_click', None )
			self.signal   = None
			self.qtaction   = QtGui.QAction( 
				self.label, None,
				checkable = self.itemType == 'check',
				triggered = self.handleEvent
				)

	def setEnabled( self, enabled = True ):
		self.qtaction.setEnabled( enabled )

	def getValue(self):
		if self.itemType in ('check','radio'):
			return self.qtaction.isChecked()
		return True

	def setValue( self, value ):
		if self.itemType in ('check','radio'):
			self.qtaction.setChecked(v and True or False)

	def handleEvent( self ):
		value = self.getValue()
		if self.module:
			self.module.onTool( self )
		if self.signal:
			self.signal( value )
		if self.onClick != None:
			self.onClick( value )

		
class ToolBarNode(object):
	"""docstring for ToolBar"""
	def __init__(self, name, qtToolbar):
		self.name = name
		assert isinstance( qtToolbar, QToolBar )
		self.qtToolbar = qtToolbar
		self.items = {}

	def addTool( self, name, option ):
		item = ToolBarItem( name, option )
		self.items[ name ] = item
		self.qtToolbar.addAction( item.qtaction )
		return item

	def getTool( self, name ):
		return self.items.get( name, None )

	def removeTool( self, name ):
		tool = self.getTool( name )
		if tool:
			self.qtToolbar.removeAction( tool.qtaction )
			del self.items[ name ]

	def enableTool( self, name, enabled = True ):
		tool = self.getTool( name )
		if tool:
			tool.setEnabled( enabled )

	def setEnabled( self, enabled = True ):
		self.qtToolbar.setEnabled( enabled )

	def setValue( self, value ):
		pass



class ToolBarManager(object):
	"""docstring for ToolBarManager"""
	_singleton = None
	@staticmethod
	def get():
		return ToolBarManager._singleton

	def __init__(self):
		assert not ToolBarManager._singleton
		ToolBarManager._singleton = self
		self.toolbars = {}

	def addToolBar( self, name, toolbar, module ):
		tb = ToolBarNode( name, toolbar )
		self.toolbars[ name ] = tb
		tb.module = module
		return tb

	def find( self, path ):
		blobs = path.split('/')
		l = len(blobs)
		if l< 1 or l > 2: 
			logging.error( 'invalid toolbar path' + path )
			return None

		toolbar = self.toolbars.get( blobs[0] )
		if l == 2 :
			return toolbar and toolbar.getTool( blobs[1] ) or None
		return toolbar 

	def addTool( self, path, option = {}, module = None ):
		blobs = path.split('/')
		if len(blobs) != 2:
			logging.error( 'invalid toolbar item path' + path )
			return None

		toolbar = self.find( blobs[0] )
		if toolbar:
			tool = toolbar.addTool( blobs[1], option )
			tool.module = module or toolbar.module
			return tool
		logging.error( 'toolbar not found:' + blobs[0] )
		return None

	def enableTool( self, path, enabled = True ):
		tool = self.find( path )
		if tool:
			tool.setEnabled( enabled )
		else:
			logging.error( 'toolbar/tool not found:' + path )


ToolBarManager()