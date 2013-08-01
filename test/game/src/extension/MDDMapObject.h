#ifndef TMMAPOBJECT_H
#define TMMAPOBJECT_H

#include <TMPathGrid.h>
#include <TMInfluenceMap.h>
#include <MDDMap.h>
#include <moaicore/MOAIProp.h>

class MDDMap;

class MDDMapObject:
	public virtual MOAIProp
{
private:
	//----------------------------------------------------------------//
	static int _setTeamFlags         ( lua_State *L );
	static int _setPassFlags         ( lua_State *L );
	static int _setVisionPassFlags   ( lua_State *L );
	static int _setCollisionFlags    ( lua_State *L );
	static int _setCollisionListener ( lua_State *L );

	static int _setTarget            ( lua_State *L );
	static int _setSpeed             ( lua_State *L );
	static int _setRadius            ( lua_State *L );

	static int _setPushing           ( lua_State *L );
	static int _setPushable          ( lua_State *L );

	static int _canSeeObject         ( lua_State *L );
	static int _canSeeTile           ( lua_State *L );
	static int _findSeeableObjects   ( lua_State *L );
	
	static int _getCellCoord         ( lua_State *L );
	static int _setCellCoord         ( lua_State *L );
	static int _getVectorFacing      ( lua_State *L );
	static int _getVectorTarget      ( lua_State *L );
	
	static int _pushWayPoint         ( lua_State *L );
	static int _clearWayPoints       ( lua_State *L );
	static int _hasWayPoint          ( lua_State *L );

	static int _moveTowardObject     ( lua_State *L );
	static int _moveAwayFromObject   ( lua_State *L );
	static int _moveToward           ( lua_State *L );
	
	static int _updateStep           ( lua_State *L );

	//----------------------------------------------------------------//
	bool computeTarget          ( float delta );
	int  computeObjectCollision ();
	int  computeWallCollision   ();
	int  checkTileState         ();

	enum {
		MOTION_FLAGS_PUSHABLE = 0x01,
		MOTION_FLAGS_PUSHING  = 0x02,
		MOTION_FLAGS_RUNAWAY  = 0x04
	};


public: //just for this project, so we just use public for all members...
	u32         mMotionFlags;
	float       mSpeed;
	int         mGroup;

	u32         mVisionPassFlags;
	u32         mPassFlags;
	u32         mTeamFlags;
	u32         mCollisionMask;
	u32         mCollisionFlags;

	USVec2D     mVectorFacing;    //final computed vector, limit within length of 1

	USVec2D     mVectorTarget;    //vector pointing intentional target
	USVec2D     mVectorAvoidance; //vector of avoidance to Object/Wall
	USVec2D     mVectorInfluence; //vector of attraction by influence map
	float       mWeightAvoid;

	USVec2D*    mTarget;

	float       mRadius;
	float       mRadiusAvoidObject;
	float       mRadiusAvoidWall;
	float       mRadiusVision;
	float       mRadiusArrival;

	STLList     <USVec2D> mWayPoints;
	
	MDDMap*     mMap;

	MOAILuaLocal mOnObjectCollision;
	MOAILuaLocal mOnTileCollision;


	//----------------------------------------------------------------//
	// void setTarget    ( USVec2D target );
	
	MOAICellCoord getCellCoord    () ;
	void setCellCoord             ( u32 x, u32 y );

	//----------------------------------------------------------------//
	bool canSeeObject             ( MDDMapObject& obj );
	bool canSeePoint              ( float x, float y );
	bool canSeeTile               ( u32 x, u32 y );
	bool canDirectVisitTile       ( u32 x, u32 y );
	bool canDirectVisitPoint      ( float x, float y );

	bool updateStep               ( float delta );
	bool update                   ( float delta, u32 phase );


	void setRadius                ( float radius, float radiusAvoidWall, float radiusAvoidObject );

	void pushWayPoint             ( USVec2D vec );
	void clearWayPoints           ();

	void setTarget                ( const USVec2D& target );
	void clearTarget              ();

	bool moveTowardObject         ( MDDMapObject& obj, float chaseRadius );
	bool moveAwayFromObject       ( MDDMapObject& obj, float safeRadius );
	void moveToward               ( USVec2D vec );

	//----------------------------------------------------------------//

	void setPushing ( bool pushing ){
		if( pushing ) {
			mMotionFlags |= MOTION_FLAGS_PUSHING;
		} else {
			mMotionFlags &= ~MOTION_FLAGS_PUSHING;
		}
	}

	void setPushable ( bool pushable ){
		if( pushable ) {
			mMotionFlags |= MOTION_FLAGS_PUSHABLE;
		} else {
			mMotionFlags &= ~MOTION_FLAGS_PUSHABLE;
		}
	}

	void setRunningAway ( bool away ){
		if( away ) {
			mMotionFlags |= MOTION_FLAGS_RUNAWAY;
		} else {
			mMotionFlags &= ~MOTION_FLAGS_RUNAWAY;
		}
	}

	inline bool isPushing () {
		return ( mMotionFlags & MOTION_FLAGS_PUSHING ) != 0;
	}

	inline bool isPushable () {
		return ( mMotionFlags & MOTION_FLAGS_PUSHABLE ) != 0;
	}

	inline bool isRunningAway () {
		return ( mMotionFlags & MOTION_FLAGS_RUNAWAY ) != 0;
	}

	inline bool isFriendTeam ( MDDMapObject& o ) {
		return ( o.mTeamFlags & mTeamFlags ) != 0;
	}

	//----------------------------------------------------------------//
	DECL_LUA_FACTORY ( MDDMapObject )

	MDDMapObject();
	~MDDMapObject();

	void  RegisterLuaClass ( MOAILuaState& state );
	void  RegisterLuaFuncs ( MOAILuaState& state );


};

#endif
