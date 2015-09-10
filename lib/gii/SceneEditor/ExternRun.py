import logging

from gii.core import *
from gii.core.tools import RunHost

from PyQt4 import QtGui,QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox

import threading


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

DialogForm,BaseClass = uic.loadUiType( _getModulePath('ExternRun.ui') )

##----------------------------------------------------------------##
_currentExternRunDialog = None

class ExternRunDialog( QtGui.QDialog ):
	def __init__( self, targetName ):
		global _currentExternRunDialog
		super( ExternRunDialog, self ).__init__()
		_currentExternRunDialog = self
		self.ui = DialogForm()
		self.ui.setupUi( self )
		self.targetName = targetName
		self.playerThread = ExternRunThread( self.targetName )
		
		self.timer = QtCore.QTimer( self )
		self.timer.setInterval( 50 )
		self.timer.timeout.connect( self.onTimerTick )
		self.timer.start()

		self.ui.buttonTerminate.clicked.connect( self.onButtonTerminate )

		self.setWindowModality( Qt.ApplicationModal )
		self.show()

		self.playerThread.start()

	def onTimerTick( self ):
		if self.playerThread.isAlive(): return
		self.timer.stop()
		self.onFinish()

	def onFinish( self ):
		self.setWindowModality( Qt.NonModal )
		if self.ui.checkAutoClose.isChecked():
			self.hide()
			self.close()

	def onButtonTerminate( self ):
		RunHost.terminate()
		self.ui.buttonTerminate.setEnabled( False )
		pass

	def closeEvent( self ,ev ):
		_currentExternRunDialog = None
		return super( ExternRunDialog, self ).closeEvent( ev )

##----------------------------------------------------------------##
class ExternRunThread( threading.Thread ):
	def __init__( self, targetName ):
		super( ExternRunThread, self ).__init__()
		self.targetName = targetName

	def run( self ):
		if not self.targetName:
			return
		RunHost.run( self.targetName )


##----------------------------------------------------------------##
def runScene( scnPath ):
	app.getProject().save()
	dialog = ExternRunDialog( 'main_preview_scene' )

def runGame():
	app.getProject().save()
	dialog = ExternRunDialog( 'main' )

