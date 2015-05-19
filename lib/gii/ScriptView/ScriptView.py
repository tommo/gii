import subprocess
import os.path
import shutil
import time
import json
##----------------------------------------------------------------##
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
##----------------------------------------------------------------##

from gii.core               import *
from gii.qt.controls.Window import MainWindow
from gii.DebugView          import DebugViewModule
from gii.qt.controls.CodeEditor import CodeEditor

##----------------------------------------------------------------##
from DebuggerHandler import DebuggerHandler
from ListStackView   import ListStackView
from TreeScopeView   import TreeScopeView
##----------------------------------------------------------------##

class ScriptView( DebugViewModule ):
	name = 'script_view'
	def onLoad(self):	
		window = self.getMainWindow()
		self.menu = self.addMenuBar( 'script', window.menuBar() )
		# self.menu.addChild('&File').addChild(['Open','E&xit'])
		editMenu=self.menu.addChild( '&Goto' ).addChild([
				{'name':'goto_line', 'label':'Goto Line', 'shortcut':'Meta+G'},
				{'name':'goto_file', 'label':'Goto File', 'shortcut':'Ctrl+P'}
			])

		self.menu.addChild( '&Debug' ).addChild([
				{ 'name':'step_over', 'label':'Step Over', 'shortcut':'F6' },
				{ 'name':'step_in',   'label':'Step In',   'shortcut':'F7' },
				{ 'name':'step_out',  'label':'Step Out',  'shortcut':'F8' },
				{ 'name':'continue',  'label':'Continue',  'shortcut':'F5' },
				{ 'name':'terminate', 'label':'Terminate', 'shortcut':'Meta+F5' }
			])

		self.panelDebug=PanelDebug()
		self.panelDebug.module=self

		self.containerDebugger = self.requestDockWindow( 'Debugger',
			title     = 'Debugger',
			size      = (120,120),
			minSize   = (120,120),
			dock      = 'right'
			)

		self.containerDebugger.addWidget( self.panelDebug )

		#init function component
		self.debuggerHandler = DebuggerHandler(self)
		signals.connect('app.command', self.onAppCommand)
		# signals.connect('app.remote', self.onAppRemote)

		#script page management
		self.scriptPages = {}
		self.defaultPageSetting=json.load(
				file( app.getPath('data/script_settings.json'), 'r' )
			)

		self.toggleDebug(False)

	def onStart( self ):
		self.locateFile( '/Volumes/prj/moai/yaka/game/main.lua', 2, 'serious' )

	def onUnload(self):
		if self.debuggerHandler.busy:
				self.debuggerHandler.doStop()	#stop debug

	def locateFile( self, filename, lineNumber=1, highLight = False ):
		self.setFocus()
		page = self.getPageByFile( filename, True )
		if not page:
			return False
		page.setFocus()
		page.locateLine( lineNumber, highLight )

	def toggleDebug(self, toggle):
		if toggle:
			self.getMainWindow().setWindowModality(Qt.ApplicationModal)
		else: 
			self.getMainWindow().setWindowModality(Qt.NonModal)
		# self.panelDebug.toggleDebug(toggle)
		self.enableMenu('script/debug/step_in',toggle)
		self.enableMenu('script/debug/step_over',toggle)
		self.enableMenu('script/debug/step_out',toggle)
		self.enableMenu('script/debug/terminate',toggle)
		self.enableMenu('script/debug/continue',toggle)
		if not toggle:
			for path in self.scriptPages:
				p = self.scriptPages[path]
				p.clearHilight( 'normal' )

	def onMenu(self, node):
		name=node.name
		if name=='step_in':
			self.debuggerHandler.doStepIn()
		elif name=='step_over':
			self.debuggerHandler.doStepOver()
		elif name=='step_out':
			self.debuggerHandler.doStepOut()
		elif name=='terminate':
			self.debuggerHandler.doStop()
		elif name=='continue':
			self.debuggerHandler.doContinue()

	def onAppCommand(self, cmd, src=None):
		if cmd=='exec':
			if self.debuggerHandler.busy:
				self.debuggerHandler.doStop()	#stop debug

	def onAppRemote( self, data, output ):
		cmd = data[0]
		if cmd == 'debug.step_in':
			pass
			#TODO

	def getPageByFile( self, path, createIfNotFound=True ):
		path = path.encode('utf-8')
		if not os.path.exists(path): return None
		page = self.scriptPages.get(path, False)
		if not page:
			if not createIfNotFound: return None
			#create
			container = self.requestDocumentWindow( 
				title = path
			)
			page = ScriptPage( path, container )
			container.addWidget( page )
			self.scriptPages[ path ]=page
		# else:
		# 	page.checkFileModified()
		return page

