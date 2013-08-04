--[[
* MOCK framework for Moai

* Copyright (C) 2012 Tommo Zhou(tommo.zhou@gmail.com).  All rights reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining
* a copy of this software and associated documentation files (the
* "Software"), to deal in the Software without restriction, including
* without limitation the rights to use, copy, modify, merge, publish,
* distribute, sublicense, and/or sell copies of the Software, and to
* permit persons to whom the Software is furnished to do so, subject to
* the following conditions:
*
* The above copyright notice and this permission notice shall be
* included in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
]]

local setmetatable=setmetatable
local getmetatable=getmetatable
local rawget,rawset=rawget,rawset

--------------------------------------------------------------------
-- CLASS
--------------------------------------------------------------------
local newclass

local BaseClass = {
	__subclasses={}
}

_BASECLASS = BaseClass --use this to extract whole class tree

--Class build DSL
function BaseClass:MODEL( t )
	local m = Model( self )
	m:update( t )
	return self
end

function BaseClass:MEMBER( t )
	for k, v in pairs( t ) do
		self[k] = v
	end
	return self
end

function BaseClass:META( t )
	self.__meta = t
	return self
end

function BaseClass:rawInstance( t )
	return setmetatable( t, self )
end

function BaseClass:isSubclass( superclass )
	local s = self.__super
	while s do
		if s == superclass then return true end
		s = s.__super
	end
	return false
end

--Instance Method
function BaseClass:getClass()
	return self.__class
end

function BaseClass:getClassName()
	return self.__class.__name
end

function BaseClass:isInstance( clas )
	local c = self.__class
	if c == clas then return true end
	return c:isSubclass( clas )
end


--------------------------------------------------------------------
local function buildInitializer(class,f)
	if not class then return f end
	local init=rawget(class,'__init')
	
	if type(init)=='table' then --copy
		local t1=init
		init=function(a)
			for k,v in pairs(t1) do
				a[k]=v
			end
		end
	end

	if init then
		if f then
			local f1=f
			f=function(a,...)
				init(a,...)
				return f1(a,...)
			end
		else
			f=init
		end
	end

	return buildInitializer(class.__super,f)
end

local function buildInstanceBuilder(class)
	local init=buildInitializer(class)
	local newinstance

	if init then
		newinstance=function (t,...)
			local o=setmetatable({}, class)
			init(o,...)
			return o
		end
	else
		newinstance=function (t)
			return setmetatable({}, class)
		end
	end

	local mt=getmetatable(class)
	mt.__call=newinstance

	for s in pairs(class.__subclasses) do
		buildInstanceBuilder(s)
	end
end

--------------------------------------------------------------------
function newclass( b, superclass, name  )		
	b=b or {}
	local index
	superclass = superclass or BaseClass
	b.__super  = superclass

	for k,v in pairs(superclass) do --copy super method to reduce index time
		if k~='__init' and rawget(b,k)==nil then 
			b[k]=v
		end
	end

	superclass.__subclasses[b] = true

	b.__index = b
	b.__class = b
	b.__subclasses = {}
	if not name then
		local s = superclass
		while s do
			local sname = s.__name
			if sname and sname ~= '??' then
				name = s.__name..':??'
				break
			end
			s = s.__super
		end
	end
	b.__name  = name or '??'


	local newindex=function( t, k, v )		
		rawset( b, k, v )
		if k=='__init' then
			buildInstanceBuilder(b)
		else --spread? TODO
		end
	end
	
	setmetatable( b, {
			__newindex = newindex,
			__isclass  = true
		}
	)

	buildInstanceBuilder(b)

	return b
end

function updateAllSubClasses(c,force)
	for s in pairs(c.__subclasses) do
		local updated=false
		for k,v in pairs(c) do			
			if force or rawget(s,k)==nil then 
				updated=true
				s[k]=v
			end
		end
		if updated then updateAllSubClasses(s) end
	end
end

function isClass( c )
	local mt = getmetatable( c )
	return mt and mt.__isclass or false
end

function isClassInstance( o )
	return getClass( o ) ~= nil
end

function getClass( o )
	if type( o ) ~= 'table' then return nil end
	local clas = getmetatable( o )
	if not clas then return nil end
	local mt = getmetatable( clas )
	return mt and mt.__isclass and clas or nil
end

local classBuilder
local function affirmClass( t, id )
	if type(id) ~= 'string' then error('class name expected',2) end
	return function( a, ... )
			local superclass
			if select( '#', ... ) >= 1 then 
				superclass = ...
				if not superclass then
					error( 'invalid superclass for:' .. id, 2 )
				end
			end
			
			if a ~= classBuilder then
				error( 'Class syntax error', 2 )
			end
			if superclass and not isClass( superclass ) then
				error( 'Superclass expected, given:'..type( superclass ), 2)
			end
			local clas = newclass( {}, superclass, id )
			local env = getfenv( 2 )
			env[id] = clas
			return clas
		end
end

classBuilder = setmetatable( {}, {__index = affirmClass })
-- _G.Class  = newclass
_G.CLASS  = classBuilder

--------------------------------------------------------------------
--MODEL & Field
--------------------------------------------------------------------

CLASS: Model ()
function Model:__init( clas )
	self.__class = clas
	self.__name  = clas.__name or 'LuaObject'
	clas.__model = self
end

