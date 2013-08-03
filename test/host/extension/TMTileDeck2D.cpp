// Copyright (c) 2010-2011 Zipline Games, Inc. All Rights Reserved.
// http://getmoai.com

#include "pch.h"
#include <moaicore/MOAIDeckRemapper.h>
#include <moaicore/MOAIGrid.h>
#include <moaicore/MOAILogMessages.h>
#include <moaicore/MOAIProp.h>
#include <moaicore/MOAIQuadBrush.h>
#include <TMTileDeck2D.h>
#include <moaicore/MOAITextureBase.h>
#include <moaicore/MOAITransformBase.h>

//----------------------------------------------------------------//
/**	@name	setRect
	@text	Set the model space dimensions of a single tile. When grid drawing, this
			should be a unit rect centered at the origin for tiles that fit each grid
			cell. Growing or shrinking the rect will cause tiles to overlap or leave
			gaps between them.
	
	@in		TMTileDeck2D self
	@in		number xMin
	@in		number yMin
	@in		number xMax
	@in		number yMax
	@out	nil
*/
int TMTileDeck2D::_setRect ( lua_State* L ) {
	MOAI_LUA_SETUP ( TMTileDeck2D, "UNNNN" )
	
	float x0	= state.GetValue < float >( 2, 0.0f );
	float y0	= state.GetValue < float >( 3, 0.0f );
	float x1	= state.GetValue < float >( 4, 0.0f );
	float y1	= state.GetValue < float >( 5, 0.0f );
	
	self->SetVerts(x0,y0,x1,y1);

	self->SetBoundsDirty ();

	return 0;
}

//----------------------------------------------------------------//
/**	@name	setUVRect
	@text	Set the UV space dimensions of the quad.
	
	@in		TMTileDeck2D self
	@in		number xMin
	@in		number yMin
	@in		number xMax
	@in		number yMax
	@out	nil
*/
int TMTileDeck2D::_setUVRect ( lua_State* L ) {
	MOAI_LUA_SETUP ( TMTileDeck2D, "UNNNN" )
	
	float u0	= state.GetValue < float >( 2, 0.0f );
	float v0	= state.GetValue < float >( 3, 0.0f );
	float u1	= state.GetValue < float >( 4, 0.0f );
	float v1	= state.GetValue < float >( 5, 0.0f );
	
	self->SetUVs(u0,v0,u1,v1);
		
	return 0;
}

void TMTileDeck2D::SetVerts ( float x0, float y0, float x1, float y1 ) {
	
	// left top
	this->mVtx [ 0 ].mX = x0;
	this->mVtx [ 0 ].mY = y1;
	
	// right top
	this->mVtx [ 1 ].mX = x1;
	this->mVtx [ 1 ].mY = y1;
	
	// right bottom
	this->mVtx [ 2 ].mX = x1;
	this->mVtx [ 2 ].mY = y0;
	
	// left bottom
	this->mVtx [ 3 ].mX = x0;
	this->mVtx [ 3 ].mY = y0;
}


void TMTileDeck2D::SetUVs( float x0, float y0, float x1, float y1 ) {
	
	// left top
	this->mUV [ 0 ].mX = x0;
	this->mUV [ 0 ].mY = y1;
	
	// right top
	this->mUV [ 1 ].mX = x1;
	this->mUV [ 1 ].mY = y1;
	
	// right bottom
	this->mUV [ 2 ].mX = x1;
	this->mUV [ 2 ].mY = y0;
	
	// left bottom
	this->mUV [ 3 ].mX = x0;
	this->mUV [ 3 ].mY = y0;
}

