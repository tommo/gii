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

local ATTR_ROTATE_QUAT  = MOAIProp. ATTR_ROTATE_QUAT

local ATTR_LOCAL_VISIBLE= MOAIProp. ATTR_LOCAL_VISIBLE
local ATTR_VISIBLE      = MOAIProp. ATTR_VISIBLE
local INHERIT_VISIBLE   = MOAIProp. INHERIT_VISIBLE

local ATTR_SHADER       = MOAIProp. ATTR_SHADER
local ATTR_BLEND_MODE   = MOAIProp. ATTR_BLEND_MODE
local ATTR_PARTITION    = MOAIProp. ATTR_PARTITION

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

function linkRot( p1, p2 )
	p1:setAttrLink( MOAIProp.ATTR_X_ROT, p2, MOAIProp.ATTR_X_ROT )
	p1:setAttrLink( MOAIProp.ATTR_Y_ROT, p2, MOAIProp.ATTR_Y_ROT )
	p1:setAttrLink( MOAIProp.ATTR_Z_ROT, p2, MOAIProp.ATTR_Z_ROT )
end

function linkScl( p1, p2 )
	p1:setAttrLink( MOAIProp.ATTR_X_SCL, p2, MOAIProp.ATTR_X_SCL )
	p1:setAttrLink( MOAIProp.ATTR_Y_SCL, p2, MOAIProp.ATTR_Y_SCL )
	p1:setAttrLink( MOAIProp.ATTR_Z_SCL, p2, MOAIProp.ATTR_Z_SCL )
end

function linkLoc( p1, p2 )
	p1:setAttrLink( MOAIProp.ATTR_X_LOC, p2, MOAIProp.ATTR_X_LOC )
	p1:setAttrLink( MOAIProp.ATTR_Y_LOC, p2, MOAIProp.ATTR_Y_LOC )
	p1:setAttrLink( MOAIProp.ATTR_Z_LOC, p2, MOAIProp.ATTR_Z_LOC )
end


function linkWorldLoc( p1, p2 )
	p1:setAttrLink( MOAIProp.ATTR_X_LOC, p2, MOAIProp.ATTR_WORLD_X_LOC )
	p1:setAttrLink( MOAIProp.ATTR_Y_LOC, p2, MOAIProp.ATTR_WORLD_Y_LOC )
	p1:setAttrLink( MOAIProp.ATTR_Z_LOC, p2, MOAIProp.ATTR_WORLD_Z_LOC )
end


function linkWorldScl( p1, p2 )
	p1:setAttrLink( MOAIProp.ATTR_X_SCL, p2, MOAIProp.ATTR_WORLD_X_SCL )
	p1:setAttrLink( MOAIProp.ATTR_Y_SCL, p2, MOAIProp.ATTR_WORLD_Y_SCL )
	p1:setAttrLink( MOAIProp.ATTR_Z_SCL, p2, MOAIProp.ATTR_WORLD_Z_SCL )
end


function linkPiv( p1, p2 )
	p1:setAttrLink( MOAIProp.ATTR_X_PIV, p2, MOAIProp.ATTR_X_PIV )
	p1:setAttrLink( MOAIProp.ATTR_Y_PIV, p2, MOAIProp.ATTR_Y_PIV )
	p1:setAttrLink( MOAIProp.ATTR_Z_PIV, p2, MOAIProp.ATTR_Z_PIV )
end

function clearLinkRot( p1 )
	p1:clearAttrLink( MOAIProp.ATTR_X_ROT )
	p1:clearAttrLink( MOAIProp.ATTR_Y_ROT )
	p1:clearAttrLink( MOAIProp.ATTR_Z_ROT )
end

function clearLinkScl( p1 )
	p1:clearAttrLink( MOAIProp.ATTR_X_SCL )
	p1:clearAttrLink( MOAIProp.ATTR_Y_SCL )
	p1:clearAttrLink( MOAIProp.ATTR_Z_SCL )
end

function clearLinkLoc( p1 )
	p1:clearAttrLink( MOAIProp.ATTR_X_LOC )
	p1:clearAttrLink( MOAIProp.ATTR_Y_LOC )
	p1:clearAttrLink( MOAIProp.ATTR_Z_LOC )
end

function clearLinkPiv( p1 )
	p1:clearAttrLink( MOAIProp.ATTR_X_PIV )
	p1:clearAttrLink( MOAIProp.ATTR_Y_PIV )
	p1:clearAttrLink( MOAIProp.ATTR_Z_PIV )
end


function linkTransform( p1, p2 )
	linkLoc( p1, p2 )
	linkScl( p1, p2 )
	linkRot( p1, p2 )
	linkPiv( p1, p2 )
end

function clearLinkTransform( p1 )
	clearLinkLoc( p1 )
	clearLinkScl( p1 )
	clearLinkRot( p1 )
	clearLinkPiv( p1 )
end

function inheritTransform( p1, p2 )
	return p1:setAttrLink ( INHERIT_TRANSFORM, p2, TRANSFORM_TRAIT )
end

function clearInheritTransform( p1 )
	p1:clearAttrLink( INHERIT_TRANSFORM )
end

function inheritColor( p1, p2 )
	return p1:setAttrLink ( INHERIT_COLOR, p2, COLOR_TRAIT )
end

function linkColor( p1, p2 )
	return p1:setAttrLink ( COLOR_TRAIT, p2, COLOR_TRAIT )
end

function inheritVisible( p1, p2 ) 
	return p1:setAttrLink ( INHERIT_VISIBLE, p2, ATTR_VISIBLE )
end

