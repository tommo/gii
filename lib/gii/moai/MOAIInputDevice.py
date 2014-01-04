from AKU import getAKU, _LuaTable, _LuaThread, _LuaObject, _LuaFunction

##----------------------------------------------------------------##
## Input DEVICE
##----------------------------------------------------------------##
class MOAIInputDevice(object):
	def __init__( self, name, id ):
		self.id           = id
		self.name         = name or 'device'
		self.sensors      = {}
		self.lastSensorId = 0
		self.registered   = False

	def addSensor(self, name, sensorType='touch'):
		assert not self.registered, 'input device already registered !!'
		assert sensorType in ('touch', 'pointer', 'button', 'keyboard', 'level', 'compass'), 'unsupported sensor type'
		assert not self.sensors.has_key(name), 'duplicated sensor name'

		clas={
			'touch'    : MOAITouchSensor,
			'pointer'  : MOAIPointerSensor,
			'button'   : MOAIButtonSensor,
			'keyboard' : MOAIKeyboardSensor,
			'level'    : MOAILevelSensor,
			'compass'  : MOAICompassSensor
			} [sensorType]

		sensor=clas(self, self.lastSensorId, name)
		self.sensors[name]=sensor
		self.lastSensorId += 1

		getAKU().reserveInputDeviceSensors( self.id, self.lastSensorId )
		for k in self.sensors:
			sensor = self.sensors[k]
			sensor.onRegister()
		# sensor.onRegister()

	def getSensor(self, name):
		return self.sensors.get(name, None)

	def onRegister(self):
		getAKU().setInputDevice( self.id, self.name )
		getAKU().reserveInputDeviceSensors( self.id, self.lastSensorId )
		for k in self.sensors:
			sensor = self.sensors[k]
			sensor.onRegister()

##----------------------------------------------------------------##
## Input SENSOR
##----------------------------------------------------------------##
class MOAIInputSensor(object):
	def __init__(self, device, id, name):
		self.device=device
		self.id=id
		self.name=name

	def onRegister(self):
		pass

##----------------------------------------------------------------##
class MOAITouchSensor(MOAIInputSensor):
	def enqueueEvent(self, touchId, down, x, y):
		getAKU().enqueueTouchEvent(
				self.device.id,
				self.id,
				touchId,
				down,
				x,y
			)

	def enqueueEventCancel(self):
		getAKU().enqueueTouchEventCancel(
				self.device.id,
				self.id				
			)

	def onRegister(self):
		getAKU().setInputDeviceTouch(self.device.id, self.id, self.name)

##----------------------------------------------------------------##
class MOAIPointerSensor(MOAIInputSensor):
	"""docstring for MOAIPointerSensor"""
	def enqueueEvent(self, x, y):
		getAKU().enqueuePointerEvent(
				self.device.id,
				self.id,
				x, y
			)

	def onRegister(self):
		getAKU().setInputDevicePointer(self.device.id, self.id, self.name)


##----------------------------------------------------------------##
class MOAIButtonSensor(MOAIInputSensor):
	"""docstring for MOAIPointerSensor"""
	def enqueueEvent(self, down):
		getAKU().enqueueButtonEvent(
				self.device.id,
				self.id,
				down
			)

	def onRegister(self):
		getAKU().setInputDeviceButton(self.device.id, self.id, self.name)

##----------------------------------------------------------------##
class MOAILevelSensor(MOAIInputSensor):
	def enqueueEvent(self, x, y, z):
		getAKU().enqueueLevelEvent(
				self.device.id,
				self.id,
				x,y,z
			)

	def onRegister(self):
		getAKU().setInputDeviceLevel(self.device.id, self.id, self.name)

##----------------------------------------------------------------##
class MOAICompassSensor(MOAIInputSensor):
	def enqueueEvent(self, heading):
		getAKU().enqueueLevelEvent(
				self.device.id,
				self.id,
				heading
			)

	def onRegister(self):
		getAKU().setInputDeviceCompass(self.device.id, self.id, self.name)


##----------------------------------------------------------------##
class MOAIKeyboardSensor(MOAIInputSensor):
	def enqueueEvent(self, keyId, down):
		getAKU().enqueueKeyboardEvent(
				self.device.id, 
				self.id,
				keyId,
				down
			)

	def enqueueShiftEvent(self, down):
		getAKU().enqueueKeyboardShiftEvent(
				self.device.id, 
				self.id,
				down
			)

	def enqueueControlEvent(self, down):
		getAKU().enqueueKeyboardControlEvent(
				self.device.id, 
				self.id,
				down
			)

	def enqueueAltEvent(self, down):
		getAKU().enqueueKeyboardAltEvent(
				self.device.id, 
				self.id,
				down
			)

	def onRegister(self):
		getAKU().setInputDeviceKeyboard(self.device.id, self.id, self.name)
