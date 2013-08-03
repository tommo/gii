#ifndef	TMBLOCKTILEDECK_H
#define	TMBLOCKTILEDECK_H

#include <moaicore/pch.h>
#include <moaicore/MOAIDeckRemapper.h>
#include <moaicore/MOAIGrid.h>
#include <moaicore/MOAILogMessages.h>
#include <moaicore/MOAIProp.h>
#include <moaicore/MOAIQuadBrush.h>
#include <moaicore/MOAITileDeck2D.h>


#define BIT_SPAN(a,l) (~(0xffffffff<<l)) << a
#define CODE_BIT_SIZE 5
#define PAGE_BIT_SIZE 5


class TMBlockGrid:
	public MOAIGrid{
	private:
		static int _setPage(lua_State* L);
		static int _setFace(lua_State* L);
		static int _setWall(lua_State* L);
		static int _setWallEdge(lua_State* L);
		static int _setHeight(lua_State* L);

		static int _setBlock(lua_State* L);

		static int _getPage(lua_State* L);
		static int _getFace(lua_State* L);
		static int _getWall(lua_State* L);
		static int _getWallEdge(lua_State* L);
		static int _getHeight(lua_State* L);
		
		static int _getBlock(lua_State* L);

		static const u32 XFLIP				= 0x20000000;
		static const u32 YFLIP				= 0x40000000;
		static const u32 HIDDEN				= 0x80000000;
		
		static const u32 FLIP_MASK			= 0x60000000;
		static const u32 FLAGS_MASK			= 0xf0000000;

		static const u32 HEIGHT_MASK		=	BIT_SPAN(25,3);
		static const u32 PAGE_MASK			=	BIT_SPAN(20,5);
		static const u32 WALLEDGE_MASK	=	BIT_SPAN(15,5);
		static const u32 WALL2_MASK			=	BIT_SPAN(10,5);
		static const u32 WALL1_MASK			=	BIT_SPAN(5, 5);
		static const u32 FACE_MASK			=	BIT_SPAN(0, 5);

		static const u32 HEIGHT_OFFSET		=	25;
		static const u32 PAGE_OFFSET			=	20;
		static const u32 WALLEDGE_OFFSET	=	15;
		static const u32 WALL2_OFFSET			=	10;
		static const u32 WALL1_OFFSET			=	5;
		static const u32 FACE_OFFSET			=	0;

		static const u32 CODE_MASK			= 0x0fffffff;

public:

		DECL_LUA_FACTORY(TMBlockGrid)

		void setFace(u32 x, u32 y, u32 code){
			u32 value=this->GetTile(x,y);
			value=(value & ~FACE_MASK) | ( code << FACE_OFFSET & FACE_MASK );
			this->SetTile(x,y, value);
		}

		void setWall(u32 x, u32 y, u32 codeUpper, u32 codeLower){
			u32 idx=this->GetTile(x,y);
			u32 value=this->GetTile(x,y);
			value=(value & ~WALL1_MASK) | ( codeUpper << WALL1_OFFSET & WALL1_MASK );
			value=(value & ~WALL2_MASK) | ( codeLower << WALL2_OFFSET & WALL2_MASK );
			this->SetTile(x,y, value);
		}

		void setPage(u32 x, u32 y, u32 code){
			u32 idx=this->GetTile(x,y);
			u32 value=this->GetTile(x,y);
			value=(value & ~PAGE_MASK) | ( code << PAGE_OFFSET & PAGE_MASK );
			this->SetTile(x,y, value);
		}

		void setWallEdge(u32 x, u32 y, u32 code){
			u32 idx=this->GetTile(x,y);
			u32 value=this->GetTile(x,y);
			value=(value & ~WALLEDGE_MASK) | ( code << WALLEDGE_OFFSET & WALLEDGE_MASK );
			this->SetTile(x,y, value);
		}

		void setHeight(u32 x, u32 y, u32 height){
			u32 idx=this->GetTile(x,y);
			u32 value=this->GetTile(x,y);
			value=(value & ~HEIGHT_MASK) | ( height << HEIGHT_OFFSET & HEIGHT_MASK );
			this->SetTile(x,y, value);
		}


		void setBlock(u32 x, u32 y, u32 height, 
				u32 page,
				u32 codeWallEdge,
				u32 codeWallUpper,u32 codeWallLower,
				u32 codeFace
				){

			u32 value=0;
			value = value | (height << HEIGHT_OFFSET & HEIGHT_MASK);
			value = value | (page << PAGE_OFFSET & PAGE_MASK);
			value = value | (codeWallEdge << WALLEDGE_OFFSET & WALLEDGE_MASK);
			value = value | (codeWallUpper << WALL1_OFFSET & WALL1_MASK);
			value = value | (codeWallLower << WALL2_OFFSET & WALL2_MASK);
			value = value | (codeFace << FACE_OFFSET & FACE_MASK);
			this->SetTile(x, y, value);

		}


		void getFace(u32 x, u32 y, u32 &code){
			u32 value=this->GetTile(x, y);
			code= value & FACE_MASK;
		}

		void getWall(u32 x, u32 y, u32 &codeUpper, u32 &codeLower){
			u32 value=this->GetTile(x, y);
			codeUpper=(value & WALL1_MASK) >> WALL1_OFFSET;
			codeLower=(value & WALL2_MASK) >> WALL2_OFFSET;
		}

		void getWallEdge(u32 x, u32 y, u32 &code){
			u32 value=this->GetTile(x, y);
			code=(value & WALLEDGE_MASK) >> WALLEDGE_OFFSET;
		}

		void getPage(u32 x, u32 y, u32 &code){
			u32 value=this->GetTile(x, y);
			code=(value & PAGE_MASK) >> PAGE_OFFSET;
		}

		void getHeight(u32 x, u32 y,u32 &height){
			u32 value=this->GetTile(x, y);
			height=(value & HEIGHT_MASK) >> HEIGHT_OFFSET;
		}

		void getBlock(u32 x, u32 y,
			u32 &height, 
			u32 &page, 
			u32 &codeWallEdge, 
			u32 &codeWall1, u32 &codeWall2, 
			u32 &codeFace)
		{
			u32 value=this->GetTile(x, y);
			height       =	(value & HEIGHT_MASK)	 >> HEIGHT_OFFSET;
			page         =	(value & PAGE_MASK)	 >> PAGE_OFFSET;
			codeWallEdge =	(value & WALLEDGE_MASK)	 >> WALLEDGE_OFFSET;
			codeWall1    =	(value & WALL1_MASK)	 >> WALL1_OFFSET;
			codeWall2    =	(value & WALL2_MASK)	 >> WALL2_OFFSET;
			codeFace     =	(value & FACE_MASK)	 >> FACE_OFFSET;
		}

	
	TMBlockGrid();
	~TMBlockGrid();

	void			RegisterLuaClass		( MOAILuaState& state );
	void			RegisterLuaFuncs		( MOAILuaState& state );
	/* data */
};

struct TMBlockBrush{
	int height;
	u32 face;
	u32 wall1;
	u32 wall2;
	u32 wallEdge;
};

class TMBlockProp:
	public MOAIProp {
	private:		
		static const u32 IDX_SHADOW_WALL1_START =5;
		static const u32 IDX_SHADOW_WALL2_START =13;
		static const u32 IDX_SHADOW_FACE_START =21;
		static int _registerBrush(lua_State *L);
		TMBlockBrush* getBrush(u32 id);
		TMBlockBrush mBrushes[256];
	public:

		DECL_LUA_FACTORY (TMBlockProp)
		
		void		Draw					( int subPrimID );
					TMBlockProp				();
					~TMBlockProp				();

		void			RegisterLuaClass		( MOAILuaState& state );
		void			RegisterLuaFuncs		( MOAILuaState& state );
};


#endif

