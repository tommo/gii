#include <extensionClasses.h>
#include "pch.h"
#include <moaicore/MOAILua.h>
#include <TMOffsetGridDeck.h>
#include <TMManualBlocker.h>
#include <MDDHelper.h>
#include <TMPathGrid.h>
#include <TMTileDeck2D.h>
#include <TMBlockProp.h>
#include <TMInfluenceMap.h>
#include <MDDMap.h>
#include <MDDMapObject.h>
#include <MOAISimplexNoiseGenerator.h>


void registerExtensionClasses(){
		// REGISTER_LUA_CLASS(TMOffsetGridDeck)
		REGISTER_LUA_CLASS(TMManualBlocker)
		REGISTER_LUA_CLASS(TMPathGrid)
		REGISTER_LUA_CLASS(MDDHelper)
		//render
		REGISTER_LUA_CLASS(TMTileDeck2D)
		REGISTER_LUA_CLASS(TMBlockGrid)
		REGISTER_LUA_CLASS(TMBlockProp)

		REGISTER_LUA_CLASS(TMInfluenceMap)
		REGISTER_LUA_CLASS(TMInfluenceMapWalker)

		REGISTER_LUA_CLASS(MDDMap)
		REGISTER_LUA_CLASS(MDDMapObject)

		REGISTER_LUA_CLASS(MOAISimplexNoiseGenerator)

}