//----------------------------------------------------------------//
/**	@name	setSize
	@text	Controls how the texture is subdivided into tiles. Default
			behavior is to subdivide the texture into N by M tiles,
			but is tile dimensions are provided (in UV space) then the resulting
			tile set will be N * tileWidth by M * tileHeight in UV
			space. This means the tile set does not have to fill all of the
			texture. The upper left hand corner of the tile set will always be
			at UV 0, 0.
	
	@in		TMTileDeck2D self
	@in		number width			Width of the tile deck in tiles.
	@in		number height			Height of the tile deck in tiles.
	@opt	number cellWidth		Width of individual tile in UV space. Defaults to 1 / width.
	@opt	number cellHeight		Height of individual tile in UV space. Defaults to 1 / height.
	@opt	number xOff				X offset of the tile from the cell. Defaults to 0.
	@opt	number yOff				Y offset of the tile from the cell. Defaults to 0.
	@opt	number tileWidth		Default value is cellWidth.
	@opt	number tileHeight		Default value is cellHeight.
	@out	nil
*/
int	TMTileDeck2D::_setSize ( lua_State* L ) {
	MOAI_LUA_SETUP ( TMTileDeck2D, "UNN" )
	
	u32 width			= state.GetValue < u32 >( 2, 0 );
	u32 height			= state.GetValue < u32 >( 3, 0 );
	
	float cellWidth		= state.GetValue < float >( 4, 1.0f / ( float )width );
	float cellHeight	= state.GetValue < float >( 5, 1.0f / ( float )height );
	
	float xOff			= state.GetValue < float >( 6, 0.0f );
	float yOff			= state.GetValue < float >( 7, 0.0f );
	
	float tileWidth		= state.GetValue < float >( 8, cellWidth );
	float tileHeight	= state.GetValue < float >( 9, cellHeight );
	
	self->SetWidth ( width );
	self->SetHeight ( height );
	
	self->SetCellWidth ( cellWidth );
	self->SetCellHeight ( cellHeight );
	
	self->SetXOff ( xOff );
	self->SetYOff ( yOff );
	
	self->SetTileWidth ( tileWidth );
	self->SetTileHeight ( tileHeight );
	
	return 0;
}

//----------------------------------------------------------------//
/**	@name	transform
	@text	Apply the given MOAITransform to all the vertices in the deck.
	
	@in		TMTileDeck2D self
	@in		MOAITransform transform
	@out	nil
*/
int TMTileDeck2D::_transform ( lua_State* L ) {
	MOAI_LUA_SETUP ( TMTileDeck2D, "UU" )
	
	MOAITransform* transform = state.GetLuaObject < MOAITransform >( 2, true );
	if ( transform ) {
		transform->ForceUpdate ();
		self->Transform ( transform->GetLocalToWorldMtx ());
		self->SetBoundsDirty ();
	}
	return 0;
}

//----------------------------------------------------------------//
/**	@name	transformUV
	@text	Apply the given MOAITransform to all the uv coordinates in the deck.
	
	@in		TMTileDeck2D self
	@in		MOAITransform transform
	@out	nil
*/
int TMTileDeck2D::_transformUV ( lua_State* L ) {
	MOAI_LUA_SETUP ( TMTileDeck2D, "UU" )
	
	MOAITransform* transform = state.GetLuaObject < MOAITransform >( 2, true );
	if ( transform ) {
		transform->ForceUpdate ();
		self->TransformUV ( transform->GetLocalToWorldMtx ());
	}
	return 0;
}

//================================================================//
// TMTileDeck2D
//================================================================//

//----------------------------------------------------------------//
USBox TMTileDeck2D::ComputeMaxBounds () {
	return this->GetItemBounds ( 0 );
}

//Vertex format already set in Prop
void TMTileDeck2D::DrawFace(u32 idx, float xOff, float yOff, float zOff, float scl){
	idx = idx - 1;
	
	MOAICellCoord coord = this->GetCellCoord ( idx );
	USRect uvRect = this->GetTileRect ( coord );
	
	float uScale = ( uvRect.mXMax - uvRect.mXMin );
	float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	float uOff = uvRect.mXMin + ( 0.5f * uScale );
	float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();
	gfxDevice.BeginPrim ( GL_TRIANGLE_STRIP );
	
		//left-top
		gfxDevice.WriteVtx ( mVtx[0].mX * scl + xOff, mVtx[0].mY * scl + yOff, zOff );
		gfxDevice.WriteUV(mUV[0].mX*uScale+uOff, mUV[0].mY*vScale+vOff);
		gfxDevice.WriteFinalColor4b ();
		
		//right-top
		gfxDevice.WriteVtx ( mVtx[1].mX * scl + xOff, mVtx[1].mY * scl + yOff, zOff );
		gfxDevice.WriteUV(mUV[1].mX*uScale+uOff, mUV[1].mY*vScale+vOff);
		gfxDevice.WriteFinalColor4b ();

		//left-bottom
		gfxDevice.WriteVtx ( mVtx[3].mX * scl + xOff, mVtx[3].mY * scl + yOff, zOff );
		gfxDevice.WriteUV(mUV[3].mX*uScale+uOff, mUV[3].mY*vScale+vOff);
		gfxDevice.WriteFinalColor4b ();

		//right-bottom
		gfxDevice.WriteVtx ( mVtx[2].mX * scl + xOff, mVtx[2].mY * scl + yOff, zOff );
		gfxDevice.WriteUV(mUV[2].mX*uScale+uOff, mUV[2].mY*vScale+vOff);
		gfxDevice.WriteFinalColor4b ();

	gfxDevice.EndPrim ();
}

