# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform

from GraphicsViewHelper import *

import sys
import math


##----------------------------------------------------------------##
class GraphNodeItemBase():
	def isGroup( self ):
		return False

	def initGraphNode( self ):
		pass

	def acceptConnection( self, conn ):
		return False

	def createConnection( self, **options ):
		return None


if __name__ == '__main__':
	import TestGraphView
	