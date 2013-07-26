import signals
import logging
from PyQt4 import QtGui, QtCore

from PyQt4.QtGui import QMenu, QMenuBar, QToolBar, QAction

class ToolBar(object):
	"""docstring for ToolBar"""
	def __init__(self, toolbar):
		super(ToolBar, self).__init__()
		self.toolbar=toolbar
		self.items=[]