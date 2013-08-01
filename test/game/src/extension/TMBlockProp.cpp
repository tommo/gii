#include <TMBlockProp.h>
#include <TMTileDeck2D.h>
#include <moaicore/MOAIVertexFormatMgr.h>
#define DRAW_SHADOW
#define OFFSET_RATIO 1.0f

int TMBlockProp::_registerBrush(lua_State* L){
	MOAI_LUA_SETUP(TMBlockProp, "UNNN");
	u32 id       = state.GetValue<u32>(2,1);
	int height   = state.GetValue<int>(3,2);
	u32 face     = state.GetValue<u32>(4,0);
	u32 wall1    = state.GetValue<u32>(5,0);
	u32 wall2    = state.GetValue<u32>(6,0);
	u32 wallEdge = state.GetValue<u32>(7,0);

	TMBlockBrush* brush = self->getBrush( id );
	brush->height   = height;
	brush->face     = face;
	brush->wall1    = wall1;
	brush->wall2    = wall2;
	brush->wallEdge = wallEdge;

	return 0;
}

TMBlockBrush* TMBlockProp::getBrush(u32 id){
	return &mBrushes[id];
}

void TMBlockProp::Draw( int subPrimID) {
	/*
		render passes:
		1. draw face at height
		2. draw wall
		3. draw walledge
	*/
	if ( !( this->mFlags & FLAGS_VISIBLE )) return;

	MOAIGrid* grid=this->mGrid;
	MOAIDeck* _d=this->mDeck;
	
	TMTileDeck2D *deck=static_cast<TMTileDeck2D *>(_d);

	if ( !grid ) return;
	if ( !deck) return;

	this->LoadGfxState ();
	
	MOAIGfxDevice& gfxDevice = MOAIGfxDevice::Get ();

	if ( this->mUVTransform ) {
		USAffine3D uvMtx = this->mUVTransform->GetLocalToWorldMtx ();
		gfxDevice.SetUVTransform ( uvMtx );
	}
	else {
		gfxDevice.SetUVTransform ();
	}
	
	if ( this->mFlags & FLAGS_BILLBOARD ) {
		USAffine3D billboardMtx;	
		billboardMtx.Init ( gfxDevice.GetBillboardMtx ());
		billboardMtx = this->GetBillboardMtx ( billboardMtx );
		gfxDevice.SetVertexTransform ( MOAIGfxDevice::VTX_WORLD_TRANSFORM, billboardMtx );
	}
	else {
		gfxDevice.SetVertexTransform ( MOAIGfxDevice::VTX_WORLD_TRANSFORM, this->GetLocalToWorldMtx ());
	}
	
	float blockSize = grid->GetTileWidth ();

	MOAICellCoord c0;
	MOAICellCoord c1;
	
	this->GetGridBoundsInView ( c0, c1 );
	
	gfxDevice.SetVertexPreset ( MOAIVertexFormatMgr::XYZWUVC );

	gfxDevice.SetVertexMtxMode ( MOAIGfxDevice::VTX_STAGE_MODEL, MOAIGfxDevice::VTX_STAGE_PROJ );
	gfxDevice.SetUVMtxMode ( MOAIGfxDevice::UV_STAGE_MODEL, MOAIGfxDevice::UV_STAGE_TEXTURE );
	
	MOAIDeckRemapper * remapper = this->mRemapper;

	
	u32 gridWidth=grid->GetWidth();
	u32 gridHeight=grid->GetHeight();

	if( gridHeight > (c1.mY+2)) c1.mY+=2; //workaround: avoid culling problem

	// DRAW FACE
	for ( int x = c0.mX; x <= c1.mX; ++x ) {
		for ( int y = c1.mY; y >= c0.mY; --y ) {
			
			MOAICellCoord wrap = grid->WrapCellCoord ( x, y );			
			u32 idx=grid->GetTile(x,y);
			if(idx==0) continue;

			TMBlockBrush* brush=getBrush(idx);

			MOAICellCoord coord ( x, y );
			USVec2D loc = grid->GetTilePoint ( coord, MOAIGridSpace::TILE_CENTER );
			int height= brush->height;

			float zOff= (4.0f-(float)height)/2.0f * blockSize;
			deck->DrawFace(brush->face, loc.mX, loc.mY, zOff , blockSize );
			if(height>=4)	continue;
				//NORTH
			if( y+1 < gridHeight ) {
				TMBlockBrush* brushN=getBrush(grid->GetTile(x,y+1));
				int heightN=brushN->height;
				//todo: draw half wall
				if(height < heightN){
					if(heightN>2){//upper wall
						deck->DrawWall(brush->wall1, loc.mX, loc.mY + blockSize/2, blockSize/2-0.01, blockSize );
					}
					if(height<=2){ //lower wall
						deck->DrawWall(brush->wall2, loc.mX, loc.mY + blockSize/2, blockSize*1.5-0.01, blockSize );
					}
				}//end of wall
			}
			//end of NORTH
		}
	}//end of face pass

	//DRAW WALLEDGE
	for ( int x = c0.mX; x <= c1.mX; ++x ) {
		for ( int y = c1.mY; y >= c0.mY; --y ) {
			
			MOAICellCoord wrap = grid->WrapCellCoord ( x, y );
			TMBlockBrush* brush=getBrush(grid->GetTile(x,y));

			u32 height=brush->height;

			MOAICellCoord coord ( x, y );
			USVec2D loc = grid->GetTilePoint ( coord, MOAIGridSpace::TILE_CENTER );
			
			if(height==0) continue;

			TMBlockBrush* bn=0;
			TMBlockBrush* bw=0;
			TMBlockBrush* be=0;
			TMBlockBrush* bs=0;


			float zOff= (4.0f-(float)height)/2.0f * blockSize;

			//WEST
			if(x>0){
				bw=getBrush(grid->GetTile(x-1,y));
				if(bw->height < height){
					deck->DrawWallSide(bw->wall1, loc.mX - blockSize/2 , loc.mY, blockSize/2-0.01, blockSize );
					deck->DrawWallEdgeW(bw->wallEdge, loc.mX, loc.mY, zOff-0.01 * OFFSET_RATIO, blockSize);
				}
			}//end of WEST
			
			//East
			if(x+1<gridWidth){
				be=getBrush(grid->GetTile(x+1,y));
				if(be->height < height){
					deck->DrawWallSide(be->wall1, loc.mX + blockSize/2 , loc.mY, blockSize/2-0.01, blockSize );
					deck->DrawWallEdgeE(be->wallEdge, loc.mX, loc.mY, zOff-0.01 * OFFSET_RATIO, blockSize);
				}
			}//end of East

			//North
			if(y+1<gridHeight){
				bn=getBrush(grid->GetTile(x,y+1));
				if(bn->height < height){
					deck->DrawWallEdgeN(bn->wallEdge, loc.mX, loc.mY, zOff-0.02 * OFFSET_RATIO, blockSize);
				}
				if(be){ //ne
					int f=(be->height < height) + (bn->height < height);
					if(f==2){
						deck->DrawWallPoleNE(bn->wallEdge, loc.mX, loc.mY, zOff-0.03 * OFFSET_RATIO, blockSize, false);
					}else if(f==0){
						TMBlockBrush *bne=getBrush(grid->GetTile(x+1,y+1));
						if(bne->height<height)
							deck->DrawWallPoleNE(bne->wallEdge, loc.mX, loc.mY, zOff-0.03 * OFFSET_RATIO, blockSize, true);
					}
				}
				if(bw){ //nw
					int f=(bw->height < height) + (bn->height < height);
					if(f==2){
						deck->DrawWallPoleNW(bn->wallEdge, loc.mX, loc.mY, zOff-0.03 * OFFSET_RATIO, blockSize, false);
					}else if(f==0){
						TMBlockBrush *bnw=getBrush(grid->GetTile(x-1,y+1));
						if(bnw->height<height)
							deck->DrawWallPoleNW(bnw->wallEdge, loc.mX, loc.mY, zOff-0.03 * OFFSET_RATIO, blockSize, true);
					}
				}
			}//end of North

			//South
			if(y>0){
				bs=getBrush(grid->GetTile(x,y-1));
				if(bs->height < height){
					deck->DrawWallEdgeS(bs->wallEdge, loc.mX, loc.mY, zOff-0.02 * OFFSET_RATIO, blockSize);
				}
				if(be){ //se
					int f=(be->height < height) + (bs->height < height);
					if(f==2){
						deck->DrawWallPoleSE(bs->wallEdge, loc.mX, loc.mY, zOff-0.03 * OFFSET_RATIO, blockSize, false);
					}else if(f==0){
						TMBlockBrush *bse=getBrush(grid->GetTile(x+1,y-1));
						if(bse->height<height)
							deck->DrawWallPoleSE(bse->wallEdge, loc.mX, loc.mY, zOff-0.03 * OFFSET_RATIO, blockSize, true);
					}
				}
				if(bw){ //sw
					int f=(bw->height < height) + (bs->height < height);
					if(f==2){
						deck->DrawWallPoleSW(bs->wallEdge, loc.mX, loc.mY, zOff-0.03 * OFFSET_RATIO, blockSize, false);
					}else if(f==0){
						TMBlockBrush *bsw=getBrush(grid->GetTile(x-1,y-1));
						if(bsw->height<height)
							deck->DrawWallPoleSW(bsw->wallEdge, loc.mX, loc.mY, zOff-0.03 * OFFSET_RATIO, blockSize, true);
					}
				}
			}//end of South


		}
	}//end of walledge pass
#ifdef DRAW_SHADOW
	
	for ( int x = c0.mX; x <= c1.mX; ++x ) {
		for ( int y = c1.mY; y >= c0.mY; --y ) {
			
			MOAICellCoord wrap = grid->WrapCellCoord ( x, y );
			TMBlockBrush *brush=getBrush(grid->GetTile(x,y));
			int height=brush->height;

			MOAICellCoord coord ( x, y );
			USVec2D loc = grid->GetTilePoint ( coord, MOAIGridSpace::TILE_CENTER );
			
			float zOff= (4.0f-(float)height)/2.0f * blockSize;

			if(height==4) continue;
			
			//WEST
			if(x>0){
				TMBlockBrush *brushW=getBrush(grid->GetTile(x-1,y));
				u32 heightW=brushW->height;

				if(heightW > height){
					u32 heightN=getBrush(grid->GetTile(x,y+1))->height;

					//draw shadow
					int shadowIdxOff= (heightW-height-1);
					deck->DrawFace(IDX_SHADOW_FACE_START + shadowIdxOff, 
													loc.mX, loc.mY, zOff-0.03 * OFFSET_RATIO , blockSize );

					if(height < heightN){
						if(heightN>2 && heightW >2 ){//upper wall
							deck->DrawWall(IDX_SHADOW_WALL1_START+shadowIdxOff,
														loc.mX, loc.mY + blockSize/2-0.02 * OFFSET_RATIO, blockSize/2, blockSize );
						}
						if(height<=2){ //lower wall
							deck->DrawWall(IDX_SHADOW_WALL2_START+shadowIdxOff,
														loc.mX, loc.mY + blockSize/2-0.02 * OFFSET_RATIO, blockSize*1.5 , blockSize );
						}

					}	

				}
			}
			//END of west			
		}
	}//end of shadow pass
#endif
}