##----------------------------------------------------------------##
class ScriptPage( CodeEditor ):
	def __init__( self, path, container ):
		CodeEditor.__init__( self, container )
		self.path = path
		self.mimeType = 'text/x-lua'
		self.container = container
		self.fileTime = 0
		self.setReadOnly(True)
		self.refreshCode()

	def refreshCode(self):
		self.refreshing = True
		code = 'Not Load'
		with file(self.path,'r') as f:
			code = f.read()
			self.fileTime = os.path.getmtime(self.path)
		try:
			code = code.decode('utf-8')
		except Exception, e:
			pass
		readOnly = self.isReadOnly()
		self.setReadOnly(False)
		self.setPlainText( code, self.mimeType )
		self.setReadOnly(readOnly)
		# self.SetSavePoint()
		# self.EmptyUndoBuffer()
		self.refreshing=False
		#self.checkModifyState()

	def checkFileModified(self):
		newtime=os.path.getmtime(self.path)
		if newtime>self.fileTime:
			self.refreshCode()

	def locateLine(self, linenumber, hilight=False):
		#TODO
		pass

	def setFocus( self ):
		self.container.show()
		self.container.raise_()
		self.container.activateWindow()
		self.container.setFocus()

##----------------------------------------------------------------##
class ScriptViewWindow( MainWindow ):
	"""docstring for ScriptViewWindow"""
	def __init__(self, arg):
		super(ScriptViewWindow, self).__init__(arg)		

	def closeEvent(self,event):
		if self.module.alive:
			self.hide()
			event.ignore()


##----------------------------------------------------------------##
class PanelDebug(QtGui.QWidget):
	def __init__(self,*args):
		super(PanelDebug,self).__init__(*args)
		
		layout = QtGui.QVBoxLayout(self)
		layout.setSpacing(0)
		layout.setMargin(0)

		self.toolbar = QtGui.QToolBar(self)
		self.toolbar.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
		layout.addWidget(self.toolbar)

		splitter=QtGui.QSplitter(QtCore.Qt.Horizontal)
		splitter.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
		layout.addWidget(splitter)
		
		font=QtGui.QFont()
		font.setFamily('Consolas')
		font.setPointSize(12)

		listStack=ListStackView()
		treeScope=TreeScopeView()

		listStack.setFont(font)
		treeScope.setFont(font)

		self.listStack=listStack
		self.treeScope=treeScope

		listStack.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
		treeScope.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)

		splitter.addWidget(listStack)
		splitter.addWidget(treeScope)

		# self.toolbar.addAction('hello').triggered.connect(self.onStepIn)

	def toggleDebug(self, toggle):
		pass
		# self.toolbarStack.EnableTool(forms.TOOLID_CONTINUE,toggle)
		# self.toolbarStack.EnableTool(forms.TOOLID_STEPIN, toggle)
		# self.toolbarStack.EnableTool(forms.TOOLID_STEPOUT, toggle)
		# self.toolbarStack.EnableTool(forms.TOOLID_STEPOVER, toggle)
		# self.toolbarStack.EnableTool(forms.TOOLID_STOP, toggle)
		# self.toolbarStack.Enable(toggle)

	def loadVarData(self,data,parentName):
		self.treeScope.loadVarData(data, parentName)

	def loadStackData(self, data ):
		self.listStack.loadStackData(data or [])		

	def onStepIn( self, event ):
		self.module.debuggerHandler.doStepIn()
	
	def onStepOver( self, event ):
		self.module.debuggerHandler.doStepOver()
	
	def onStepOut( self, event ):
		self.module.debuggerHandler.doStepOut()
	
	def onStop( self, event ):
		self.module.debuggerHandler.doStop()
	
	def onContinue( self, event ):
		self.module.debuggerHandler.doContinue()



