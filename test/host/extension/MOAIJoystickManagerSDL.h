#ifndef	MOAIJOYSTICKMANAGERSDL_H
#define	MOAIJOYSTICKMANAGERSDL_H

//joystick
//haptic
#include <moai-sim/headers.h>

class MOAIJoystickManagerSDL:
	public MOAIGlobalClass < MOAIJoystickManagerSDL, MOAINode > 
{
private:
	
	//----------------------------------------------------------------//
	static int _getJoystickCount         ( lua_State* L );
	
	static int _getJoystickCount         ( lua_State* L );
	static int _getJoystickName          ( lua_State* L );
	static int _getJoystickGUID          ( lua_State* L );
	static int _getJoystickInputDevice   ( lua_State* L );
	static int _getJoystickHapticDevice  ( lua_State* L );
	
public:

	enum {
		EVENT_JOYSTICK_CONNECT,
		EVENT_JOYSTICK_DISCONNECT
	};
	
	
	DECL_LUA_SINGLETON ( MOAIJoystickManagerSDL )


	//----------------------------------------------------------------//
	MOAIJoystickManagerSDL();
	~MOAIJoystickManagerSDL();
	
	void			RegisterLuaClass	( MOAILuaState& state );
};


#endif