void TMTileDeck2D::DrawWall(u32 idx, float xOff, float yOff, float zOff, float scl){
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();
	idx = idx - 1;
	
	MOAICellCoord coord = this->GetCellCoord ( idx );
	USRect uvRect = this->GetTileRect ( coord );
	
	float uScale = ( uvRect.mXMax - uvRect.mXMin );
	float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	float uOff = uvRect.mXMin + ( 0.5f * uScale );
	float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	gfxDevice.BeginPrim ( GL_TRIANGLE_STRIP );
	
		//left-top
		gfxDevice.WriteVtx ( mVtx[0].mX * scl + xOff, yOff, mVtx[0].mY * scl + zOff );
		gfxDevice.WriteUV(mUV[0].mX*uScale+uOff, -mUV[0].mY*vScale+vOff);
		gfxDevice.WriteFinalColor4b ();
		
		//right-top
		gfxDevice.WriteVtx ( mVtx[1].mX * scl + xOff, yOff, mVtx[1].mY * scl + zOff );
		gfxDevice.WriteUV(mUV[1].mX*uScale+uOff, -mUV[1].mY*vScale+vOff);
		gfxDevice.WriteFinalColor4b ();

		//left-bottom
		gfxDevice.WriteVtx ( mVtx[3].mX * scl + xOff, yOff, mVtx[3].mY * scl + zOff );
		gfxDevice.WriteUV(mUV[3].mX*uScale+uOff, -mUV[3].mY*vScale+vOff);
		gfxDevice.WriteFinalColor4b ();

		//right-bottom
		gfxDevice.WriteVtx ( mVtx[2].mX * scl + xOff, yOff, mVtx[2].mY * scl + zOff );
		gfxDevice.WriteUV(mUV[2].mX*uScale+uOff, -mUV[2].mY*vScale+vOff);
		gfxDevice.WriteFinalColor4b ();

	gfxDevice.EndPrim ();
}


void TMTileDeck2D::DrawWallSide(u32 idx, float xOff, float yOff, float zOff, float scl){
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();
	idx = idx - 1;
	
	MOAICellCoord coord = this->GetCellCoord ( idx );
	USRect uvRect = this->GetTileRect ( coord );
	
	float uScale = ( uvRect.mXMax - uvRect.mXMin );
	float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	float uOff = uvRect.mXMin + ( 0.5f * uScale );
	float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	gfxDevice.BeginPrim ( GL_TRIANGLE_STRIP );
	
		//left-top
		gfxDevice.WriteVtx ( xOff, mVtx[0].mX * scl + yOff, mVtx[0].mY * scl + zOff );
		gfxDevice.WriteUV(mUV[0].mX*uScale+uOff, -mUV[0].mY*vScale+vOff);
		gfxDevice.Write<u32>( this->mColorSideWall );
		
		//right-top
		gfxDevice.WriteVtx ( xOff, mVtx[1].mX * scl + yOff, mVtx[1].mY * scl + zOff );
		gfxDevice.WriteUV(mUV[1].mX*uScale+uOff, -mUV[1].mY*vScale+vOff);
		gfxDevice.Write<u32>( this->mColorSideWall );

		//left-bottom
		gfxDevice.WriteVtx ( xOff, mVtx[3].mX * scl + yOff, mVtx[3].mY * scl + zOff );
		gfxDevice.WriteUV(mUV[3].mX*uScale+uOff, -mUV[3].mY*vScale+vOff);
		gfxDevice.Write<u32>( this->mColorSideWall );

		//right-bottom
		gfxDevice.WriteVtx ( xOff, mVtx[2].mX * scl + yOff, mVtx[2].mY * scl + zOff );
		gfxDevice.WriteUV(mUV[2].mX*uScale+uOff, -mUV[2].mY*vScale+vOff);
		gfxDevice.Write<u32>( this->mColorSideWall );

	gfxDevice.EndPrim ();
}

