from gii.core import signals

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt

from ToolWindowManager import ToolWindowManager

def getWindowScreenId(window):
	desktop=QtGui.QApplication.desktop()
	return desktop.screenNumber(window)
	
def moveWindowToCenter(window):
	desktop=QtGui.QApplication.desktop()
	geom=desktop.availableGeometry(window)
	x=(geom.width()-window.width())/2 +geom.x()
	y=(geom.height()-window.height())/2+geom.y()
	window.move(x,y)

def ensureWindowVisible( widget ):
	screenRect = QtGui.QApplication.desktop().availableGeometry(widget);
	widgetRect = widget.frameGeometry()
	pos = widget.pos()
	
	if widgetRect.left() < screenRect.left() :
		pos.setX( pos.x() + screenRect.left() - widgetRect.left() )
	elif widgetRect.right() > screenRect.right():
		pos.setX( pos.x() + screenRect.right() - widgetRect.right() )

	if widgetRect.top() < screenRect.top():
		pos.setY( pos.y() + screenRect.top() - widgetRect.top() )			
	elif widgetRect.bottom() > screenRect.bottom():
		pos.setY( pos.y() + screenRect.bottom() - widgetRect.bottom() )

	widget.move( pos )

##----------------------------------------------------------------##
class MainWindow(QtGui.QMainWindow):
	"""docstring for MainWindow"""
	def __init__(self, parent):
		super(MainWindow, self).__init__(parent)		
		# self.setDocumentMode(True)
		self.setUnifiedTitleAndToolBarOnMac( False )
		self.setDockOptions(
			QtGui.QMainWindow.AllowNestedDocks | QtGui.QMainWindow.AllowTabbedDocks  )
		# self.setTabPosition( Qt.AllDockWidgetAreas, QtGui.QTabWidget.North)
		font=QtGui.QFont()
		font.setPointSize(11)
		self.setFont(font)
		self.setIconSize( QtCore.QSize( 16, 16 ) )
		self.setFocusPolicy( Qt.WheelFocus )
		
		self.centerTabWidget = QtGui.QTabWidget( self )
		self.setCentralWidget( self.centerTabWidget )
		
		self.centerTabWidget.currentChanged.connect( self.onDocumentTabChanged )

		# self.centerTabWidget.setDocumentMode(True)
		self.centerTabWidget.setMovable(True)
		self.centerTabWidget.setTabsClosable(True)
		self.centerTabWidget.tabCloseRequested.connect( self.onTabCloseRequested )

		# self.toolWindowMgr = ToolWindowManager( self )
		# self.setCentralWidget( self.toolWindowMgr )

	def moveToCenter(self):
		moveWindowToCenter(self)

	def ensureVisible(self):
		ensureWindowVisible(self)

	def startTimer(self, fps, trigger):
		assert(hasattr(trigger,'__call__'))
		interval = 1000/fps
		timer = QtCore.QTimer(self)
		timer.timeout.connect(trigger)
		timer.start(interval)
		return timer

	def requestSubWindow(self, id, **windowOption ):
		title = windowOption.get('title',id)
		
		window = SubWindow(self)
		window.setWindowTitle(title)

		window.windowMode = 'sub'
		window.titleBase = title


		minSize=windowOption.get('minSize',None)
		if minSize:
			window.setMinimumSize(*minSize)
		# else:
		# 	window.setMinimumSize(20,20)

		maxSize=windowOption.get('minSize',None)
		if maxSize:
			window.setMaximumSize( *maxSize )

		size=windowOption.get('size',None)
		if size:
			window.resize(*size)
		return window

	def requestDocumentWindow(self, id, **windowOption ):
		title  = windowOption.get('title',id)
		
		window = DocumentWindow( self.centerTabWidget )
		# window = DocumentWindow( self.toolWindowMgr )
		# self.toolWindowMgr.addToolWindow( window, ToolWindowManager.EmptySpace )
		window.parentWindow = self
		window.setWindowTitle( title )
		# self.centerTabWidget.addTab( window, title )

		window.windowMode = 'tab'
		window.titleBase = title


		minSize = windowOption.get('minSize',None)
		if minSize:
			window.setMinimumSize(*minSize)
		else:
			window.setMinimumSize(20,20)

		size = windowOption.get('size',None)
		if size:
			window.resize(*size)
		return window

	def requestDockWindow(self, id, **dockOptions ):
		title=dockOptions.get( 'title', id )

		dockArea=dockOptions.get('dock','left')
		
		if dockArea=='left':
			dockArea=Qt.LeftDockWidgetArea
		elif dockArea=='right':
			dockArea=Qt.RightDockWidgetArea
		elif dockArea=='top':
			dockArea=Qt.TopDockWidgetArea
		elif dockArea=='bottom':
			dockArea=Qt.BottomDockWidgetArea
		elif dockArea=='main':
			dockArea='center'
		elif dockArea=='float':
			dockArea = False
		elif dockArea:
			raise Exception('unsupported dock area:%s'%dockArea)
		
		window=DockWindow(self)
		if title:
			window.setWindowTitle(title)
		window.setObjectName('_dock_'+id)
		
		window.windowMode = 'dock'
		window.titleBase = title

		if dockOptions.get( 'allowDock', True ):
			window.setAllowedAreas( Qt.AllDockWidgetAreas )
		else:
			window.setAllowedAreas( Qt.NoDockWidgetArea )
			dockArea = None
			
		if dockArea and dockArea!='center':
			self.addDockWidget(dockArea, window)
		elif dockArea=='center':
			self.setCentralWidget(window)
			window.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
			window.hideTitleBar()
		else:
			window.setFloating(True)
			# window.setupCustomTitleBar()

		minSize=dockOptions.get('minSize',None)
		if minSize:
			window.setMinimumSize(*minSize)
		else:
			window.setMinimumSize(20,20)

		size=dockOptions.get('size',None)
		if size:
			window.resize(*size)

		if not dockOptions.get('autohide',False):
			window._useWindowFlags()

		window.dockOptions=dockOptions

		return window

	def requestToolWindow(self, id, **option ):
		pass

	def onTabCloseRequested( self, idx ):
		subwindow = self.centerTabWidget.widget( idx )
		if subwindow.close():
			self.centerTabWidget.removeTab( idx )

	def requestToolBar( self, name, **options ):
		toolbar = QtGui.QToolBar()
		toolbar.setFloatable( options.get( 'floatable', False ) )
		toolbar.setMovable(   options.get( 'movable',   True ) )		
		toolbar.setObjectName( 'toolbar-%s' % name )
		self.addToolBar( toolbar )
		return toolbar
		
	def onDocumentTabChanged( self, idx ):
		w = self.centerTabWidget.currentWidget()
		if w: w.setFocus()
	

