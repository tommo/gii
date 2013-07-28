cdef extern from *:
	ctypedef char* const_char_ptr "const char*"

ctypedef void (*funcOpenWindow)( const_char_ptr title, int width, int height)
ctypedef void (*funcEnterFullscreen)()
ctypedef void (*funcExitFullscreen)()

cdef extern from "aku/AKU.h" nogil:
	ctypedef struct lua_State:
		pass
	# call back
	
	void AKUSetFunc_OpenWindow(funcOpenWindow func)
	void AKUSetFunc_EnterFullscreenMode(funcEnterFullscreen func)
	void AKUSetFunc_ExitFullscreenMode(funcExitFullscreen func)

	# context api
	void		AKUClearMemPool				()
	int			AKUCreateContext			()
	void		AKUDeleteContext			( int context )
	int			AKUGetContext				()
	void*		AKUGetUserdata				()
	void		AKUFinalize				()
	void		AKUInitMemPool				( size_t sizeInBytes )
	void		AKUSetContext				( int context )
	void		AKUSetUserdata				( void* user )

	# management api
	void		AKUDetectGfxContext			()
	lua_State*		AKUGetLuaState				()
	double		AKUGetSimStep				()
	char*		AKUGetWorkingDirectory		( char* buffer, int length )
	int			AKUMountVirtualDirectory		( const_char_ptr virtualPath, const_char_ptr archive )
	void		AKUPause				( bint pause )
	void		AKUReleaseGfxContext		()
	void		AKURender				()
	void		AKURunBytecode				( void* data, size_t size )
	void		AKURunScript				( const char* filename )
	void		AKURunString				( const char* script )
	void		AKUSetOrientation			( int orientation )
	void		AKUSetScreenDpi				( int dpi )
	void		AKUSetScreenSize			( int width, int height )
	void		AKUSetViewSize				( int width, int height )
	void		AKUSoftReleaseGfxResources		( int age )
	int			AKUSetWorkingDirectory		( const_char_ptr path )
	void		AKUUpdate				()

	# input device api
	void		AKUReserveInputDevices		( int total )
	void		AKUReserveInputDeviceSensors	( int deviceID, int total )
	void		AKUSetInputConfigurationName	( const_char_ptr name )
	void		AKUSetInputDevice			( int deviceID, const_char_ptr name )
	void		AKUSetInputDeviceActive		( int deviceID, bint active )
	void		AKUSetInputDeviceButton		( int deviceID, int sensorID, const_char_ptr name )
	void		AKUSetInputDeviceCompass		( int deviceID, int sensorID, const_char_ptr name )
	void		AKUSetInputDeviceKeyboard		( int deviceID, int sensorID, const_char_ptr name )
	void		AKUSetInputDeviceLevel		( int deviceID, int sensorID, const_char_ptr name )
	void		AKUSetInputDeviceLocation		( int deviceID, int sensorID, const_char_ptr name )
	void		AKUSetInputDevicePointer		( int deviceID, int sensorID, const_char_ptr name )
	void		AKUSetInputDeviceTouch		( int deviceID, int sensorID, const_char_ptr name )
	void		AKUSetInputDeviceWheel		( int deviceID, int sensorID, const_char_ptr name )

	# input events api
	void		AKUEnqueueButtonEvent		( int deviceID, int sensorID, bint down )
	void		AKUEnqueueCompassEvent		( int deviceID, int sensorID, float heading )
	void		AKUEnqueueKeyboardAltEvent		( int deviceID, int sensorID, bint down )
	void		AKUEnqueueKeyboardControlEvent	( int deviceID, int sensorID, bint down )
	void		AKUEnqueueKeyboardEvent		( int deviceID, int sensorID, int keyID, bint down )
	void		AKUEnqueueKeyboardShiftEvent	( int deviceID, int sensorID, bint down )
	void		AKUEnqueueLevelEvent		( int deviceID, int sensorID, float x, float y, float z )
	void		AKUEnqueueLocationEvent		( int deviceID, int sensorID, double longitude, double latitude, double altitude, float hAccuracy, float vAccuracy, float speed )
	void		AKUEnqueuePointerEvent		( int deviceID, int sensorID, int x, int y )
	void		AKUEnqueueTouchEvent		( int deviceID, int sensorID, int touchID, bint down, float x, float y )
	void		AKUEnqueueTouchEventCancel		( int deviceID, int sensorID )
	void		AKUEnqueueWheelEvent		( int deviceID, int sensorID, float value )

	# extra
	
cdef extern from "aku/AKU-luaext.h" nogil:
	void AKUExtLoadLuacrypto()
	void AKUExtLoadLuacurl()
	void AKUExtLoadLuafilesystem()
	void AKUExtLoadLuasocket()
	void AKUExtLoadLuasql()
	void AKUExtLoadLPeg()
	void AKUExtLoadStruct()

cdef extern from "aku/AKU-untz.h" nogil:
	void AKUUntzInit()

cdef extern from "aku/AKU-fmod-designer.h" nogil:
	void AKUFmodDesignerUpdate( float step )
	void AKUFmodDesignerInit()


cdef extern from "aku/AKU-audiosampler.h" nogil:
	void AKUAudioSamplerInit()
	# extension loaders
cdef extern from "extensionClasses.h" nogil:
	void registerExtensionClasses()

cdef extern from "helpers.h" nogil:
	void registerHelpers()