// REALLY DIRTY CODES!!!!!!!!!!!
// May never rewrite this...
void TMTileDeck2D::DrawWallEdgeN(u32 idx, float xOff, float yOff, float zOff, float scl){
	idx = idx - 1;
	
	MOAICellCoord coord = this->GetCellCoord ( idx );
	USRect uvRect = this->GetTileRect ( coord );
	
	float uScale = ( uvRect.mXMax - uvRect.mXMin );
	float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	float uOff = uvRect.mXMin + ( 0.5f * uScale );
	float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();

		
	float x0=mVtx[0].mX * scl, y0=mVtx[0].mY * scl;
	float x1=mVtx[1].mX * scl, y1=mVtx[1].mY * scl;
	float x3=mVtx[3].mX * scl, y3=mVtx[3].mY * scl;
	float x2=mVtx[2].mX * scl, y2=mVtx[2].mY * scl;

	float u0=mUV[0].mX * uScale, v0=mUV[0].mY * vScale;
	float u1=mUV[1].mX * uScale, v1=mUV[1].mY * vScale;
	float u3=mUV[3].mX * uScale, v3=mUV[3].mY * vScale;
	float u2=mUV[2].mX * uScale, v2=mUV[2].mY * vScale;

	gfxDevice.BeginPrim ( GL_TRIANGLE_STRIP );

		//left-top
		gfxDevice.WriteVtx ( x0 + xOff, y0 + yOff, zOff );
		gfxDevice.WriteUV ( u0+uOff, v0+vOff );
		gfxDevice.WriteFinalColor4b ();
		
		//right-top
		gfxDevice.WriteVtx ( x1 + xOff, y1 + yOff, zOff );
		gfxDevice.WriteUV ( u1+uOff, v1+vOff );
		gfxDevice.WriteFinalColor4b ();

		//left-bottom
		gfxDevice.WriteVtx ( x3 + xOff, 0 + yOff, zOff );
		gfxDevice.WriteUV ( u3+uOff, 0+vOff );
		gfxDevice.WriteFinalColor4b ();

		//right-bottom
		gfxDevice.WriteVtx ( x2 + xOff, 0 + yOff, zOff );
		gfxDevice.WriteUV ( u2+uOff, 0+vOff );
		gfxDevice.WriteFinalColor4b ();

	gfxDevice.EndPrim ();
}

void TMTileDeck2D::DrawWallEdgeS(u32 idx, float xOff, float yOff, float zOff, float scl){
	idx = idx - 1;
	
	MOAICellCoord coord = this->GetCellCoord ( idx );
	USRect uvRect = this->GetTileRect ( coord );
	
	float uScale = ( uvRect.mXMax - uvRect.mXMin );
	float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	float uOff = uvRect.mXMin + ( 0.5f * uScale );
	float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();

		
	float x0=mVtx[0].mX * scl, y0=mVtx[0].mY * scl;
	float x1=mVtx[1].mX * scl, y1=mVtx[1].mY * scl;
	float x3=mVtx[3].mX * scl, y3=mVtx[3].mY * scl;
	float x2=mVtx[2].mX * scl, y2=mVtx[2].mY * scl;

	float u0=mUV[0].mX * uScale, v0=mUV[0].mY * vScale;
	float u1=mUV[1].mX * uScale, v1=mUV[1].mY * vScale;
	float u3=mUV[3].mX * uScale, v3=mUV[3].mY * vScale;
	float u2=mUV[2].mX * uScale, v2=mUV[2].mY * vScale;

	gfxDevice.BeginPrim ( GL_TRIANGLE_STRIP );

		//left-top
		gfxDevice.WriteVtx ( x0 + xOff, 0 + yOff, zOff );
		gfxDevice.WriteUV ( u0+uOff, 0+vOff );
		gfxDevice.WriteFinalColor4b ();
		
		//right-top
		gfxDevice.WriteVtx ( x1 + xOff, 0 + yOff, zOff );
		gfxDevice.WriteUV ( u1+uOff, 0+vOff );
		gfxDevice.WriteFinalColor4b ();

		//left-bottom
		gfxDevice.WriteVtx ( x3 + xOff, y3 + yOff, zOff );
		gfxDevice.WriteUV ( u3+uOff, -v3+vOff );
		gfxDevice.WriteFinalColor4b ();

		//right-bottom
		gfxDevice.WriteVtx ( x2 + xOff, y2 + yOff, zOff );
		gfxDevice.WriteUV ( u2+uOff, -v2+vOff );
		gfxDevice.WriteFinalColor4b ();

	gfxDevice.EndPrim ();
}

