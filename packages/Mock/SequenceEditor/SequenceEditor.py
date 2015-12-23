# -*- coding: utf-8 -*-

import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor

from gii.SceneEditor  import SceneEditorModule

from gii.moai.MOAIRuntime import MOAILuaDelegate

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

from SequenceEditorWidget import SequenceEditorWidget


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class SequenceView( SceneEditorModule ):
	name       = 'sequence_editor'
	dependency = [ 'mock' ]

	def onLoad( self ):
		self.container = self.requestDockWindow(
				title = 'Sequence',
				dock = 'bottom'
			)
		self.window = window = self.container.addWidget( SequenceEditorWidget() )
		
		# self.canvas = addWidgetWithLayout(
		# 	MOAIEditCanvas( window.containerGraph )
		# )
		# self.delegate = MOAILuaDelegate( self )
		# self.delegate.load( _getModulePath( 'SequenceView.lua' ) )
		
		# self.updateTimer        = self.container.startTimer( 60, self.onUpdateTimer )
		self.updatePending      = False
		self.previewing         = False
		self.previewUpdateTimer = False		

	def onStart( self ):
		self.container.show()
		class TestRoutineNode(object):
			def __init__( self, parent ):
				self.parent = parent
				self.children = []
				self.mark = None
				self.index = 0

			def getParent( self ):
				return self.parent

			def getChildren( self ):
				return self.children

			def getTag( self ):
				testTag = [
					'SAY',#'<font color="#900">SAY</font>',
					'ANIM',#'<font color="#090">ANIM</font>',
					'SPAWN'#'<font color="#90a">SPAWN</font>'
				]
				return testTag[ self.index % len( testTag ) ]

			def getDesc( self ):
				testDesc = [
					"The <b>Dock Widgets</b> example demonstrates how to use ",
					"Qt's dock widgets. You can enter your own text, click a ",
					"customer to add a customer name and address, and click ",
					"standard paragraphs to add them.",
					"THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS",
					"* Neither the name of Nokia Corporation and its Subsidiary(-ies) nor"
				]

				return testDesc[ self.index % 6 ]

			def getMark( self ):
				return self.mark

			def getIndex( self ):
				return self.index

			def getMarkText( self ):
				if self.mark: return '<%s>' % self.mark
				return '%d' % self.index

			def addChild( self, node ):
				self.children.append( node )
				node.parent = self
				node.index = len( self.children )
				return node

		class TestRoutine(object):
			def __init__( self ):
				self.rootNode = TestRoutineNode( None )

			def getRootNode( self ):
				return self.rootNode

		testRoutine = TestRoutine()
		root = testRoutine.rootNode
		for k in range( 20 ):
			node = root.addChild(
				TestRoutineNode( None )
			)
			if k == 5:
				for j in range( 5 ):
					node.addChild(
						TestRoutineNode( None )
					)

		self.window.addRoutine( testRoutine )

	def onSetFocus( self ):
		self.getModule( 'scene_editor' ).setFocus()
		self.container.show()
		self.container.setFocus()

	def onUpdateTimer( self ):
		if self.updatePending == True:
			self.updatePending = False
			#TODO
	
