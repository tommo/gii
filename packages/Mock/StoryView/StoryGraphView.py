import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor

from gii.qt.controls.GraphicsView.GraphNodeView import  *

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt


##----------------------------------------------------------------##
class StoryGraphView( GraphNodeViewWidget ):
	def __init__(self, *args, **kwargs ):
		super(StoryGraphView, self).__init__( *args, **kwargs )
		self.owner = None

	def setOwner( self, owner ):
		self.owner = owner

	