void TMTileDeck2D::DrawWallEdgeE(u32 idx, float xOff, float yOff, float zOff, float scl){
	idx = idx - 1;
	
	MOAICellCoord coord = this->GetCellCoord ( idx );
	USRect uvRect = this->GetTileRect ( coord );
	
	float uScale = ( uvRect.mXMax - uvRect.mXMin );
	float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	float uOff = uvRect.mXMin + ( 0.5f * uScale );
	float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();

		
	float x0=mVtx[0].mX * scl, y0=mVtx[0].mY * scl;
	float x1=mVtx[1].mX * scl, y1=mVtx[1].mY * scl;
	float x3=mVtx[3].mX * scl, y3=mVtx[3].mY * scl;
	float x2=mVtx[2].mX * scl, y2=mVtx[2].mY * scl;

	float u0=mUV[0].mX * uScale, v0=mUV[0].mY * vScale;
	float u1=mUV[1].mX * uScale, v1=mUV[1].mY * vScale;
	float u3=mUV[3].mX * uScale, v3=mUV[3].mY * vScale;
	float u2=mUV[2].mX * uScale, v2=mUV[2].mY * vScale;

	gfxDevice.BeginPrim ( GL_TRIANGLE_STRIP );

		//left-top
		gfxDevice.WriteVtx ( 0 + xOff, y1 + yOff, zOff );
		gfxDevice.WriteUV ( u0+uOff, 0+vOff );
		gfxDevice.WriteFinalColor4b ();
		
		//right-top
		gfxDevice.WriteVtx ( x1 + xOff, y1 + yOff, zOff );
		gfxDevice.WriteUV ( u0+uOff, v0+vOff );
		gfxDevice.WriteFinalColor4b ();

		//left-bottom
		gfxDevice.WriteVtx ( 0 + xOff, y3 + yOff, zOff );
		gfxDevice.WriteUV ( u1+uOff, 0+vOff );
		gfxDevice.WriteFinalColor4b ();

		//right-bottom
		gfxDevice.WriteVtx ( x2 + xOff, y2 + yOff, zOff );
		gfxDevice.WriteUV ( u1+uOff, v1+vOff );
		gfxDevice.WriteFinalColor4b ();

	gfxDevice.EndPrim ();
}

void TMTileDeck2D::DrawWallEdgeW(u32 idx, float xOff, float yOff, float zOff, float scl){
	idx = idx - 1;
	
	MOAICellCoord coord = this->GetCellCoord ( idx );
	USRect uvRect = this->GetTileRect ( coord );
	
	float uScale = ( uvRect.mXMax - uvRect.mXMin );
	float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	float uOff = uvRect.mXMin + ( 0.5f * uScale );
	float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();

		
	float x0=mVtx[0].mX * scl, y0=mVtx[0].mY * scl;
	float x1=mVtx[1].mX * scl, y1=mVtx[1].mY * scl;
	float x3=mVtx[3].mX * scl, y3=mVtx[3].mY * scl;
	float x2=mVtx[2].mX * scl, y2=mVtx[2].mY * scl;

	float u0=mUV[0].mX * uScale, v0=mUV[0].mY * vScale;
	float u1=mUV[1].mX * uScale, v1=mUV[1].mY * vScale;
	float u3=mUV[3].mX * uScale, v3=mUV[3].mY * vScale;
	float u2=mUV[2].mX * uScale, v2=mUV[2].mY * vScale;

	gfxDevice.BeginPrim ( GL_TRIANGLE_STRIP );

		//left-top
		gfxDevice.WriteVtx ( x0 + xOff, y0 + yOff, zOff );
		gfxDevice.WriteUV ( u1+uOff, v1+vOff );
		gfxDevice.WriteFinalColor4b ();
		
		//right-top
		gfxDevice.WriteVtx ( 0 + xOff, y1 + yOff, zOff );
		gfxDevice.WriteUV ( u1+uOff, 0+vOff );
		gfxDevice.WriteFinalColor4b ();

		//left-bottom
		gfxDevice.WriteVtx ( x3 + xOff, y3 + yOff, zOff );
		gfxDevice.WriteUV ( u0+uOff, v0+vOff );
		gfxDevice.WriteFinalColor4b ();

		//right-bottom
		gfxDevice.WriteVtx ( 0 + xOff, y2 + yOff, zOff );
		gfxDevice.WriteUV ( u0+uOff, 0+vOff );
		gfxDevice.WriteFinalColor4b ();

	gfxDevice.EndPrim ();
}


