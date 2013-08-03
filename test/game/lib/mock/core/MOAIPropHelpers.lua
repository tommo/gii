--------PriorityNameTable
local priorityNames = {}
function addPriorityName( t )
	for k, v in pairs( t ) do
		priorityNames[ k ] = v
	end
end

function getPriorityByName( name )
	return priorityNames[ name ]
end

function getPriorityNameTable()
	return priorityNames
end

-------------------
local GL_SRC_ALPHA              = MOAIProp. GL_SRC_ALPHA
local	GL_ONE_MINUS_SRC_ALPHA    = MOAIProp. GL_ONE_MINUS_SRC_ALPHA
local GL_ZERO                   = MOAIProp. GL_ZERO
local GL_ONE                    = MOAIProp. GL_ONE
local BLEND_NORMAL              = MOAIProp. BLEND_NORMAL --TINT
local	BLEND_ADD                 = MOAIProp. BLEND_ADD
local	BLEND_MULTIPLY            = MOAIProp. BLEND_MULTIPLY
local DEPTH_TEST_DISABLE        = MOAIProp. DEPTH_TEST_DISABLE
local DEPTH_TEST_NEVER          = MOAIProp. DEPTH_TEST_NEVER
local DEPTH_TEST_ALWAYS         = MOAIProp. DEPTH_TEST_ALWAYS
local DEPTH_TEST_LESS           = MOAIProp. DEPTH_TEST_LESS
local DEPTH_TEST_LESS_EQUAL     = MOAIProp. DEPTH_TEST_LESS_EQUAL
local DEPTH_TEST_GREATER        = MOAIProp. DEPTH_TEST_GREATER
local DEPTH_TEST_GREATER_EQUAL  = MOAIProp. DEPTH_TEST_GREATER_EQUAL

local getBuiltinShader          = MOAIShaderMgr. getShader
local DECK2D_TEX_ONLY_SHADER    = MOAIShaderMgr. DECK2D_TEX_ONLY_SHADER
local DECK2D_SHADER             = MOAIShaderMgr. DECK2D_SHADER


----------ATTR HELPERS
local tmpNode  = MOAIColor.new()

local getAttr  = tmpNode.getAttr
local setAttr  = tmpNode.setAttr
local seekAttr = tmpNode.seekAttr
local moveAttr = tmpNode.moveAttr

local yield=coroutine.yield

local INHERIT_TRANSFORM = MOAIProp. INHERIT_TRANSFORM
local TRANSFORM_TRAIT   = MOAIProp. TRANSFORM_TRAIT

local INHERIT_LOC       = MOAIProp. INHERIT_LOC
local ATTR_TRANSLATE    = MOAIProp. ATTR_TRANSLATE

local INHERIT_COLOR     = MOAIProp. INHERIT_COLOR
local COLOR_TRAIT       = MOAIProp. COLOR_TRAIT 

local ATTR_VISIBLE      = MOAIProp. ATTR_VISIBLE
local INHERIT_VISIBLE   = MOAIProp. INHERIT_VISIBLE
local ACTUAL_VISIBLE    = MOAIProp. ACTUAL_VISIBLE

local ATTR_R_COL        = MOAIColor. ATTR_R_COL
local ATTR_G_COL        = MOAIColor. ATTR_G_COL
local ATTR_B_COL        = MOAIColor. ATTR_B_COL
local ATTR_A_COL        = MOAIColor. ATTR_A_COL

function extractColor(m)
	local r = getAttr( m, ATTR_R_COL )
	local g = getAttr( m, ATTR_G_COL )
	local b = getAttr( m, ATTR_B_COL )
	local a = getAttr( m, ATTR_A_COL )
	return r,g,b,a
end

function inheritLoc( p1, p2 )
	return p1:setAttrLink ( INHERIT_LOC, p2, TRANSFORM_TRAIT )
end

function inheritTransform( p1, p2 )
	return p1:setAttrLink ( INHERIT_TRANSFORM, p2, TRANSFORM_TRAIT )
end

function inheritColor( p1, p2 )
	return p1:setAttrLink ( INHERIT_COLOR, p2, COLOR_TRAIT )
end

--TODO: convert to support offical MOAI visiblity control
function inheritVisible( p1, p2 ) 
	return p1:setAttrLink ( INHERIT_VISIBLE, p2, ACTUAL_VISIBLE )
end

function inheritTransformColor( p1, p2 )
	inheritTransform( p1, p2 )
	return inheritColor( p1, p2 )
end

function inheritTransformColorVisible( p1, p2 )
	inheritTransformColor( p1, p2 )
	return inheritVisible( p1, p2 )
end

function alignPropPivot(p, align)  --align prop's pivot against deck
	local x,y,z,x1,y1,z1=p:getBounds()
	if align=='top' then
		p:setPivot(x,y1)
	end
	-- error('todo')
	--todo
end

local function genAttrFunctions(id)
	local src=[[
		return function(getAttr,setAttr,seekAttr,moveAttr,id)
			return 
				function(obj)                     --get
					return getAttr(obj,id)
				end,
				function(obj,value)               --set
					return setAttr(obj,id,value)
				end,
				function(obj,value,time,easetype) --seek
					return seekAttr(obj,id,value,time,easetype)
				end,
				function(obj,value,time,easetype) --move
					return moveAttr(obj,id,value,time,easetype)
				end
		end
	]]

	local tmpl=loadstring(src)()
	return tmpl(getAttr,setAttr,seekAttr,moveAttr,id)
end

getLocX,setLocX,seekLocX,moveLocX = genAttrFunctions(MOAITransform.ATTR_X_LOC)
getLocY,setLocY,seekLocY,moveLocY = genAttrFunctions(MOAITransform.ATTR_Y_LOC)
getLocZ,setLocZ,seekLocZ,moveLocZ = genAttrFunctions(MOAITransform.ATTR_Z_LOC)




