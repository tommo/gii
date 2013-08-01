// Copyright (c) 2010-2011 Zipline Games, Inc. All Rights Reserved.
// http://getmoai.com
// ORIGINAL: MOAITileDeck2D
// modified for MDD

#ifndef	TMTILEDECK2D_H
#define	TMTILEDECK2D_H

#include <moaicore/MOAIDeck.h>
#include <moaicore/MOAILua.h>

class MOAITextureBase;

//================================================================//
// TMTileDeck2D
//================================================================//
/**	@name	TMTileDeck2D
	@text	Subdivides a single texture into uniform tiles enumerated
			from the texture's left top to right bottom.
*/
class TMTileDeck2D :
	public MOAIDeck,
	public MOAIGridSpace {
private:
	
	// MOAIQuadBrush mQuad;
	USVec2D mUV[4];
	USVec2D mVtx [ 4 ];
	u32     mColorSideWall;

	
	//----------------------------------------------------------------//
	static int		_setRect				( lua_State* L );
	static int		_setUVRect				( lua_State* L );
	static int		_setSize				( lua_State* L );
	static int		_transform				( lua_State* L );
	static int		_transformUV			( lua_State* L );
	
	//----------------------------------------------------------------//
	USBox			ComputeMaxBounds		();
	USBox			GetItemBounds			( u32 idx );

	void				SetVerts			( float x0, float y0, float x1, float y1 );
	void				SetUVs				( float x0, float y0, float x1, float y1 );

public:
	
	DECL_LUA_FACTORY ( TMTileDeck2D )
	
	//----------------------------------------------------------------//
	void			DrawIndex				( u32 idx, float xOff, float yOff, float zOff, float xScl, float yScl, float zScl );
					TMTileDeck2D			();
					~TMTileDeck2D			();
	void			RegisterLuaClass		( MOAILuaState& state );
	void			RegisterLuaFuncs		( MOAILuaState& state );
	void			SerializeIn				( MOAILuaState& state, MOAIDeserializer& serializer );
	void			SerializeOut			( MOAILuaState& state, MOAISerializer& serializer );
	void			Transform				( const USAffine3D& mtx );
	void			TransformUV				( const USAffine3D& mtx );

	void 			DrawFace(u32 idx, float xOff, float yOff, float zOff, float Scl);
	void 			DrawWall(u32 idx, float xOff, float yOff, float zOff, float Scl);
	void 			DrawWallSide(u32 idx, float xOff, float yOff, float zOff, float Scl);
	void 			DrawWallEdgeE(u32 idx, float xOff, float yOff, float zOff, float scl);
	void 			DrawWallEdgeW(u32 idx, float xOff, float yOff, float zOff, float scl);
	void 			DrawWallEdgeN(u32 idx, float xOff, float yOff, float zOff, float scl);
	void 			DrawWallEdgeS(u32 idx, float xOff, float yOff, float zOff, float scl);

	void 			DrawWallPoleNE(u32 idx, float xOff, float yOff, float zOff, float scl, bool inner);
	void 			DrawWallPoleSW(u32 idx, float xOff, float yOff, float zOff, float scl, bool inner);
	void 			DrawWallPoleSE(u32 idx, float xOff, float yOff, float zOff, float scl, bool inner);
	void 			DrawWallPoleNW(u32 idx, float xOff, float yOff, float zOff, float scl, bool inner);

};

#endif
