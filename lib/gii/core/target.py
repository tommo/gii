from abc import ABCMeta, abstractmethod
import logging
import json
import os
import os.path
import sys

class Target(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def getName( self ):
		pass

	def preBuild( self, project ):
		pass

	def onBuild( self, project ):
		pass

	def preDeploy( self, project ):
		pass

	def onDeploy( self, project ):
		pass

