module 'mock'

local GlobalObjectRegistry = {}
--------------------------------------------------------------------
CLASS: GlobalObjectNode ()
	:MODEL{
		Field '_folded' :boolean() :no_edit(); 

		Field 'name' :string() :set( 'setName' ); 
		Field 'persistent' :boolean();
	}

function GlobalObjectNode:__init()
	self.children = {}
	self.name = self:getClassName()
	self.persistent = false
	self.type     = false
	self.object   = false
	self._folded  = false
end

function GlobalObjectNode:addNode( name, child )
	local child = child or GlobalObjectNode()
	child.parent   = self
	child.library  = self.library
	child:setName( name )
	return child
end

function GlobalObjectNode:setName( name )
	--build fullpath for object	
	local parent = self.parent
	if self.name then
		parent.children[ self.name ] = nil
	end
	self.name = name
	parent.children[ name ] = self
	self:updateFullName()
end

function GlobalObjectNode:updateFullName()
	local name = self.name
	local parent = self.parent
	if self.fullName then
		self.library.index[ self.fullName ] = nil
	end
	self.fullName = parent.fullName and ( parent.fullName .. '.' .. name ) or name
	self.library.index[ self.fullName ] = self
	for k, obj in pairs( self.children ) do
		obj:updateFullName()
	end
end

function GlobalObjectNode:addGroup( name )
	local node = self:addNode( name )
	node.type = 'group'
	return node
end

function GlobalObjectNode:addObject( name, object )
	local node = self:addNode( name )
	node.type     = 'object'
	node.object   = object
	node.objectType = object:getClassName()
	return node
end

function GlobalObjectNode:removeNode( name )
	local n = self.children[ name ]
	if n then
		n.parent = false
		self.children[ name ] = nil
		return true
	end
	return false
end

---------------------------------------------------------------------
CLASS: GlobalObjectLibrary ()
	:MODEL{}

function GlobalObjectLibrary:__init()
	self.index = {}
	
	local root    = GlobalObjectNode()
	root.type     = 'group'
	root.library  = self
	root.fullName = false

	self.root  = root
end

local function _loadGlobalObject( objData, parent )
	assert( objData['type'] == 'group' )

	for name ,childData in pairs( objData['children'] ) do
		local tt   = childData['type']
		if tt == 'group' then
			local node = parent:addGroup( name )
			_loadGlobalObject( childData, node )
		else
			local object = deserialize( nil, childData['object'] )
			local node = parent:addObject( name, object )
		end
	end
	
end

function GlobalObjectLibrary:load( data )
	if not data then return end
	_loadGlobalObject( data, self.root )	
end

-- local function _reloadGlobalObject( node )
-- 	local tt = node.type
-- 	if tt == 'group' then
-- 		for name, child in pairs( node.children ) do
-- 			_reloadGlobalObject( child )
-- 		end
-- 	else
-- 		local data = serialize( node.object )
-- 		deserialize( node.object, data )
-- 	end
-- end

-- function GlobalObjectLibrary:reload()
-- 	_reloadGlobalObject( self.root )
-- end

function GlobalObjectLibrary:reload()
	local data = self:save()
	self:load( data )
end

local function _saveGlobalObject( node )
	local tt = node.type
	if tt == 'group' then
		local children = {}
		for name, child in pairs( node.children ) do
			children[ name ] = _saveGlobalObject( child )
		end
		return {
			name   = node.name,
			children = children,
			type   = 'group'
		}
	else
		return {
			name   = node.name,
			object = serialize( node.object ),
			type   = 'object'
		}
	end
end

function GlobalObjectLibrary:save()
	return _saveGlobalObject( self.root )	
end

function GlobalObjectLibrary:get( path )
	local n = self:getNode( path )
	if not n then return nil end
	return n.object
end

function GlobalObjectLibrary:getNode( path )
	return self.index[ path ]
end

local function _collectChildNode( node, list )
	for k, n in pairs( node.children ) do
		table.insert( list, n )
		_collectChildNode( n, list )
	end
	return list
end

function GlobalObjectLibrary:getNodeList()
	local list = {}
	_collectChildNode( self.root, list )
	return list
end

--------------------------------------------------------------------
function registerGlobalObject( name, clas ) --TODO:icon?
	if GlobalObjectRegistry[ name ] then
		_warn( 'global object class duplicated', clas )
	end
	GlobalObjectRegistry[ name ] = clas
end

function getGlobalObjectClass( name )
	return GlobalObjectRegistry[ name ]
end

function getGlobalObjectClassRegistry()
	return GlobalObjectRegistry
end
