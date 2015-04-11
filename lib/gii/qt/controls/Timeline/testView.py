from TimelineView import *
from random import random
from PyQt4 import QtOpenGL

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

class TestTrack():
	def __init__( self, name ):
		self.name = name
		self.keys = [
			TestKey( self ),
			TestKey( self ),
			TestKey( self ),
			TestKey( self )
		]

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

	def formatPos( self, pos ):
		i = int( pos/1000 )
		f = int( pos - i*1000 )
		return '%d:%02d' % ( i, f/10 )

	def getRulerParam( self ):
		return dict( zoom = 1 )
		# return dict( zoom = 5 )


class TestFrame( QtGui.QWidget ):
	def __init__( self ):
		pass

app = QtGui.QApplication( sys.argv )
styleSheetName = 'gii.qss'
app.setStyleSheet(
		open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
	)
timeline = TestTimeline()
timeline.resize( 600, 300 )
timeline.show()
timeline.raise_()
timeline.rebuild()
# # timeline.setZoom( 10 )
# # timeline.selectTrack( dataset[1] )
# timeline.selectKey( dataset[1].keys[0] )

app.exec_()