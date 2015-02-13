module 'mock'

CLASS: PrebuiltAtlasItem ()
CLASS: PrebuiltAtlasPage ()
CLASS: PrebuiltAtlas ()

PrebuiltAtlasItem
	:MODEL{
		Field 'name' :string() :no_edit();
		Field 'x' ;
		Field 'y' ;		
		Field 'w' ;
		Field 'h' ;
		Field 'ox'; --offset
		Field 'oy';
		Field 'ow'; --original
		Field 'oh';
		Field 'u0';
		Field 'v0';
		Field 'u1';
		Field 'v1';
		Field 'rotated' :boolean();		
	}

function PrebuiltAtlasItem:__init()
	self.w,  self.h  = 100, 100
	self.ow, self.oh = 100, 100
	self.x,  self.y  = 0,0
	self.ox, self.oy = 0,0
	self.u0, self.v0 = 0,0
	self.u1, self.v1 = 1,1
	self.rotated = false
	self.parent  = false
end

--------------------------------------------------------------------
PrebuiltAtlasPage
	:MODEL{
		Field 'id'     :int();
		Field 'textureAtlasId' :int();
		Field 'source' :string() :no_edit();		
		Field 'w'      :int();
		Field 'h'      :int();
		Field 'ow'     :int();
		Field 'oh'     :int();
		-- Field 'texture' :string() :no_edit();
		Field 'items'   :array( PrebuiltAtlasItem ) :no_edit();
	}

function PrebuiltAtlasPage:__init()
	self.id             = 0
	self.textureAtlasId = 0
	self.source         = false	
	self.items          = {}
	self.parent         = false
	self._texture       = false
	
	self.w = 100
	self.h = 100
	self.ow = 100
	self.oh = 100
end

function PrebuiltAtlasPage:addItem()
	local item = PrebuiltAtlasItem()
	table.insert( self.items, item )
	item.parent = self
	return item
end

function PrebuiltAtlasPage:getItems()
	return self.items
end

function PrebuiltAtlasPage:_postLoad()
	for i, item in ipairs( self.items ) do
		item.parent = self
	end
end

function PrebuiltAtlasPage:updateTexture( textureAtlasId, x, y, w, h )
	for i, item in ipairs( self.items ) do
		item.x = x + item.x
		item.y = y + item.y
	end
	self.textureAtlasId = textureAtlasId
	self.w = w
	self.h = h
	--todo: other modifications/ size/ explosion...
end

function PrebuiltAtlasPage:rescale( scl )
	self.w = self.w * scl
	self.h = self.h * scl
	for i, item in ipairs( self.items ) do
		item.x = item.x*scl
		item.y = item.y*scl
		item.w = item.w*scl
		item.h = item.h*scl
	end
end

function PrebuiltAtlasPage:findItem( id )
	for i, item in ipairs( self.items ) do
		if item.name == id then return item end
	end
	return nil
end

function PrebuiltAtlasPage:getMoaiTexture()
	return self._texture
end

--------------------------------------------------------------------
PrebuiltAtlas
	:MODEL{
		Field 'path' :string() :no_edit();
		Field 'pages' :array( PrebuiltAtlasPage ) :no_edit();
	}

function PrebuiltAtlas:__init()
	self.path  = false
	self.pages = {}
end

function PrebuiltAtlas:addPage()
	local page = PrebuiltAtlasPage()
	table.insert( self.pages, page )
	page.parent = self
	page.id = #self.pages
	return page
end

function PrebuiltAtlas:getPages()
	return self.pages
end

function PrebuiltAtlas:getPage( id )
	return self.pages[ id ]
end

function PrebuiltAtlas:affirmPage( id )
	assert( type( id ) == 'number' )
	local page = self.pages[ id ]
	if not page then
		for i = #self.pages, id - 1 do
			self:addPage()
		end
		page = self.pages[ id ]
	end
	return page
end

function PrebuiltAtlas:rescale( scl )
	for i, page in ipairs( self.pages ) do
		page:rescale( scl )
	end
end

function PrebuiltAtlas:load( path )
	mock.deserializeFromFile( self, path )
	for i, page in ipairs( self.pages ) do
		page.parent = self
		page:_postLoad()
	end
end

function PrebuiltAtlas:save( path )
	return mock.serializeToFile( self, path )
end

function PrebuiltAtlas:buildItemLookupDict()
	local dict = {}
	for i, page in ipairs( self.pages ) do
		for j, item in ipairs( page.items ) do
			dict[ item.name ] = item
		end
	end
	self.itemDict = dict
	return dict
end