void TMTileDeck2D::DrawWallPoleSW(u32 idx, float xOff, float yOff, float zOff, float scl, bool inner){
	idx = idx - 1;
	
	MOAICellCoord coord = this->GetCellCoord ( idx );
	USRect uvRect = this->GetTileRect ( coord );
	
	float uScale = ( uvRect.mXMax - uvRect.mXMin );
	float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	float uOff = uvRect.mXMin + ( 0.5f * uScale );
	float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();

		
	float x0=mVtx[0].mX * scl, 	y0=0;
	float x1=0, 								y1=0;
	float x2=0, 								y2=mVtx[2].mY * scl;
	float x3=mVtx[3].mX * scl, 	y3=mVtx[3].mY * scl;

	float u0=mUV[0].mX * uScale, 	v0=0;
	float u1=0, 									v1=0;
	float u2=0, 									v2=mUV[2].mY * vScale;
	float u3=mUV[3].mX * uScale, 	v3=mUV[3].mY * vScale;

	if(inner){
		u0+=uScale*0.5;
		u1+=uScale*0.5;
		u2+=uScale*0.5;
		u3+=uScale*0.5;
	}

	gfxDevice.BeginPrim ( GL_TRIANGLE_STRIP );

		//left-top
		gfxDevice.WriteVtx ( x0 + xOff, y0 + yOff, zOff );
		gfxDevice.WriteUV ( u0+uOff, v0+vOff );
		gfxDevice.WriteFinalColor4b ();
		
		//right-top
		gfxDevice.WriteVtx ( x1 + xOff, y1 + yOff, zOff );
		gfxDevice.WriteUV ( u1+uOff, v1+vOff );
		gfxDevice.WriteFinalColor4b ();

		//left-bottom
		gfxDevice.WriteVtx ( x3 + xOff, y3 + yOff, zOff );
		gfxDevice.WriteUV ( u3+uOff, v3+vOff );
		gfxDevice.WriteFinalColor4b ();

		//right-bottom
		gfxDevice.WriteVtx ( x2 + xOff, y2 + yOff, zOff );
		gfxDevice.WriteUV ( u2+uOff, v2+vOff );
		gfxDevice.WriteFinalColor4b ();

	gfxDevice.EndPrim ();
}


void TMTileDeck2D::DrawWallPoleNE(u32 idx, float xOff, float yOff, float zOff, float scl, bool inner){
	idx = idx - 1;
	
	MOAICellCoord coord = this->GetCellCoord ( idx );
	USRect uvRect = this->GetTileRect ( coord );
	
	float uScale = ( uvRect.mXMax - uvRect.mXMin );
	float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	float uOff = uvRect.mXMin + ( 0.5f * uScale );
	float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();

		
	float x0=0, 								y0=mVtx[0].mY * scl;
	float x1=mVtx[1].mX * scl,	y1=mVtx[1].mY * scl;
	float x2=mVtx[2].mX * scl,	y2=0;
	float x3=0, 								y3=0;

	float u0=mUV[0].mX * uScale, 	v0=0;
	float u1=0, 									v1=0;
	float u2=0, 									v2=mUV[2].mY * vScale;
	float u3=mUV[3].mX * uScale, 	v3=mUV[3].mY * vScale;

	if(inner){
		u0+=uScale*0.5;
		u1+=uScale*0.5;
		u2+=uScale*0.5;
		u3+=uScale*0.5;
	}

	gfxDevice.BeginPrim ( GL_TRIANGLE_STRIP );

		//left-top
		gfxDevice.WriteVtx ( x0 + xOff, y0 + yOff, zOff );
		gfxDevice.WriteUV ( u2+uOff, v2+vOff );
		gfxDevice.WriteFinalColor4b ();
		
		//right-top
		gfxDevice.WriteVtx ( x1 + xOff, y1 + yOff, zOff );
		gfxDevice.WriteUV ( u3+uOff, v3+vOff );
		gfxDevice.WriteFinalColor4b ();

		//left-bottom
		gfxDevice.WriteVtx ( x3 + xOff, y3 + yOff, zOff );
		gfxDevice.WriteUV ( u1+uOff, v1+vOff );
		gfxDevice.WriteFinalColor4b ();

		//right-bottom
		gfxDevice.WriteVtx ( x2 + xOff, y2 + yOff, zOff );
		gfxDevice.WriteUV ( u0+uOff, v0+vOff );
		gfxDevice.WriteFinalColor4b ();

	gfxDevice.EndPrim ();
}

