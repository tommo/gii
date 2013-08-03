#ifndef MOAISIMPLEXNOISEGENERATOR_H
#define MOAISIMPLEXNOISEGENERATOR_H

#include <moaicore/pch.h>
#include <moaicore/MOAILua.h>

#define SFMT_MEXP 19937
//----------------------------------------------------------------//
extern "C" {
	#include <SFMT.h>
}

//----------------------------------------------------------------//
// SimplexNoise1234
// Copyright © 2003-2011, Stefan Gustavson
//
// Contact: stegu@itn.liu.se
typedef struct {
	unsigned char perm[512];
} snoise_permtable;

void snoise_setup_perm_noseed(snoise_permtable* p, SFMT_T* sfmt); // use SFMT instead of MT
float snoise1(snoise_permtable* c, float x);
float snoise2(snoise_permtable* c, float x, float y);
float snoise3(snoise_permtable* c, float x, float y, float z);
float snoise4(snoise_permtable* c, float x, float y, float z, float w);

#define FASTFLOOR(x) ( ((x)>0) ? ((int)x) : (((int)x)-1) )


//----------------------------------------------------------------//
//MOAISimplexNoiseGenerator
//----------------------------------------------------------------//
class MOAISimplexNoiseGenerator:
	public virtual MOAILuaObject
{
private:
	SFMT_T  mSFMT;
	snoise_permtable mPermtable;

	static int _seedNoise   ( lua_State* L );
	static int _genNoise1D  ( lua_State* L );
	static int _genNoise2D  ( lua_State* L );
	static int _genNoise3D  ( lua_State* L );

public:
	void  SeedNoise  ( u32 seed );
	float GenNoise1D ( float x );
	float GenNoise2D ( float x, float y );
	float GenNoise3D ( float x, float y, float z );

	DECL_LUA_FACTORY (MOAISimplexNoiseGenerator)

	void			RegisterLuaClass		( MOAILuaState& state );
	void			RegisterLuaFuncs		( MOAILuaState& state );

	MOAISimplexNoiseGenerator();
	~MOAISimplexNoiseGenerator();

};

#endif
