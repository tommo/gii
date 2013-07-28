import random
from PyQt4            import QtCore, QtGui, uic
from PyQt4.QtCore     import Qt

from gii.core         import *
from gii.qt           import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.PropertyGrid      import PropertyGrid
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget


class AssetTreeView( GenericTreeWidget ):
	def __init__( self, *args, **kwargs ):
		super( AssetTreeView, self ).__init__( *args, **kwargs )

	def saveTreeStates( self ):
		for node, item in self.nodeDict.items():
			node.setProperty( 'expanded', item.isExpanded() )

	def loadTreeStates( self ):
		for node, item in self.nodeDict.items():
			if node.getProperty( 'expanded', False ):
				item.setExpanded( True )

	def getRootNode( self ):
		return app.getAssetLibrary().getRootNode()

	def getNodeParent( self, node ): # reimplemnt for target node
		return node.getParent()

	def getNodeChildren( self, node ):
		return node.getChildren()

	def createItem( self, node ):
		return AssetTreeItem()

	def updateItem( self, item, node, **option ):
		if option.get('basic', True):
			item.setText( 0, node.getName() )
			item.setText( 1, '' )
			item.setText( 2, node.getType() )
			assetType=node.getType()

			iconName = app.getAssetLibrary().getAssetIcon( assetType )
			item.setIcon(0, getIcon(iconName,'normal'))

		if option.get('deploy', True):
			dstate=node.getDeployState()
			if   dstate is None:
				item.setIcon(1, getIcon(None))
			elif dstate == False:
				item.setIcon(1, getIcon('deploy_no'))
			elif dstate == True:
				item.setIcon(1, getIcon('deploy_yes'))
			else: #'dep' or 'parent'
				item.setIcon(1, getIcon('deploy_dep'))

	def getHeaderInfo( self ):
		return [('Name',200), ('Deploy',30), ('Type',60)]

	def onClicked(self, item, col):
		pass

	def onDClicked(self, item, col):
		node=item.node
		if node:
			node.edit()

	def onItemSelectionChanged(self):
		items = self.selectedItems()
		if items:
			selections = [item.node for item in items]
			app.getSelectionManager().changeSelection(selections)
		else:
			app.getSelectionManager().changeSelection(None)

	def doUpdateItem(self, node, updateLog=None, **option):
		super( AssetTreeView, self ).doUpdateItem( node, updateLog, **option )

		if option.get('updateDependency',False):
			for dep in node.rDep:
				self.doUpdateItem(dep, updateLog, **option)
	
##----------------------------------------------------------------##
#TODO: allow sort by other column
class AssetTreeItem(QtGui.QTreeWidgetItem):
	def __lt__(self, other):
		node0 = self.node
		node1 = hasattr(other, 'node') and other.node or None
		if not node1:
			return True
		t0 = node0.getType()
		t1 = node1.getType()
		if t1!=t0:
			if t0 == 'folder': return True
			if t1 == 'folder': return False
		return node0.getName().lower()<node1.getName().lower()

##----------------------------------------------------------------##