TMBlockProp::TMBlockProp()
{
	RTTI_BEGIN
		RTTI_EXTEND(MOAIProp)
	RTTI_END
	this->SetMask ( MOAIProp::CAN_DRAW );
}

TMBlockProp::~TMBlockProp(){
	mBrushes[0].height=0;
}

void	TMBlockProp::RegisterLuaClass	( MOAILuaState& state ){
	MOAIProp::RegisterLuaClass ( state );
}

void	TMBlockProp::RegisterLuaFuncs	( MOAILuaState& state ){
	MOAIProp::RegisterLuaFuncs ( state );
	luaL_Reg regTable [] = {
		{"registerBrush",			_registerBrush},
		{ NULL, NULL }
	};
	
	luaL_register ( state, 0, regTable );
}


// int TMBlockGrid::_init(lua_State *L){
// 	MOAI_LUA_SETUP(TMBlockGrid, "UNNNN");
// 	u32 col=state.GetValue<u32>(2,0);
// 	u32 row=state.GetValue<u32>(3,0);

// 	u32 blockSize=state.GetValue<u32>(4,1);
	
// 	self->mBlockSize=blockSize;
// 	self->mBlockRow=row;
// 	self->mBlockCol=col;

// 	self->mGrid->Init(col,row,blockSize,blockSize);
// 	self->mGrid->GetTileArray().Init(self->mGrid->GetTotalCells());
// 	self->mGrid->Fill(0);
// 	return 0;

