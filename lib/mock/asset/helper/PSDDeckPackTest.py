from PSDDeckPackProject import *
import PSDDeckMTileset
import PSDDeckMQuad

proj = PSDDeckPackProject()
proj.setDefaultProcessor( 'mquad' )
proj.loadPSD( 'test/test.decks.psd' )
proj.save( 'test/', 'testpack', ( 2048, 2048 ) )
