#ifndef GRIDMAPOBJECT_H
#define GRIDMAPOBJECT_H

class GridMap
{
private:

public:
	GridMap();
	~GridMap();

	u32 mTileSize;
	u32 mWidth;
	u32 mHeight;
	u32 mSliceSize;

	MOAILuaSharedPtr <TMPathGrid>    mPathGrid;
	MOAILuaSharedPtr <MOAIGrid>      mBaseGrid;
	MOAILuaSharedPtr <MOAIGrid>      mFogGrid;
	MOAILuaSharedPtr <MOAIGrid>      mWaterGrid;

	void init( u32 width, u32 height, u32 tileSize, u32 partitionCellSize, u32 sliceSize );
	
	void insertObject( GridMapObject& obj );
	void removeObject( GridMapObject& obj );

	inline MOAICellCoord getRenderCellCoord( float x, float y ){
		return mBaseGrid->GetCellCoord( x, y );
	}

	inline MOAICellCoord getLogicCellCoord( float x, float y ){
		return mBaseGrid->GetCellCoord( x, y ); //FIXME
	}

	inline USVec2D getTileLoc( u32 x, u32 y ){
		return mBaseGrid->GetTilePoint( MOAICellCoord( x, y ), MOAIGridSpace::TILE_CENTER );
	}

};

class GridMapObject:
	public virtual MOAILuaObject
{
private:

public:
	GridMapObject();
	~GridMapObject();


	
};

#endif