function inheritTransformColor( p1, p2 )
	inheritTransform( p1, p2 )
	return inheritColor( p1, p2 )
end

function inheritTransformColorVisible( p1, p2 )
	inheritTransformColor( p1, p2 )
	return inheritVisible( p1, p2 )
end

function inheritPartition( p1, p2 )
	p1:setAttrLink ( ATTR_PARTITION, p2, ATTR_PARTITION )
end

function inheritShader( p1, p2 )
	p1:setAttrLink ( ATTR_SHADER, p2, ATTR_SHADER )
end

function inheritAllPropAttributes( p1, p2 )
	inheritTransformColorVisible( p1, p2 )
	p1:setAttrLink ( ATTR_PARTITION, p2, ATTR_PARTITION )
	p1:setAttrLink ( ATTR_SHADER, p2, ATTR_SHADER )
	p1:setAttrLink ( ATTR_BLEND_MODE, p2, ATTR_BLEND_MODE )
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

getRotX,setRotX,seekRotX,moveRotX = genAttrFunctions(MOAITransform.ATTR_X_ROT)
getRotY,setRotY,seekRotY,moveRotY = genAttrFunctions(MOAITransform.ATTR_Y_ROT)
getRotZ,setRotZ,seekRotZ,moveRotZ = genAttrFunctions(MOAITransform.ATTR_Z_ROT)

getSclX,setSclX,seekSclX,moveSclX = genAttrFunctions(MOAITransform.ATTR_X_SCL)
getSclY,setSclY,seekSclY,moveSclY = genAttrFunctions(MOAITransform.ATTR_Y_SCL)
getSclZ,setSclZ,seekSclZ,moveSclZ = genAttrFunctions(MOAITransform.ATTR_Z_SCL)

getPivX,setPivX,seekPivX,movePivX = genAttrFunctions(MOAITransform.ATTR_X_PIV)
getPivY,setPivY,seekPivY,movePivY = genAttrFunctions(MOAITransform.ATTR_Y_PIV)
getPivZ,setPivZ,seekPivZ,movePivZ = genAttrFunctions(MOAITransform.ATTR_Z_PIV)

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

-- function copyTransform( t1, t2 )
-- 	t1:setLoc( t2:getLoc() )
-- 	t1:setScl( t2:getScl() )
-- 	t1:setRot( t2:getRot() )
-- end

----TODO: replace this with C++ functions!!!
function syncWorldLoc( t1, t2 )
	local x2,y2,z2 =  t2:getWorldLoc()
	local x1,y1,z1 =  t1:getWorldLoc()
	t1:addLoc( x2-x1, y2-y1, z2-z1 )
end

function syncWorldRot( t1, t2 )
	-- local rx2,ry2,rz2 = t2:getWorldDir()
	-- local rx1,ry1,rz1 = t1:getWorldDir()
	-- print( rz1, rz2 )
	-- t1:addRot( rx2-rx1, ry2-ry1, rz2-rz1 ) 
	local rz2 = t2:getWorldRot()
	local rz1 = t1:getWorldRot()
	t1:addRot( 0,0, rz2-rz1 )
end

function syncWorldScl( t1, t2 )
	local sx2,sy2,sz2 = t2:getWorldScl()
	local sx1,sy1,sz1 = t1:getWorldScl()
	local sx,sy,sz = t1:getScl()
	local kx,ky,kz
	kx = sx1 ~= 0 and sx2/sx1 or 1
	ky = sy1 ~= 0 and sy2/sy1 or 1
	kz = sz1 ~= 0 and sz2/sz1 or 1
	t1:setScl( sx*kx, sy*ky, sz*kz )
end

function syncWorldTransform( t1, t2 )	
	syncWorldLoc( t1, t2 )
	syncWorldRot( t1, t2 )
	syncWorldScl( t1, t2 )
end

function setPropBlend( prop, blend )
	if     blend == 'alpha'    then prop:setBlendMode( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA ) 
	elseif blend == 'add'      then prop:setBlendMode( BLEND_ADD )
	elseif blend == 'multiply' then prop:setBlendMode( BLEND_MULTIPLY )
	elseif blend == 'normal'   then prop:setBlendMode( BLEND_NORMAL )
	elseif blend == 'mask'     then prop:setBlendMode( GL_ZERO,GL_SRC_ALPHA )	
	elseif blend == 'solid'    then prop:setBlendMode( GL_ONE,GL_ZERO )
	elseif type(blend) == 'table' then
		local s, d = unpack( blend )
		prop:setBlendMode( s, d )
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
	local deck = option.deck
	if deck then 
		if type(deck) == 'string' then
			deck = mock.loadAsset( deck )
		end
		prop:setDeck( deck )
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

	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_X_LOC, 'LocX' )
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_Y_LOC, 'LocY' )
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_Z_LOC, 'LocZ' )
	
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_X_ROT, 'RotX' )
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_Y_ROT, 'RotY' )
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_Z_ROT, 'RotZ' )

	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_X_SCL, 'SclX' )
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_Y_SCL, 'SclY' )
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_Z_SCL, 'SclZ' )

	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_X_PIV, 'PivX' )
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_Y_PIV, 'PivY' )
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_Z_PIV, 'PivZ' )

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

	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_R_COL, 'ColorR' )
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_G_COL, 'ColorG' )
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_B_COL, 'ColorB' )
	_wrapAttrGetSetSeekMove( clas, propName, MOAIProp.ATTR_A_COL, 'Alpha' )
	_wrapAttrGetterBoolean( clas, propName, MOAIProp.ATTR_VISIBLE, 'isVisible' )

	return clas
end

