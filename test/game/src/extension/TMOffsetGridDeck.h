// Copyright (c) 2010-2011 Zipline Games, Inc. All Rights Reserved.
// http://getmoai.com
#ifndef	TMOFFSETGRIDDECK_H
#define	TMOFFSETGRIDDECK_H

#include "pch.h"
#include <moaicore/MOAIDeckRemapper.h>
#include <moaicore/MOAIGrid.h>
#include <moaicore/MOAILogMessages.h>
#include <moaicore/MOAIProp.h>
#include <moaicore/MOAIQuadBrush.h>
#include <moaicore/MOAITileDeck2D.h>
#include <moaicore/MOAITextureBase.h>
#include <moaicore/MOAITransformBase.h>


class TMOffsetGridDeck :
	public MOAITileDeck2D {
private:
		static int _setYZRatio(lua_State *L);
		float 		mYZRatio;
public:
			DECL_LUA_FACTORY ( TMOffsetGridDeck )
			

			TMOffsetGridDeck();
			~TMOffsetGridDeck();

			void			DrawIndex				( u32 idx, float xOff, float yOff, float zOff, float xScl, float yScl, float zScl );

			void			RegisterLuaClass		( MOAILuaState& state );
			void			RegisterLuaFuncs		( MOAILuaState& state );

};

#endif
