--------------------------------------------------------------------

CLASS: Vec3 ()
	:MODEL{
		Field 'x': type('number') ;
		Field 'y': type('number') ;
		Field 'z': type('number') ;
	}
function Vec3:__init( x, y, z )
	self.x = x or 0 
	self.y = y or 0 
	self.z = z or 0 
end

function Vec3:unpack()
	return self.x, self.y, self.z
end

local function getMoaiLoc( prop )
	return Vec3( prop:getLoc() )
end

local function getMoaiRot( prop )
	return Vec3( prop:getRot() )
end

local function getMoaiScl( prop )
	return Vec3( prop:getScl() )
end

local function setMoaiLoc( prop, loc )
	return prop:setLoc( loc:unpack() )
end

local function setMoaiRot( prop, rot )
	return prop:setRot( rot:unpack() )
end

local function setMoaiScl( prop, scl )
	return prop:setScl( scl:unpack() )
end

-- CLASS: Vec2 ()
-- 	:MODEL{
-- 		Field 'x': type('number') ;
-- 		Field 'y': type('number') ;
-- 	}

Model( MOAIProp, 'MOAIProp' ):update{
	Field 'Loc' :type( Vec3 ) :get( getMoaiLoc ) :set( setMoaiLoc ) ;
	Field 'Rot' :type( Vec3 ) :get( getMoaiRot ) :set( setMoaiRot ) ;
	Field 'Scl' :type( Vec3 ) :get( getMoaiScl ) :set( setMoaiScl ) ;
}