// }

int TMBlockGrid::_setBlock(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNN");
	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;

	u32 height=state.GetValue<u32>(4,0);
	u32 page=state.GetValue<u32>(5,0);
	u32 wallEdge=state.GetValue<u32>(6,0);
	u32 wall1=state.GetValue<u32>(7,0);
	u32 wall2=state.GetValue<u32>(8,0);
	u32 face=state.GetValue<u32>(9,0);

	self->setBlock(x, y, height, page, wallEdge, wall1, wall2, face);
	return 0;
}

int TMBlockGrid::_getBlock(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNN");
	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;

	u32 height;
	u32 page;
	u32 wallEdge;
	u32 wall1;
	u32 wall2;
	u32 face;

	self->getBlock(x, y, height, page, wallEdge, wall1, wall2, face);

	state.Push(height);
	state.Push(page);
	state.Push(wallEdge);
	state.Push(wall1);
	state.Push(wall2);
	state.Push(face);
	return 6;
}


int TMBlockGrid::_setFace(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNNN");
	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;

	u32 value=state.GetValue<u32>(4,0);
	self->setFace(x, y, value);
	return 0;
}

int TMBlockGrid::_setPage(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNNN");
	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;

	u32 value=state.GetValue<u32>(4,0);
	self->setPage(x, y, value);
	return 0;
}

