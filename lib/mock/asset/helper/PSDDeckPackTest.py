from PSDDeckPackProject import *
import PSDDeckMQuad
import PSDDeckMTileset

proj = PSDDeckPackProject()
proj.loadPSD( 'test/test.decks.psd' )
proj.save( 'test/', 'testpack', ( 2048, 2048 ) )