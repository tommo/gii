from gii.core                 import *
from gii.moai.MOAIEditCanvas  import MOAIEditCanvas
from gii.AssetEditor          import AssetPreviewer
from gii.qt.helpers           import addWidgetWithLayout

from PyQt4 import uic
from PyQt4 import QtGui

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class ParticlePreviewer(AssetPreviewer):
	def createWidget(self, container):
		self.canvas=addWidgetWithLayout(
			MOAIEditCanvas(container)			
		)
		self.canvas.loadScript( _getModulePath('ParticlePreview.lua') )
		return self.canvas

	def accept(self, assetNode):
		return assetNode.getType() in [ 'particle_system', 'particle_pex'  ]

	def onStart(self, assetNode):
		atype = assetNode.getType()
		self.canvas.makeCurrent()
		self.canvas.safeCallMethod( 'preview', 'showParticle', assetNode.getPath() )
		self.canvas.startUpdateTimer( 60 )
		
	def onStop(self):
		self.canvas.stopUpdateTimer()
		self.canvas.safeCallMethod( 'preview', 'clearParticle' )

ParticlePreviewer().register()