int TMBlockGrid::_setHeight(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNNN");
	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;

	u32 value=state.GetValue<u32>(4,0);
	self->setHeight(x, y, value);
	return 0;
}

int TMBlockGrid::_setWallEdge(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNNN");
	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;

	u32 value=state.GetValue<u32>(4,0);
	self->setWallEdge(x, y, value);
	return 0;
}

int TMBlockGrid::_setWall(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNNN");
	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;

	u32 wall1=state.GetValue<u32>(4,0);
	u32 wall2=state.GetValue<u32>(5,0);
	self->setWall(x, y, wall1, wall2);
	return 0;
}


int TMBlockGrid::_getHeight(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNN");
	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;
	u32 value;
	self->getHeight(x, y, value);
	state.Push(value);
	return 1;
}


int TMBlockGrid::_getFace(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNN");
	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;
	u32 value;
	self->getFace(x, y, value);
	state.Push(value);
	return 1;
}



int TMBlockGrid::_getPage(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNN");

	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;
	u32 value;
	self->getPage(x, y, value);
	state.Push(value);
	return 1;
}


int TMBlockGrid::_getWallEdge(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNN");
	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;
	u32 value;
	self->getWallEdge(x, y, value);
	state.Push(value);
	return 1;
}

int TMBlockGrid::_getWall(lua_State *L){
	MOAI_LUA_SETUP(TMBlockGrid, "UNN");
	u32 x = state.GetValue<u32>(2,1)-1;
	u32 y = state.GetValue<u32>(3,1)-1;

	u32 wall1,wall2;
	self->getWall(x, y, wall1, wall2);
	state.Push(wall1);
	state.Push(wall2);
	return 2;
}


TMBlockGrid::TMBlockGrid()
{
	RTTI_BEGIN
		RTTI_EXTEND(MOAIGrid)
	RTTI_END
	// this->SetContentMask ( MOAIProp::CAN_DRAW );
}

TMBlockGrid::~TMBlockGrid(){
}


void TMBlockGrid::RegisterLuaClass(MOAILuaState &state){
	MOAIGrid::RegisterLuaClass (state);
}

void TMBlockGrid::RegisterLuaFuncs(MOAILuaState &state){
	MOAIGrid::RegisterLuaFuncs ( state );

	luaL_Reg regTable [] = {
		// { "init",			_init },

		{"setPage",			_setPage},
		{"setFace",			_setFace},
		{"setWall",			_setWall},
		{"setWallEdge",	_setWallEdge},
		{"setHeight",		_setHeight},
		{"setBlock",		_setBlock},

		{"getPage",			_getPage},
		{"getFace",			_getFace},
		{"getWall",			_getWall},
		{"getWallEdge",	_getWallEdge},
		{"getHeight",		_getHeight},
		{"getBlock",		_getBlock},

		{ NULL, NULL }

	};
	
	luaL_register ( state, 0, regTable );
}