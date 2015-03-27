import os.path

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QEventLoop, QEvent, QObject

import logging
from gii.core import app

_cursorCache = {}

def getCursor(name, fallback=None):
	global _cursorCache
	if not name: return QtGui.QCursor()

	cursor = _cursorCache.get(name,None)
	if cursor: return cursor
	iconFile = None
	path = app.findDataFile( 'cursor/%s.png' % name )
	if not path:
		if fallback:
			return getCursor(fallback)
		logging.error('cursor not found: %s' % name)
		return QtGui.QCursor()

	cursor = QtGui.QCursor(QtGui.QPixmap(path))
	_cursorCache[name]=cursor
	return cursor

