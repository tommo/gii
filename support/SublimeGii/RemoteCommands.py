import sys
import logging
import os
import socket

import sublime_plugin
import sublime

def send_to_server( message = '', ip = '127.0.0.1', port = 61957 ):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((ip, port))
	sock.send(message)
	response = sock.recv(1024)
	sock.close()
	return response



class GiiSendRemoteCommand(sublime_plugin.WindowCommand):
	def run(self, **kwargs):
		self.kwargs = kwargs
		sublime.active_window().show_input_panel('Command to send:', '', self.do, None, None)

	def do(self, command):
		kwargs = self.kwargs
		kwargs['cmd'] = command
		send_to_server( command )


class GiiReloadScriptCommand(sublime_plugin.WindowCommand):
	def run(self, **kwargs):
		send_to_server( 'reload_script' )



class GiiRunGameCommand(sublime_plugin.WindowCommand):
	def run(self, **kwargs):
		send_to_server( 'run_game' )

class GiiEvalCommand(sublime_plugin.WindowCommand):
	def run(self, **kwargs):
		sublime.active_window().show_input_panel('(Gii)Script to execute:', '', self.do, None, None)

	def do(self, script):
		send_to_server( 'eval '+script )
	

class GiiPreviewStartCommand(sublime_plugin.WindowCommand):
	def run(self, **kwargs):
		send_to_server( 'reload_script' )
		send_to_server( 'preview_start' )


class GiiPreviewStopCommand(sublime_plugin.WindowCommand):
	def run(self, **kwargs):
		send_to_server( 'preview_stop' )

