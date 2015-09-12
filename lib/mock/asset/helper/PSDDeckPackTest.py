from PSDDeckPackProject import *
import PSDDeckMQuad
import PSDDeckMTileset

proj = PSDDeckPackProject()
proj.setDefaultProcessor( 'mquad' )
proj.loadPSD( 'test/test2.decks.psd' )
proj.save( 'test/', 'testpack', ( 2048, 2048 ) )