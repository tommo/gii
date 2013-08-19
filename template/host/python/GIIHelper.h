#ifndef	GIIHELPER_H
#define	GIIHELPER_H
#include <pch.h>
#include <moaicore/MOAIActionMgr.h>
#include <moaicore/MOAIDebugLines.h>
#include <moaicore/MOAIFrameBuffer.h>
#include <moaicore/MOAIGfxDevice.h>
#include <moaicore/MOAIInputMgr.h>
#include <moaicore/MOAILogMessages.h>
#include <moaicore/MOAINodeMgr.h>
#include <moaicore/MOAIProp.h>
#include <moaicore/MOAISim.h>
#include <moaicore/MOAITextureBase.h>


class GIIHelper:
	public MOAIGlobalClass < GIIHelper, MOAILuaObject > 
{
private:
	
	//----------------------------------------------------------------//
	static int _stepSim             ( lua_State* L );
	static int _updateInput         ( lua_State* L );
	static int _setBufferSize       ( lua_State* L );
	static int _renderFrameBuffer   ( lua_State* L );
	static int _setVertexTransform  ( lua_State* L );

public:
	
	DECL_LUA_SINGLETON ( GIIHelper )

	//
	void stepSim( double step );
	void updateInput();

	//----------------------------------------------------------------//
	GIIHelper();
	~GIIHelper();
	
	void			RegisterLuaClass	( MOAILuaState& state );
};

extern "C"{
	void registerGIIHelper();
}


#endif