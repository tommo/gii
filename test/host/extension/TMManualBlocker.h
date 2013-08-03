#ifndef	TMMANUALBLOCKER_H
#define	TMMANUALBLOCKER_H

#include "pch.h"
#include <moaicore/MOAIAction.h>
#include <moaicore/MOAIActionMgr.h>


class TMManualBlocker:
	public MOAIBlocker
{
private:
	static int _isBlocked( lua_State *L);
	static int _unblock( lua_State *L);
	static int _setBlocker( lua_State *L);
	static int _blockCurrentAction( lua_State *L);
	static int _blockAction( lua_State *L);

public:
	DECL_LUA_FACTORY ( TMManualBlocker )

	TMManualBlocker();
	~TMManualBlocker();

	void			RegisterLuaClass		( MOAILuaState& state );
	void			RegisterLuaFuncs		( MOAILuaState& state );
};


#endif
