from abc import ABCMeta, abstractmethod
import logging
import json
import os
import os.path
import sys

import signals
from project import Project

##----------------------------------------------------------------##
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

	def register( self ):
		depolyManager.registerTarget( self )

##----------------------------------------------------------------##
class DeployManager( object ):
	def __init__( self ):
		self.targets = {}

	def build( self ):
		pass

	def deploy( self ):
		pass

	def registerTarget( self, target ):
		self.targets[ target.getName() ] = target

	def getTarget( self, name ):
		return self.target.get( name, None )

##----------------------------------------------------------------##
depolyManager = DeployManager()