void TMTileDeck2D::DrawWallPoleSE(u32 idx, float xOff, float yOff, float zOff, float scl, bool inner){
	idx = idx - 1;
	
	MOAICellCoord coord = this->GetCellCoord ( idx );
	USRect uvRect = this->GetTileRect ( coord );
	
	float uScale = ( uvRect.mXMax - uvRect.mXMin );
	float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	float uOff = uvRect.mXMin + ( 0.5f * uScale );
	float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();

		
	float x0=0,									y0=0;
	float x1=mVtx[1].mX * scl,	y1=0;
	float x2=mVtx[2].mX * scl,	y2=mVtx[2].mY * scl;
	float x3=0,									y3=mVtx[3].mY * scl;

	float u0=mUV[0].mX * uScale, 	v0=0;
	float u1=0, 									v1=0;
	float u2=0, 									v2=mUV[2].mY * vScale;
	float u3=mUV[3].mX * uScale, 	v3=mUV[3].mY * vScale;

	if(inner){
		u0+=uScale*0.5;
		u1+=uScale*0.5;
		u2+=uScale*0.5;
		u3+=uScale*0.5;
	}

	gfxDevice.BeginPrim ( GL_TRIANGLE_STRIP );

		//left-top
		gfxDevice.WriteVtx ( x0 + xOff, y0 + yOff, zOff );
		gfxDevice.WriteUV ( u1+uOff, v1+vOff );
		gfxDevice.WriteFinalColor4b ();
		
		//right-top
		gfxDevice.WriteVtx ( x1 + xOff, y1 + yOff, zOff );
		gfxDevice.WriteUV ( u0+uOff, v0+vOff );
		gfxDevice.WriteFinalColor4b ();

		//left-bottom
		gfxDevice.WriteVtx ( x3 + xOff, y3 + yOff, zOff );
		gfxDevice.WriteUV ( u2+uOff, v2+vOff );
		gfxDevice.WriteFinalColor4b ();

		//right-bottom
		gfxDevice.WriteVtx ( x2 + xOff, y2 + yOff, zOff );
		gfxDevice.WriteUV ( u3+uOff, v3+vOff );
		gfxDevice.WriteFinalColor4b ();

	gfxDevice.EndPrim ();
}

void TMTileDeck2D::DrawWallPoleNW(u32 idx, float xOff, float yOff, float zOff, float scl, bool inner){
	idx = idx - 1;
	
	MOAICellCoord coord = this->GetCellCoord ( idx );
	USRect uvRect = this->GetTileRect ( coord );
	
	float uScale = ( uvRect.mXMax - uvRect.mXMin );
	float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	float uOff = uvRect.mXMin + ( 0.5f * uScale );
	float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();

		
	float x0=mVtx[0].mX * scl,	y0=mVtx[0].mY * scl;
	float x1=0,									y1=mVtx[1].mY * scl;
	float x2=0,									y2=0;
	float x3=mVtx[3].mX * scl,	y3=0;

	float u0=mUV[0].mX * uScale, 	v0=0;
	float u1=0, 									v1=0;
	float u2=0, 									v2=mUV[2].mY * vScale;
	float u3=mUV[3].mX * uScale, 	v3=mUV[3].mY * vScale;

	if(inner){
		u0+=uScale*0.5;
		u1+=uScale*0.5;
		u2+=uScale*0.5;
		u3+=uScale*0.5;
	}

	gfxDevice.BeginPrim ( GL_TRIANGLE_STRIP );

		//left-top
		gfxDevice.WriteVtx ( x0 + xOff, y0 + yOff, zOff );
		gfxDevice.WriteUV ( u3+uOff, v3+vOff );
		gfxDevice.WriteFinalColor4b ();
		
		//right-top
		gfxDevice.WriteVtx ( x1 + xOff, y1 + yOff, zOff );
		gfxDevice.WriteUV ( u2+uOff, v2+vOff );
		gfxDevice.WriteFinalColor4b ();

		//left-bottom
		gfxDevice.WriteVtx ( x3 + xOff, y3 + yOff, zOff );
		gfxDevice.WriteUV ( u0+uOff, v0+vOff );
		gfxDevice.WriteFinalColor4b ();

		//right-bottom
		gfxDevice.WriteVtx ( x2 + xOff, y2 + yOff, zOff );
		gfxDevice.WriteUV ( u1+uOff, v1+vOff );
		gfxDevice.WriteFinalColor4b ();

	gfxDevice.EndPrim ();
}

// void TMTileDeck2D::DrawWall

