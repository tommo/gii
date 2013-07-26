
module('gii',package.seeall)

local FieldBuilder={}
local FieldBuilderMT={
	__index=FieldBuilder, 
	__call=function (t,v)
			return t:__build(v)
		end
	}

local FieldMT={
	__call=function(t, arg)
		assert(type(arg)=='table')
		for k,v in pairs(arg) do
			t[k]=v
		end	
		return t
	end
}

function FieldBuilder:extend(t1)
	assert(type(t1)=='table', type(t1))
	local f={}
	for k,v in pairs(self.__data) do
		f[k]=v
	end
	for k,v in pairs(t1) do
		f[k]=v
	end
	return setmetatable({__data=f}, FieldBuilderMT)
end

function FieldBuilder:__build(t1)
	assert(type(t1)=='string')
	local f={}
	for k,v in pairs(self.__data) do
		f[k]=v
	end
	f.id=t1
	return setmetatable(f, FieldMT)	
end


local MetaBuilder={}
local MetaBuilderMT={__index=MetaBuilder, __call=function(t,v) return t:__build(v) end}
local MetaMT={}

function MetaBuilder:__build(t1)
	assert(type(t1)=='table')
	return setmetatable(self:__extend(t1), MetaMT)
end

function MetaBuilder:__extend(t1)
	assert(type(t1)=='table')
	local f={}
	for k,v in pairs(self.__data) do
		f[k]=v
	end
	for k,v in pairs(t1) do
		f[k]=v
	end
	return f
end

function MetaBuilder:extend(t1)
	return setmetatable({ __data = self:__extend(t1) }, MetaBuilderMT)
end

Field = setmetatable({
		__data={type='number'}
	}, FieldBuilderMT)

Model = Field:extend{} --temporary

Meta	= setmetatable({
		__data={
			__meta__=true
		}
	}, MetaBuilderMT)

--numeric
Field.number   = Field:extend{ type='number', default=0 }
Field.integer  = Field:extend{ type='integer', default=0 }
Field.int      = Field.integer
Field.num      = Field.number
Field.num2f    = Field.number:extend{ decimal=2, step=0.1 }

Field.num_spin = Field.number:extend{ widget='spin', step=1 }
Field.int_spin = Field.integer:extend{ widget='spin', step=1 }


--boolean
Field.boolean = Field:extend{ type='boolean', default=false, choice={'True', 'False'} }
Field.bool    = Field.boolean

--string
Field.string  = Field:extend{ type='string', default='' }
Field.str     = Field.string

--enum
Field.enum    = Field:extend{ type='integer', choice={'enum1','enum2'}, widget='enum'}

--flags
Field.flags   = Field:extend{ type='integer', choice={'flag1','flag2'}, widget='flag'}


--object
Field.reference = Field:extend{ default=false, reference=true }
Field.subobject = Field:extend{ default=false, reference=false, subobject=true }
Field.sub = Field.subobject
Field.ref = Field.reference

------
Meta.default = Meta:extend{ 
									labelInitialCapital=true									
								}

Meta.ref = Meta.default:extend{
									reference = true,
									subobject = false,
									defaultRefWidget = 'ref'
								}


--[[

BLEND_ENUM = {
	-- NORMAL = MOAIProp.BLEND_NORMAL,
	-- ADD = MOAIProp.BLEND_ADD,
	-- MULTIPLY = MOAIProp.BLEND_MULTIPLY,
	NORMAL = 1,
	ADD = 1,
	MULTIPLY = 1,
}

TILE_FLAGS={
	-- HIDE = MOAIGridSpace.TILE_HIDE,
	-- X_FLIP = MOAIGridSpace.TILE_X_FLIP,
	-- Y_FLIP = MOAIGridSpace.TILE_Y_FLIP,
	HIDE = 1,
	X_FLIP = 1,
	Y_FLIP = 1,
}

local function ModelTest()
	--@apple
	AppleModel=
		Model 'Apple' {
			--- meta
			Meta.ref { 
				valueChanged	=	'onModelValueChanged' ; --method name for target object;
				--
				defaultRefWidget='ref';
			};

			--- atomic value type
			Field.num 'x' ;
			Field.num 'y' ;
			Field.num 'z' ;

			Field.num2f 'price'		{ step=0.5, widget='spin', range={1.5, 5.0} };

			Field.int 'id' 				{ readonly=true };

			Field.bool 'checked' 	{ default=true, choice={'Yes','No'} };

			Field.str 'name'			{ default='apple' };

			--- enum
			Field.enum 'blend'		{ choice = BLEND_ENUM , default = 'NORMAL'};

			--- bitmask
			Field.flags 'flags'		{ choice = TILE_FLAGS , default = {'TILE_Y_FLIP', 'TILE_X_FLIP'} };

			--- reference value type
			Field.sub 'color' 		{ type='MOAIColor' };
			Field.sub 'size' 			{ type='Rect' };

			Field.ref 'owner' 		{ type='Person' };

			--- dynamic property
			Field.sub 'pos'				{ type='Vec3', 
															label='Position',  
															getter = function(obj) return Vec(obj.x, obj.y, obj.z) end,
															setter = function(obj,v) obj.x,obj.y,obj.z= v.x,v.y.v.z end
														}
		}
	print(MOAIJsonParser.encode(AppleModel))
end
]]