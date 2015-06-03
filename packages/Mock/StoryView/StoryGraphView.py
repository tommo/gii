import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor

from gii.qt.controls.GraphicsView.GraphicsViewHelper import  *

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
_DEFAULT_BG = makeBrush( color = '#222' )
makeStyle( 'cv',                '#ffffff',    '#acbcff'              )
makeStyle( 'tp',                dict( color = '#b940d6', alpha=0.5 ),    '#b940d6'    )
makeStyle( 'curve',             '#c1ff03',    None             )


##----------------------------------------------------------------##
class StoryGraphView( GLGraphicsView ):
	def __init__(self, *args, **kwargs ):
		super(StoryGraphView, self).__init__( *args, **kwargs )

		scene = QtGui.QGraphicsScene()
		self.setScene( scene )
		self.setBackgroundBrush( _DEFAULT_BG )
		
		#grid
		self.gridSize = 100
		self.gridBackground = GridBackground()
		self.gridBackground.setGridSize( self.gridSize, self.gridSize )
		self.gridBackground.setAxisShown( True, True )
		self.gridBackground.setCursorVisible( False )
		scene.addItem( self.gridBackground )

