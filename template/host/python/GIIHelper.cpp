#include <MOEIHelper.h>

int MOEIHelper::_stepSim( lua_State *L){
	MOAILuaState state (L);
	if ( !state.CheckParams ( 1, "N" )) return 0;
	double step=state.GetValue<double>(1, 0);
	MOEIHelper::Get().stepSim(step);
	return 0;
}

int MOEIHelper::_setBufferSize( lua_State *L){
	MOAILuaState state (L);
	if ( !state.CheckParams ( 1, "NN" )) return 0;
	u32 width=state.GetValue<u32>(1, 0);
	u32 height=state.GetValue<u32>(2, 0);
	MOAIGfxDevice::Get ().SetBufferSize ( width, height );
	return 0;
}

int MOEIHelper::_renderFrameBuffer( lua_State *L ){
	MOAILuaState state (L);
	if ( !state.CheckParams ( 1, "U" )) return 0;
	MOAIFrameBuffer* frameBuffer = state.GetLuaObject < MOAIFrameBuffer >( 1, false );
	if (frameBuffer) {
		frameBuffer->Render();
	}
	return 0;
}

void MOEIHelper::stepSim( double step ){
	MOAIInputMgr::Get ().Update ();
	MOAIActionMgr::Get ().Update (( float )step );		
	MOAINodeMgr::Get ().Update ();
}


MOEIHelper::MOEIHelper(){
	RTTI_BEGIN
		RTTI_SINGLE(MOAILuaObject)
	RTTI_END
}

MOEIHelper::~MOEIHelper(){}

void MOEIHelper::RegisterLuaClass(MOAILuaState &state){
	luaL_Reg regTable [] = {
		{ "stepSim",             _stepSim },
		{ "setBufferSize",       _setBufferSize },
		{ "renderFrameBuffer",   _renderFrameBuffer },
		{ NULL, NULL }
	};

	luaL_register ( state, 0, regTable );
}

