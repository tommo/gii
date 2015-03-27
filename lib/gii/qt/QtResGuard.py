from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QEventLoop, QEvent, QObject

from gii.core import ResGuard

class ResGuardQWidget(object):
	
	target = QtGui.QWidget

	def onRelease( self, widget ):
		print 'releasing widget!!', widget
		widget.setParent( None )
