from TimelineWidget import *
from random import random

_spanid = 1
class TestSpan():
	def __init__( self, track ):
		global _spanid
		_spanid += 1
		self.name = 'span - %d' % _spanid
		self.length = random()* 1000
		self.pos    = random()*1000 + 50
		self.track  = track

class TestTrack():
	def __init__( self, name ):
		self.name = name
		self.spans = [
			TestSpan( self ),
			TestSpan( self )
		]

class TestEvent():
	def __init__( self ):
		self.name = 'event'

dataset = [
	TestTrack( 'track' ),
	TestTrack( 'track0' ),
	TestTrack( 'track1' ),
	TestTrack( 'track2' ),
	TestTrack( 'track3' )
]

class TestTimeline( TimelineWidget ):
	def getTrackNodes( self ):
		return dataset

	def getSpanNodes( self, trackNode ):
		return trackNode.spans

	def getSpanParam( self, spanNode ): #pos, length
		return spanNode.pos, spanNode.length

	def getParentTrackNode( self, spanNode ):
		return spanNode.track

	def updateTrackContent( self, track, trackNode, **option ):
		track.getHeader().setText( trackNode.name )

	def updateSpanContent( self, span, spanNode, **option ):
		pass



class TestFrame( QtGui.QWidget ):
	def __init__( self ):
		pass

app = QtGui.QApplication( sys.argv )
styleSheetName = 'xn.qss'
app.setStyleSheet(
		open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
	)

timeline = TestTimeline()
timeline.resize( 600, 300 )
timeline.show()
timeline.raise_()
timeline.rebuild()


app.exec_()
		