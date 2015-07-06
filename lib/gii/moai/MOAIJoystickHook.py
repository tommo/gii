from gii.core import *
from freejoy  import Joystick, getJoystickCount
from MOAIRuntime import getAKU

##----------------------------------------------------------------##
class MOAIJoystickSensorGetter():
	def __init__( self, joyId ):
		joyName = 'joy-%d' % joyId
		#button - keyboard sensor
		self.buttonSensorName = joyName + '.button'
		#axis
		axisSensorNames = []
		maxJoystickAxisCount = 6
		for axisId in range( 1, maxJoystickAxisCount + 1 ):
			axisSensorName = joyName + ( '.axis-%d' % axisId )
			axisSensorNames.append( axisSensorName )
		self.axisSensorNames = axisSensorNames

	def getButtonSensor( self, inputDevice ):
		return inputDevice.getSensor( self.buttonSensorName )

	def getAxisSensor( self, inputDevice, axisId ):
		name = self.axisSensorNames[ axisId ]
		return inputDevice.getSensor( name )

##----------------------------------------------------------------##
class MOAIJoystickHook( EditorModule ):
	name       = 'joystick_hook'
	dependency = [ 'moai' ]

	def __init__( self ):
		self.joysticks = []
		self.joystickSensorGetters = []
		for i in range( 0, 8 ):
			j = Joystick( i )
			j.setButtonListener( self.onButtonEvent )
			j.setAxisListener( self.onAxisEvent )
			j.setContext( i )
			self.joysticks.append( j )
			getter = MOAIJoystickSensorGetter( i + 1 )
			self.joystickSensorGetters.append( getter )

		self.joystickCount = 0
		self.inputDevice   = None

	def onLoad( self ):
		self.refreshJoysticks()	
		runtime = self.getModule( 'moai' )

	def setInputDevice( self, inputDevice ):
		self.inputDevice = inputDevice

	def onUpdate( self ):
		joysticks = self.joysticks
		for i in range( 0, self.joystickCount ):
			joysticks[ i ].poll()
	
	def refreshJoysticks( self ):
		self.joystickCount = getJoystickCount()
		logging.info( 'found joysticks: %d' % self.joystickCount )
		for j in self.joysticks:
			j.flush()

	def onButtonEvent( self, joystick, buttonId, down ):		
		jid = joystick.getContext()
		inputDevice = self.inputDevice
		if not inputDevice: return
		getter = self.joystickSensorGetters[ jid ]
		sensor = getter.getButtonSensor( inputDevice )
		if sensor:
			sensor.enqueueKeyEvent( buttonId, down )

	def onAxisEvent( self, joystick, axisId, value ):		
		jid = joystick.getContext()
		inputDevice = self.inputDevice
		if not inputDevice: return
		getter = self.joystickSensorGetters[ jid ]
		sensor = getter.getAxisSensor( inputDevice, axisId )
		if sensor:
			sensor.enqueueEvent( value )
			# print 'joyAxis', axisId, value
