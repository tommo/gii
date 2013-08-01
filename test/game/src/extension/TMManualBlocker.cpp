#include <TMManualBlocker.h>

int TMManualBlocker::_unblock(lua_State* L){
	MOAI_LUA_SETUP (TMManualBlocker, "U")
	self->UnblockAll();
	return 0;
}

int TMManualBlocker::_isBlocked(lua_State* L){
	MOAI_LUA_SETUP (TMManualBlocker, "U")
	lua_pushboolean(state, self->IsBlocked());
	return 1;
}

int TMManualBlocker::_blockCurrentAction(lua_State* L){
	MOAI_LUA_SETUP (TMManualBlocker, "U")

	MOAIAction* current = MOAIActionMgr::Get ().GetCurrentAction ();
	if ( !current ) return 0;
	
	current->SetBlocker ( self );
	
	return lua_yield ( state, 0 );
}

int TMManualBlocker::_blockAction(lua_State* L){
	MOAI_LUA_SETUP(TMManualBlocker, "U")
	MOAIAction* blocked = state.GetLuaObject < MOAIAction >( 2, true );
	if ( !blocked ) return 0;
	blocked->SetBlocker(self);
	return 0;
}

int TMManualBlocker::_setBlocker(lua_State* L){
	MOAI_LUA_SETUP(TMManualBlocker, "U")
	MOAIAction* blocker = state.GetLuaObject < MOAIAction >( 2, true );
	if ( !blocker ) return 0;
	self->SetBlocker(blocker);
	return 0;
}

TMManualBlocker::TMManualBlocker(){
	RTTI_BEGIN
		RTTI_EXTEND(TMManualBlocker)
	RTTI_END
}

TMManualBlocker::~TMManualBlocker(){

}

void TMManualBlocker::RegisterLuaFuncs( MOAILuaState& state) {
	luaL_Reg regTable [] = {
		{ "isBlocked",					_isBlocked },
		{ "unblock",						_unblock },
		
		{ "blockAction",				_blockAction },
		{ "blockCurrentAction",	_blockCurrentAction },
		{ "setBlocker",					_setBlocker },

		{ NULL, NULL }
	};
	
	luaL_register ( state, 0, regTable );
}

void TMManualBlocker::RegisterLuaClass( MOAILuaState& state ) {

}