------------Apply transform & other common settings
local setScl, setRot, setLoc, setPiv = extractMoaiInstanceMethods(
			MOAITransform,
			'setScl', 'setRot', 'setLoc', 'setPiv'
		)

function setupMoaiTransform( prop, transform )
	local loc = transform.loc 
	local rot = transform.rot
	local scl = transform.scl 
	local piv = transform.piv

	if loc then setLoc( prop, loc[1], loc[2], loc[3] ) end
	if rot then
		if type( rot )=='number' then
			setRot( prop, nil, nil, rot )
		else
			setRot( prop, rot[1], rot[2], rot[3] ) 
		end
	end
	if scl then setScl( prop, scl[1], scl[2], scl[3] ) end
	if piv then setPiv( prop, piv[1], piv[2], piv[3] ) end

	return prop
end

function setPropBlend( prop, blend )
	if     blend == 'alpha'    then prop:setBlendMode( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA ) 
	elseif blend == 'add'      then prop:setBlendMode( BLEND_ADD )
	elseif blend == 'multiply' then prop:setBlendMode( BLEND_MULTIPLY )
	elseif blend == 'normal'   then prop:setBlendMode( BLEND_NORMAL )
	elseif blend == 'mask'     then prop:setBlendMode( GL_ZERO,GL_SRC_ALPHA )	
	elseif blend == 'solid'    then prop:setBlendMode( GL_ONE,GL_ZERO )	
	end
end

function setupMoaiProp( prop, option )
	---------------PRIORITY
	local priority = option.priority
	if priority then
		local tt = type(priority)
		if tt == 'number' then
			prop:setPriority( priority )	
		elseif tt == 'string' then
			local p = priorityNames[ priority ]
			assert( p, 'priority name not found:'..priority )
			prop:setPriority( p )
		end
	end

	---------DEPTH MASK/Func
	local depthTest = option.depthTest
	if option.depthMask == false then	prop:setDepthMask( false ) end
	if depthTest then		
		if depthTest=='always' then
			prop:setDepthTest( DEPTH_TEST_ALWAYS )
		elseif depthTest=='greater' then
			prop:setDepthTest( DEPTH_TEST_GREATER )	
		else 
			prop:setDepthTest( DEPTH_TEST_LESS_EQUAL )	
		end
	-- else
	-- 	prop:setDepthTest( DEPTH_TEST_DISABLE )	
	end
	
	---------BLEND MODE
	local blend = option.blend or 'alpha'
	setPropBlend( prop, blend )
	
	----------SHADER
	local shader = option.shader
	if shader then
		local ts = type( shader )
		if ts == 'string' then
			if shader == 'tex' then
				prop:setShader( getBuiltinShader( DECK2D_TEX_ONLY_SHADER ) )
			elseif shader == 'color-tex' then
				prop:setShader( getBuiltinShader( DECK2D_SHADER ) )
			end
		else
			prop:setShader( shader )
		end
	end

	---------Deck
	if option.deck then 
		prop:setDeck( option.deck )
	elseif option.texture then
		prop:setTexture( option.texture )
	end

	---------COMMON
	if option.visible == false then prop:setVisible( false )	end
	if option.color then prop:setColor( unpack(option.color) ) end
	if option.index then prop:setIndex( option.index ) end
	
	local transform = option.transform
	if transform then return setupMoaiTransform( prop, transform ) end	
	
	return prop
end

injectMoaiClass( MOAIProp, {
	setupTransform = setupMoaiTransform,
	setupProp      = setupMoaiProp
	})


----------some method wrapper
function wrapWithMoaiTransformMethods( clas, propName )
	_wrapMethods(clas, propName, {
			'addLoc',
			'addRot',
			'addScl',
			'addPiv',
			'moveLoc',
			'movePiv',
			'moveRot',
			'moveScl',
			
			'setScl',
			'setLoc',
			'setRot',
			'setPiv',
			'getScl',
			'getLoc',
			'getRot',
			'getPiv',

			'setIndex',
			'getIndex',

			'getWorldScl',
			'getWorldLoc',
			'getWorldRot',
			'getWorldDir',

			'seekScl',
			'seekLoc',
			'seekRot',
			'seekPiv',

			'seekAttr',
			'setAttr',
			'moveAttr',

			'forceUpdate',
			'scheduleUpdate',

			'worldToModel',
			'modelToWorld',

			'setBillboard',
			'modelToWorld',


		})

	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_X_LOC, 'LocX' )
	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_Y_LOC, 'LocY' )
	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_Z_LOC, 'LocZ' )
	
	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_X_ROT, 'RotX' )
	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_Y_ROT, 'RotY' )
	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_Z_ROT, 'RotZ' )

	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_X_SCL, 'SclX' )
	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_Y_SCL, 'SclY' )
	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_Z_SCL, 'SclZ' )

	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_X_PIV, 'PivX' )
	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_Y_PIV, 'PivY' )
	_wrapAttrGetSet( clas, propName, MOAIProp.ATTR_Z_PIV, 'PivZ' )

	return clas
end

function wrapWithMoaiPropMethods( clas, propName )
	
	wrapWithMoaiTransformMethods( clas, propName )

	_wrapMethods(clas, propName, {
			'setColor',
			'seekColor',
			'setVisible',
			'inside',
		})

	_wrapAttrGetter( clas, propName, MOAIProp.ATTR_A_COL, 'getAlpha' )
	_wrapAttrSetter( clas, propName, MOAIProp.ATTR_A_COL, 'setAlpha' )
	_wrapAttrGetter( clas, propName, MOAIProp.ATTR_VISIBLE, 'isVisible' )

	return clas
end

