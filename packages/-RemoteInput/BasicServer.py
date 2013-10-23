from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import time
import threading

_LISTENER_PORT = 8080

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class Handler(BaseHTTPRequestHandler):

	def do_GET(self):
		self.send_response(200)
		self.end_headers()
		print self.path
		if self.path == '/':
			f = file( _getModulePath( 'main.htm' ), 'r' )
			txt = f.read()
			f.close()
			self.wfile.write( txt )

		elif self.path == '/input':
			print self.path

		return

	def log_message( self, format, *ars ):
		pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""    

_Running = False

def _startServer():
	global _Running
	server = ThreadedHTTPServer(('0.0.0.0', _LISTENER_PORT), Handler)
	_Running = True
	server.timeout = 0
	print 'start remote input listener at port: %d' % _LISTENER_PORT 
	while _Running:
		server.handle_request()
		time.sleep(0.05)


def startServer():
	threading.Thread( target = _startServer ).start()

def stopServer():
	global _Running
	_Running = False
	