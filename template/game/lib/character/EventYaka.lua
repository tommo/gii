module 'character'

EnumYakaFightProjectileMessages = _ENUM_V {
	'projectile.launch',
}
CLASS: YakaEventMessageProjectile ( EventMessage )
	:MODEL{
		Field 'loc' :type('vec3') :getset('Loc');
		Field 'message' :enum( EnumYakaFightProjectileMessages );
	}

function YakaEventMessageProjectile:__init()
	self.name      = 'projectile'
	self.transform = MOAITransform.new()
	self.message   = 'projectile.launch'
end

function YakaEventMessageProjectile:setLoc( x,y,z )
	return self.transform:setLoc( x,y,z )
end

function YakaEventMessageProjectile:getLoc()
	return self.transform:getLoc()
end

function YakaEventMessageProjectile:onBuildGizmo()
	local giz = mock_edit.SimpleBoundGizmo()
	giz:setTarget( self )
	linkLoc( giz:getProp(), self.transform )	
	return giz
end

function YakaEventMessageProjectile:drawBounds()
	MOAIDraw.drawCircle( 0,0, 20 )
end

registerActionMessageEventType( 'projectile', YakaEventMessageProjectile )
-- --------------------------------------------------------------------

-- EnumYakaFightCommonMessages = _ENUM_V {
-- 	'attack.prepare',
-- 	'attack.execute',
-- 	'attack.start',
-- 	'attack.stop',
-- }

-- CLASS: YakaEventMessageCommon ( EventMessage )
-- 	:MODEL{
		
-- 	}