##----------------------------------------------------------------##
class SubWindowMixin:	
	def setDocumentName( self, name ):
		self.documentName = name
		if name:
			title = '%s - %s' % ( self.documentName, self.titleBase )
			self.setWindowTitle( title )
		else:
			self.setWindowTitle( self.titleBase )
		
	def setupUi(self):
		self.container = self.createContainer()
		
		self.mainLayout = QtGui.QVBoxLayout(self.container)
		self.mainLayout.setSpacing(0)
		self.mainLayout.setMargin(0)
		self.mainLayout.setObjectName('MainLayout')

	def createContainer(self):
		container = QtGui.QWidget(self)
		self.setWidget(container)
		return container


	def addWidget(self, widget, **layoutOption):
		# widget.setParent(self)		
		if layoutOption.get('fixed', False):
			widget.setSizePolicy(
				QtGui.QSizePolicy.Fixed,
				QtGui.QSizePolicy.Fixed
				)
		elif layoutOption.get('expanding', True):
			widget.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Expanding
				)		
		self.mainLayout.addWidget(widget)
		return widget

	def addWidgetFromFile(self, uiFile, **layoutOption):
		form = uic.loadUi(uiFile)
		return self.addWidget(form, **layoutOption)	

	def moveToCenter(self):
		moveWindowToCenter(self)

	def ensureVisible(self):
		ensureWindowVisible(self)