//----------------------------------------------------------------//
void TMTileDeck2D::DrawIndex ( u32 idx, float xOff, float yOff, float zOff, float xScl, float yScl, float zScl ) {
	UNUSED ( zScl );
	UNUSED ( yScl );

	DrawFace(idx,xOff,yOff,zOff,xScl);
	return;
	
	// MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();
	// MOAIQuadBrush::BindVertexFormat ( gfxDevice );
	
	// gfxDevice.SetVertexMtxMode ( MOAIGfxDevice::VTX_STAGE_MODEL, MOAIGfxDevice::VTX_STAGE_PROJ );
	// gfxDevice.SetUVMtxMode ( MOAIGfxDevice::UV_STAGE_MODEL, MOAIGfxDevice::UV_STAGE_TEXTURE );
	
	// idx = idx - 1;
	
	// MOAICellCoord coord = this->GetCellCoord ( idx );
	// USRect uvRect = this->GetTileRect ( coord );
	
	// float uScale = ( uvRect.mXMax - uvRect.mXMin );
	// float vScale = -( uvRect.mYMax - uvRect.mYMin );
	
	// float uOff = uvRect.mXMin + ( 0.5f * uScale );
	// float vOff = uvRect.mYMin - ( 0.5f * vScale );
	
	// this->mQuad.Draw ( xOff, yOff, zOff, xScl, yScl, uOff, vOff, uScale, vScale );
}

//----------------------------------------------------------------//
USBox TMTileDeck2D::GetItemBounds ( u32 idx ) {
	UNUSED ( idx );
	USBox bounds;

	USRect rect;
	rect.Init ( this->mVtx [ 0 ]);
	rect.Grow ( this->mVtx [ 1 ]);
	rect.Grow ( this->mVtx [ 2 ]);
	rect.Grow ( this->mVtx [ 3 ]);
	bounds.Init ( rect.mXMin, rect.mYMax, rect.mXMax, rect.mYMin, 0.0f, 0.0f );	
	return bounds;
}

//----------------------------------------------------------------//
TMTileDeck2D::TMTileDeck2D () {
	
	RTTI_BEGIN
		RTTI_EXTEND ( MOAIDeck )
		RTTI_EXTEND ( MOAIGridSpace )
	RTTI_END
	
	this->SetContentMask ( MOAIProp::CAN_DRAW );
	this->SetVerts ( -0.5f, -0.5f, 0.5f, 0.5f );
	this->SetUVs ( -0.5f, -0.5f, 0.5f, 0.5f );
	this->mColorSideWall = USColor::PackRGBA( 0.7f, 0.7f, 0.7f, 1.0f );
}

//----------------------------------------------------------------//
TMTileDeck2D::~TMTileDeck2D () {

	this->mTexture.Set ( *this, 0 );
}

//----------------------------------------------------------------//
void TMTileDeck2D::RegisterLuaClass ( MOAILuaState& state ) {

	MOAIDeck::RegisterLuaClass ( state );
	MOAIGridSpace::RegisterLuaClass ( state );
}

//----------------------------------------------------------------//
void TMTileDeck2D::RegisterLuaFuncs ( MOAILuaState& state ) {

	MOAIDeck::RegisterLuaFuncs ( state );
	MOAIGridSpace::RegisterLuaFuncs ( state );

	luaL_Reg regTable [] = {
		{ "setRect",			_setRect },
		{ "setUVRect",			_setUVRect },
		{ "setSize",			_setSize },
		{ "transform",			_transform },
		{ "transformUV",		_transformUV },
		{ NULL, NULL }
	};

	luaL_register ( state, 0, regTable );
}

//----------------------------------------------------------------//
void TMTileDeck2D::SerializeIn ( MOAILuaState& state, MOAIDeserializer& serializer ) {

	MOAIGridSpace::SerializeIn ( state, serializer );
	
	this->mTexture.Set ( *this, serializer.MemberIDToObject < MOAITextureBase >( state.GetField < uintptr >( -1, "mTexture", 0 )));
}

//----------------------------------------------------------------//
void TMTileDeck2D::SerializeOut ( MOAILuaState& state, MOAISerializer& serializer ) {

	MOAIGridSpace::SerializeOut ( state, serializer );
	
	state.SetField ( -1, "mTexture", serializer.AffirmMemberID ( this->mTexture ));
}

//----------------------------------------------------------------//
void TMTileDeck2D::Transform ( const USAffine3D& mtx ) {

	mtx.Transform ( this->mVtx [ 0 ]);
	mtx.Transform ( this->mVtx [ 1 ]);
	mtx.Transform ( this->mVtx [ 2 ]);
	mtx.Transform ( this->mVtx [ 3 ]);
}

//----------------------------------------------------------------//
void TMTileDeck2D::TransformUV ( const USAffine3D& mtx ) {
	mtx.Transform ( this->mUV [ 0 ]);
	mtx.Transform ( this->mUV [ 1 ]);
	mtx.Transform ( this->mUV [ 2 ]);
	mtx.Transform ( this->mUV [ 3 ]);
}