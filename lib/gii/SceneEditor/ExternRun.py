import logging

from gii.core import *
from gii.core.tools import RunHost

from PyQt4 import QtGui,QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox

import threading
import time

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

DialogForm,BaseClass = uic.loadUiType( _getModulePath('ExternRun.ui') )


##----------------------------------------------------------------##
def _formatSeconds( seconds ):
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	return "%d:%02d:%02d" % (h, m, s)

##----------------------------------------------------------------##
_currentExternRunDialog = None

class ExternRunDialog( QtGui.QDialog ):
	def __init__( self, targetName, **kwargs ):
		global _currentExternRunDialog
		super( ExternRunDialog, self ).__init__( **kwargs )
		_currentExternRunDialog = self
		self.ui = DialogForm()
		self.ui.setupUi( self )
		self.targetName = targetName
		self.playerThread = ExternRunThread( self.targetName )
		self.finished = False
		
		self.playerThread.start()

		self.timer = QtCore.QTimer( self )
		self.timer.setInterval( 50 )
		self.timer.timeout.connect( self.onTimerTick )
		self.timer.start()

		self.startTime = time.time()

		self.ui.buttonTerminate.clicked.connect( self.onButtonTerminate )

		# self.setWindowModality( Qt.ApplicationModal )
		self.setWindowModality( Qt.WindowModal )
		self.show()

		signals.emit( 'external_player.start', targetName )


	def setMessage( self, msg ):
		self.ui.labelMessage.setText( msg )

	def onTimerTick( self ):
		elapsed = time.time() - self.startTime
		self.ui.labelElapsed.setText( 'Elapsed: ' + _formatSeconds( elapsed ) )
		if not self.playerThread.finished: return
		self.timer.stop()
		self.onFinish()

	def onFinish( self ):
		self.ui.buttonTerminate.setText( 'OK' )
		self.finished = True
		self.setWindowModality( Qt.NonModal )
		self.setMessage( 'Finished' )
		signals.emit( 'external_player.stop' )

		if self.ui.checkAutoClose.isChecked():
			self.hide()
			self.close()

	def onButtonTerminate( self ):
		if self.finished:
			self.close()
		else:
			RunHost.terminate()
			self.playerThread.finished = True
			self.ui.buttonTerminate.setEnabled( False )

	def closeEvent( self ,ev ):
		_currentExternRunDialog = None
		return super( ExternRunDialog, self ).closeEvent( ev )

##----------------------------------------------------------------##
class ExternRunThread( threading.Thread ):
	def __init__( self, targetName ):
		super( ExternRunThread, self ).__init__()
		self.targetName = targetName
		self.finished = False

	def run( self ):
		if not self.targetName:
			return
		RunHost.run( self.targetName )
		self.finished = True


##----------------------------------------------------------------##
def runScene( scnPath, **kwargs ):
	app.getProject().save()
	parentWindow = kwargs.get( 'parent_window', None )
	dialog = ExternRunDialog( 'main_preview_scene', parent = parentWindow )
	dialog.setMessage( 'Running current scene' )
	dialog.setWindowTitle( 'Running current scene' )

def runGame( **kwargs ):
	app.getProject().save()
	parentWindow = kwargs.get( 'parent_window', None )
	dialog = ExternRunDialog( 'main', parent = parentWindow )
	dialog.setMessage( 'Running game' )
	dialog.setWindowTitle( 'Running game' )