##----------------------------------------------------------------##
				
class SubWindow(QtGui.QMainWindow, SubWindowMixin):
	def __init__(self, parent):
		super(SubWindow, self).__init__(parent)
		self.setupUi()
		self.stayOnTop = False
		self.setFocusPolicy( Qt.WheelFocus )


	def hideTitleBar(self):
		pass
		# emptyTitle=QtGui.QWidget()
		# self.setTitleBarWidget(emptyTitle)

	def createContainer(self):
		container=QtGui.QWidget(self)
		self.setCentralWidget(container)
		return container


	def startTimer(self, fps, trigger):
		assert(hasattr(trigger,'__call__'))
		interval = 1000/fps
		timer=QtCore.QTimer(self)
		timer.timeout.connect(trigger)
		timer.start(interval)
		return timer


	def focusOutEvent(self, event):
		pass

	def focusInEvent(self, event):
		pass

##----------------------------------------------------------------##
class DocumentWindow( SubWindow ):
	def show( self, *args ):
		tab = self.parentWindow.centerTabWidget
		idx = tab.indexOf( self )
		if idx < 0:
			idx = tab.addTab( self, self.windowTitle() )
		super( DocumentWindow, self ).show( *args )
		tab.setCurrentIndex( idx )

	def setWindowTitle( self, title ):
		super( DocumentWindow, self ).setWindowTitle( title )
		tabParent = self.parentWindow.centerTabWidget
		idx = tabParent.indexOf( self )
		tabParent.setTabText( idx, title )
		
	def addToolBar(self):
		return self.addWidget( QtGui.QToolBar(), expanding = False ) 
		
##----------------------------------------------------------------##
class DockWindowTitleBar( QtGui.QWidget ):
	"""docstring for DockWindowTitleBar"""
	def __init__(self, *args):
		super(DockWindowTitleBar, self).__init__(*args)

	def sizeHint(self):
		return QtCore.QSize(20,15)

	def minimumSizeHint(self):
		return QtCore.QSize(20,15)

##----------------------------------------------------------------##
class DockWindow(QtGui.QDockWidget, SubWindowMixin):
	"""docstring for DockWindow"""	
	def __init__(self, parent):
		super(DockWindow, self).__init__(parent)
		self.setupUi()
		self.setupCustomTitleBar()
		self.topLevelChanged.connect( self.onTopLevelChanged )
		font = QtGui.QFont()
		font.setPointSize(11)
		self.setFont(font)
		# signals.connect( 'app.activate', self.onAppActivate )
		# signals.connect( 'app.deactivate', self.onAppDeactivate )
		self.topLevel  = False
		self.stayOnTop = False

	def setupCustomTitleBar(self):
		self.originTitleBar = self.titleBarWidget()
		self.customTitleBar = DockWindowTitleBar( self )
		self.customTitleBar = self.originTitleBar
		self.setTitleBarWidget( self.customTitleBar )
		pass

	def _useWindowFlags(self):
		pass

	def setStayOnTop( self, stayOnTop ):
		self.stayOnTop = stayOnTop
		if stayOnTop and self.topLevel:
			self.setWindowFlags( Qt.Window | Qt.WindowStaysOnTopHint )
		
	def hideTitleBar(self):
		emptyTitle = QtGui.QWidget()
		self.setTitleBarWidget(emptyTitle)

	def startTimer(self, fps, trigger):
		assert(hasattr(trigger,'__call__'))
		interval = 1000/fps
		timer=QtCore.QTimer(self)
		timer.timeout.connect(trigger)
		timer.start(interval)
		return timer

	def onTopLevelChanged(self, toplevel):
		self.topLevel = toplevel
		if toplevel:
			self.setTitleBarWidget( self.originTitleBar )
			flag = Qt.Window
			if self.stayOnTop:
				flag |= Qt.WindowStaysOnTopHint
			self.setWindowFlags( flag )
			self.show()
		else:
			self.setTitleBarWidget( self.customTitleBar )
			pass

	def addToolBar(self):
		return self.addWidget( QtGui.QToolBar(), expanding = False ) 

