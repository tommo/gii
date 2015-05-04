from TimelineView import *
from random import random
from PyQt4 import QtOpenGL

from time import time

_keyid = 1
class TestKey():
	def __init__( self, track ):
		global _keyid
		_keyid += 1
		self.name = 'key - %d' % _keyid
		# self.length = random()*500/1000.0
		self.length = 0.0
		self.pos    = ( random()*1000 + 50 ) /1000.0
		self.track  = track

_trackId = 0
class TestTrack():
	def __init__( self, name, pos = None ):
		global _trackId
		pos = _trackId * 25
		_trackId += 1
		self.name = name
		self.keys = [
			TestKey( self ),
			TestKey( self ),
			TestKey( self ),
			TestKey( self )
		]
		self.pos = pos

class TestEvent():
	def __init__( self ):
		self.name = 'event'

dataset = [
	TestTrack( 'track' ),
	TestTrack( 'track0' ),
	TestTrack( 'track1' ),
	TestTrack( 'track2' ),
	TestTrack( 'track3' ),
	TestTrack( 'track1' ),
	TestTrack( 'track2' ),
	TestTrack( 'track3' ),
	TestTrack( 'track1' ),
	TestTrack( 'track2' ),
	TestTrack( 'track3' )
]

class TestTimeline( TimelineView ):
	def getTrackNodes( self ):
		return dataset

	def getKeyNodes( self, trackNode ):
		return trackNode.keys

	def getKeyParam( self, keyNode ): #pos, length, resizable
		return keyNode.pos, keyNode.length, True

	def getParentTrackNode( self, keyNode ):
		return keyNode.track

	def updateTrackContent( self, track, trackNode, **option ):
		# track.getHeaderItem().setText( trackNode.name )
		pass

	def updateKeyContent( self, key, keyNode, **option ):
		pass

	def isTrackVisible( self, track ):
		return True

	def getTrackPos( self, track ):
		return track.pos

	def formatPos( self, pos ):
		i = int( pos/1000 )
		f = int( pos - i*1000 )
		return '%d:%02d' % ( i, f/10 )

	def getRulerParam( self ):
		return dict( zoom = 1 )
		# return dict( zoom = 5 )


class TestFrame( QtGui.QFrame ):
	def __init__( self ):
		super( TestFrame, self ).__init__()
		layout = QtGui.QVBoxLayout( self )
		layout.setMargin( 0 )
		timeline = TestTimeline()
		layout.addWidget( timeline )
		timeline.rebuild()

		timeline.keyChanged.connect( self.onKeyChanged )
		self.timer = QtCore.QTimer( self )
		self.timer.timeout.connect( self.onTimer )
		self.timer.setInterval( 100 )
		self.timer.start()
		self.t0 = time()

	def onKeyChanged( self, key ):
		pass

	def onTimer( self ):
		t1 = time()
		# print '%.2f' % (t1- self.t0)
		self.t0 = t1
		


app = QtGui.QApplication( sys.argv )
styleSheetName = 'gii.qss'
app.setStyleSheet(
		open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
	)
frame = TestFrame()

frame.resize( 600, 300 )
frame.show()
frame.raise_()

# # timeline.setZoom( 10 )
# # timeline.selectTrack( dataset[1] )
# timeline.selectKey( dataset[1].keys[0] )

app.exec_()
