class MOAIJoystickFFBSensorSDL :
	public MOAISensor
{

public:
	MOAIJoystickFFBSensorSDL(arguments);
	~MOAIJoystickFFBSensorSDL();

	/* data */
};

void AKUSetInputDeviceJoystickFFB( int deviceID, int sensorID, char const* name ) {
	MOAISim::Get ().GetInputMgr ().SetSensor < MOAIJoystickSensor >(( u8 )deviceID, ( u8 )sensorID, name );
}