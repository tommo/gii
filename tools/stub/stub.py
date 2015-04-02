import os.path
import logging
import osbit

from gii.core import Project, app
from gii.qt.helpers   import addWidgetWithLayout
from gii.qt.dialogs   import alertMessage
from PyQt4    import QtGui, QtCore, uic
##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path
##----------------------------------------------------------------##
_task = {
	'task' : False,
	'path' : '',
	'option' : {}
}
##----------------------------------------------------------------##
class StubGui( QtGui.QWidget ):
	def __init__( self ):
		QtGui.QWidget.__init__( self )
		self.ui = addWidgetWithLayout( 
			uic.loadUi( _getModulePath( 'stub.ui' ) ),
			self
		)
		self.setMinimumSize( 600,400 )
		self.setMaximumSize( 600,400 )

		self.ui.buttonOpen.clicked.connect( self.onButtonOpen )
		self.ui.buttonNew.clicked.connect( self.onButtonNew )

		self.setWindowTitle( 'GII ( %d bits )' % osbit.pythonBits() )

	def onButtonNew( self ):
		alertMessage ( 'Not implemented','Not implemented yet, use CLI instead.')

	def onButtonOpen( self ):
		options   = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
		directory = QtGui.QFileDialog.getExistingDirectory(self,
			"Select Project Folder To Open",
			"",
			options
			)		
		if directory:
			info = Project.findProject( directory )
			if info:
				_task[ 'task' ] = 'open'
				_task[ 'path' ] = info['path']
				self.close()
			else:
				alertMessage( 'Project not found','No valid Gii project found.' )				

##----------------------------------------------------------------##
def start():
	stubApp = QtGui.QApplication( [] )
	gui = StubGui()
	gui.show()
	gui.raise_()
	stubApp.exec_()
	return _task
