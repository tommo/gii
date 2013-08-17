from gii.core import *

import BasicServer

#a test entry
def postAppStart():
	BasicServer.startServer()

def onAppStop():
	BasicServer.stopServer()
	
signals.connect( 'app.post_start', postAppStart )
signals.connect( 'app.close', onAppStop )