function Model.fromObject( obj )
	local clas = getClass( obj )
	-- if not clas then return nil end
	assert( clas, 'not class object' )
	return Model.fromClass( clas )
end

function Model.fromClass( clas )
	if not isClass(clas) then
		error( 'not valid class', 2 ) 
		return nil
	end
	local m = rawget( clas, '__model' )
	if not m then
		m = Model( clas )
	end
	return m	
end

function Model:__call( body )
	self:update( body )
	return self
end

function Model:update( body )
	--body[1] = name
	-- local name = body[1]
	-- if type(name) ~= 'string' then error('Model Name should be the first item', 3 ) end
	-- self.__name = name
	local fields = {}
	local fieldN = {}
	for i = 1, #body do
		local f = body[i]
		if getmetatable( f ) ~= Field then 
			error('Field expected in Model, given:'..type( f ), 3)
		end
		local id = f.__id
		if fieldN[id] then error( 'duplicated Field:'..id, 3 ) end
		fieldN[ id ] = f
		fields[ i ] = f
	end
	self.__fields = fields
	self.__fieldNames = fieldN
	-- self.__class.__name = name
	return self
end

function Model:getMeta()
	return rawget( self.__class, '__meta' )
end

function Model:getField( name, findInSuperClass )
	local fields = self.__fields
	if fields then 
		for i, f in ipairs( self.__fields ) do
			if f.__id == name then return f end
		end
	end
	findInSuperClass = findInSuperClass~=false
	if findInSuperClass then
		local superModel = self:getSuperModel()
		if superModel then return superModel:getField( name, true ) end
	end
	return nil
end

local function _collectFields( model, includeSuperFields, list, dict )
	list = list or {}
	dict = dict or {}
	if includeSuperFields then
		local s = model:getSuperModel()
		if s then _collectFields( s, true, list, dict ) end
	end
	local fields = model.__fields
	if fields then
		for i, f in ipairs( fields ) do
			local id = f.__id
			local i0 = dict[id]
			if i0 then --override
				list[i0] = f
			else
				local n = #list
				list[ n + 1 ] = f
				dict[ id ] = n + 1
			end
		end
	end
	return list
end

function Model:getFieldList( includeSuperFields )
	return _collectFields( self, includeSuperFields ~= false )
end


local function _collectMeta( clas, meta )
	meta = meta or {}
	local super = clas.__super
	if super then
		_collectMeta( super, meta )
	end
	local m = rawget( clas, '__meta' )
	if not m then return meta end
	for k, v in pairs( m ) do
		meta[ k ] = v
	end
	return meta
end

function Model:getCombinedMeta()
	return _collectMeta( self.__class )
end


function Model:getSuperModel( name )
	local superclass = self.__class.__super
	if not superclass then return nil end
	local m = rawget( superclass, '__model' )
	if not m then
		m = Model( superclass )
	end
	return m
end

function Model:getClass()
	return self.__class
end

function Model:isInstance( obj )
	if type(obj) ~= 'table' then return false end
	local clas = getmetatable( obj )
	local clas0 = self.__class
	while clas do
		if clas == clas0 then return true end
		clas = rawget( clas, '__super' )
	end
	return false
end

function Model:getFieldValue( obj, name )
	if not self:isInstance( obj ) then return nil end
	local f = self:getField( name )
	if not f then return nil end
	return f:getFieldValue( obj )
end

function Model:setFieldValue( obj, name, value )
	if not self:isInstance( obj ) then return nil end
	local f = self:getField( name )
	if not f then return nil end
	return f:setFieldValue( obj, value )
end

--------------------------------------------------------------------
CLASS: Field ()
function Field:__init( id )
	self.__id       = id
	self.__type     = 'number'
	self.__keytype  = false  
	self.__getter   = true 
	self.__setter   = true
end

function Field:type( t )
	self.__type = t
	return self
end

function Field:array( t ) 
	self.__type    = t
	self.__keytype = 'number'
	return self
end

function Field:table( ktype, vtype ) 
	self.__type    = v
	self.__keytype = ktype
	return self
end

function Field:meta( meta )
	assert( type(meta) == 'table', 'metadata should be table' )
	self.__meta = meta
	return self
end

function Field:get( getter )
	if type(getter) == 'string' then
		local getterName = getter
		getter = function( obj )
			local f = obj[getterName]
			if f then return f( obj ) else error( 'getter not found:'..getterName ) end
		end
	end
	self.__getter = getter
	return self
end

function Field:set( setter )
	if type(setter) == 'string' then
		local setterName = setter
		setter = function( obj, v )
			local f = obj[setterName]
			if f then return f( obj, v ) else error( 'setter not found:'..setterName ) end
		end
	end
	self.__setter = setter
	return self
end

function Field:getset( fieldName )
	return self:get('get'..fieldName):set('set'..fieldName)
end

function Field:getValue( obj )
	local getter = self.__getter
	if not getter then return nil end 
	if getter == true then return obj[ self.__id ] end
	return getter( obj )
end

function Field:setValue( obj, v )
	local setter = self.__setter
	if not setter then return end 
	if setter == true then obj[ self.__id ] = v return end
	return setter( obj, v )
end

function Field:getIndexValue( obj, idx )
	local t = self:getValue( obj )	
	return t[idx]
end

function Field:setIndexValue( obj, idx, v )
	local t = self:getValue( obj )	
	t[idx] = v
end
