import logging
from PyQt4 import QtGui,QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox

import threading


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

ProcessDialogForm,BaseClass = uic.loadUiType( _getModulePath('ProcessDialog.ui') )

class ProcessDialog( QtGui.QFrame ):
	def __init__( self, *args, **kwargs ):
		super( ProcessDialog, self ).__init__( *args, **kwargs )
		self.ui = ProcessDialogForm()
		self.ui.setupUi( self )
		self.setWindowFlags( Qt.Dialog )

def requestProcess( message, **options ):
	dialog = ProcessDialog()
