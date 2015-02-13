if not MOAIBox2DBody then return end

local insert = table.insert
local setmetatable = setmetatable

--------------------------------------------------------------------
local defaultBodysettings={
	type           = 'dynamic',
	angularDamping = 0,
	linearDamping  = 0,
	bullet         = false,
	fixedRotation  = false
}

local bodySettingsMT = {__index=defaultBodysettings}

local defaultMaterial={
	name        = 'default',
	restitution = 1,
	friction    = 0,
	density     = 5,
	sensor      = false,
	coltype     = 1,
	collision   = false
}

local materialSettingMT = {__index=defaultMaterial}

local bodyType={
	['dynamic']   = MOAIBox2DBody.DYNAMIC,
	['static']    = MOAIBox2DBody.STATIC,
	['kinematic'] = MOAIBox2DBody.KINEMATIC
}

--------------------------------------------------------------------
local collisionHandler=function( phase, fixa, fixb, arb )
	local body   = fixa:getBody()
	local owner  = body.owner
	local onCollision = owner and owner.onCollision
	if onCollision then 
		return onCollision( owner, phase, fixa, fixb, arb )
	end
end

--------------------------------------------------------------------
local function addB2Shape( body, shapeSetting, resetMass )
	local shapeType = shapeSetting.type
	local shape
	if     shapeType == 'circle' then
		shape = body:addCircle( unpack( shapeSetting.data ) ) -- x,y, radius
	elseif shapeType == 'rect' then
		shape = body:addRect( unpack( shapeSetting.data ) )   -- x0, y0, x1, y1
	elseif shapeType == 'polygon' then
		shape = body:addPolygon( shapeSetting.data )          -- x[n],y[n], ...
	elseif shapeType == 'edges' then
		shape = body:addEdges( shapeSetting.data )            -- x[n],y[n], ...
	else
		error('unkown shape type')
	end

	local mat = shapeSetting.material and setmetatable( shapeSetting.material, materialSettingMT ) or defaultMaterial
	if shapeType ~= 'edges' then
		shape:setDensity     ( mat.density     )
		shape:setSensor      ( mat.sensor      )
		shape:setFriction    ( mat.friction    )
		shape:setRestitution ( mat.restitution )
	end
	
	if mat.category or mat.mask or mat.group then 
		shape:setFilter(mat.category or 1, mat.mask,mat.group)
	end

	shape.material = mat
	shape.body     = body
	shape.name = shapeSetting.name or k
	insert( body.shapes, shape )

	if resetMass~=false then 
		body:resetMassData()
	end

	--collision handler
	local collision = shapeSetting.collision
	if collision == nil then collision = mat.collision or false end
	if collision then
		shape:setCollisionHandler(
				collisionHandler,
				mat.collisionPhaseMask or shapeSetting.collisionPhaseMask or (MOAIBox2DArbiter.ALL),
				shapeSetting.collisionCategoryMask or mat.collisionCategoryMask
			)
	end

	return shape
end

local function attachB2Body( body, owner )
	local prop = owner:getProp()
	prop:forceUpdate()
	local tx, ty  = owner:getWorldLoc()
	local _, _, rz = prop:getRot()
	body:setTransform( tx, ty, rz )
	
	if owner.parent then
		prop:clearAttrLink( MOAIProp.INHERIT_TRANSFORM )
	end
	
	body.owner = owner	
	inheritTransform( prop, body )

	prop:setLoc(0,0)
	prop:setRot(0)
	body:forceUpdate()
	body:setActive( true )

	return body
end

local function detachB2Body( body, owner )
	body.owner = nil	
	body.shapes = nil
	body:destroy()
end

local function getOwner( body )
	return self.owner
end

local function getShapes()
	return self.shapes
end

local function getShape( name )
	for i,s in pairs( self.shapes ) do
		if s.name == name then return s end
	end
	return nil
end

--------------------------------------------------------------------
injectMoaiClass( MOAIBox2DBody, {
	addShape  = addB2Shape,
	onAttach  = attachB2Body,
	onDetach  = detachB2Body,
	getOwner  = getOwner,
	getShapes = getShapes,
	getShape  = getShape,
})
--------------------------------------------------------------------

function Box2DBody( settings )
	settings = settings and setmetatable( settings, bodySettingsMT ) or defaultBodysettings
	local body = game.b2world:addBody(
		bodyType[ settings.type ] or MOAIBox2DBody.DYNAMIC
		)
	
	body:setFixedRotation  ( settings.fixedRotation  )
	body:setAngularDamping ( settings.angularDamping )
	body:setLinearDamping  ( settings.linearDamping  )
	body:setBullet         ( settings.bullet         )

	body.name = settings.name

	body.shapes = {}

	if settings.shapes then
		for _, shapeSetting in pairs(settings.shapes) do
			body:addShape( shapeSetting, false )
		end
		body:resetMassData()
	end
	body:setActive( false ) --only get activated when get attached
	return body
end
