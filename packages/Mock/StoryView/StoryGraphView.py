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
_DEFAULT_BG = makeBrush( color = '#222' )
makeStyle( 'cv',                '#ffffff',    '#acbcff'              )
makeStyle( 'tp',                dict( color = '#b940d6', alpha=0.5 ),    '#b940d6'    )
makeStyle( 'curve',             '#c1ff03',    None             )


##----------------------------------------------------------------##
class StoryGraphView( GraphNodeViewWidget ):
	def __init__(self, *args, **kwargs ):
		super(StoryGraphView, self).__init__( *args, **kwargs )
