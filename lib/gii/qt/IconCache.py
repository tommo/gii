import os.path

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QEventLoop, QEvent, QObject

import logging
from gii.core import app

_iconCache={}
def getIcon(name, fallback=None):
	global _iconCache
	if not name: return QtGui.QIcon()

	icon = _iconCache.get(name,None)
	if icon: return icon

	path = app.getPath( 'data/icons/%s.png' % name )
	if not os.path.exists(path):
		if fallback:
			return getIcon(fallback)
		logging.info('icon not found:' + path)
		return None

	icon = QtGui.QIcon(QtGui.QPixmap(path))
	_iconCache[name]=icon
	return icon
