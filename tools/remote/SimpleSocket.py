import sys
import logging
import os
import SocketServer
import socket
import threading

RemoteArgumentCallBack=None

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        cur_thread = threading.currentThread()
        data = data.split()
        #Note to the self.server.app
        if not RemoteArgumentCallBack is None:
            RemoteArgumentCallBack( data, self.request )
        self.request.send('<OK>')

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    stopped = False
    allow_reuse_address = True

    def serve_forever(self):
        while not self.stopped:
            self.handle_request()

    def force_stop(self):
        self.server_close()
        self.stopped = True

def send_to_server(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.send(message)
    response = sock.recv(1024)
    sock.close()
    return response

def start_server(host, port):

    server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.setDaemon(True)
    server_thread.start()

    return server

server = None
def checkSingleInstance(PORT=61957):
    # HOST = socket.gethostname()
    HOST = '127.0.0.1'
    argv=sys.argv[:]
    argv.insert(0, os.path.realpath('.'))
    # if len(argv) > 1:
    #     argv[1]=os.path.realpath(argv[1])
    try:
        send_to_server(HOST, PORT, ' '.join(argv))
        logging.warn( "running instance detected" )
        sys.exit()
    except socket.error:
        pass
        server = start_server(HOST, PORT)
    return True

def setRemoteArgumentCallback(callback):
    global RemoteArgumentCallBack
    RemoteArgumentCallBack=callback

