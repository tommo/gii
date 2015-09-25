import sys
import os

from PyQt4 import QtGui, QtCore, QtOpenGL, uic

from GraphNodeView import *

app = QtGui.QApplication( sys.argv )
styleSheetName = 'gii.qss'
app.setStyleSheet(
		open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
	)

g = GraphNodeViewWidget()
g.resize( 600, 300 )
g.show()
g.raise_()
# Graph.setZoom( 10 )
# Graph.selectTrack( dataset[1] )

app.exec_()
