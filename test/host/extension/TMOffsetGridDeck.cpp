#include <TMOffsetGridDeck.h>
#include <moaicore/MOAILogMgr.h>

void TMOffsetGridDeck::DrawIndex( u32 idx, float xOff, float yOff, float zOff, float xScl, float yScl, float zScl ){
	zOff=zOff+yOff*(25.0/20.0);//*32.0;

	MOAITileDeck2D::DrawIndex(idx,xOff,yOff,zOff,xScl,yScl,zScl);
}


int TMOffsetGridDeck::_setYZRatio(lua_State *L){
	MOAI_LUA_SETUP(TMOffsetGridDeck, "UN")

	self->mYZRatio=state.GetValue <float> (2,1) ;
	return 0;
}

TMOffsetGridDeck::TMOffsetGridDeck():
	mYZRatio(1)
{
	RTTI_BEGIN
		RTTI_EXTEND(MOAITileDeck2D)
	RTTI_END
}

TMOffsetGridDeck::~TMOffsetGridDeck(){

}




void TMOffsetGridDeck::RegisterLuaClass ( MOAILuaState& state ) {
	MOAITileDeck2D::RegisterLuaClass(state);	
}

//----------------------------------------------------------------//
void TMOffsetGridDeck::RegisterLuaFuncs ( MOAILuaState& state ) {
	MOAITileDeck2D::RegisterLuaFuncs(state);
	
	luaL_Reg regTable [] = {
		{ "setYZRatio",				_setYZRatio },
		{ NULL, NULL }
	};

	luaL_register ( state, 0, regTable );
}