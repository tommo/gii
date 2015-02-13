module 'mock'

local enumSpawnMethod = _ENUM_V {
	'root',
	'sibling',
	'child',
}

CLASS: PrefabSpawner ()
	:MODEL{
		Field 'prefab'         :asset('prefab');
		-- Field 'spanwName'         :string();
		'----';		
		Field 'copyLoc'        :boolean();
		Field 'copyRot'        :boolean();
		Field 'copyScl'        :boolean();
		'----';		
		Field 'autoSpawn'      :boolean();
		Field 'destroyOnSpawn' :boolean();
		Field 'spawnMethod'    :enum( enumSpawnMethod )
		-- Field 'spawnAsChild'   :boolean();
	}

registerComponent( 'PrefabSpawner', PrefabSpawner )
registerEntityWithComponent( 'PrefabSpawner', PrefabSpawner )

function PrefabSpawner:__init()
	self.prefab         = false
	self.autoSpawn      = true
	self.destroyOnSpawn = true
	self.spawnAsChild   = false
	self.copyLoc        = true
	self.copyScl        = false
	self.copyRot        = false
	self.spawnMethod    = 'child'
end

function PrefabSpawner:onStart( ent )
	if self.autoSpawn then
		self:spawn()
	end
end

function PrefabSpawner:spawn()
	local ent = self._entity
	local instance
	if self.prefab then
		instance = loadPrefab( self.prefab )
		if instance then
			local spawnMethod = self.spawnMethod
			if spawnMethod == 'child' then
				ent:addChild( instance )
				if self.copyLoc then	instance:setLoc( 0,0,0 )	end
				if self.copyRot then	instance:setRot( 0,0,0 )	end
				if self.copyScl then	instance:setScl( 1,1,1 )	end
			elseif spawnMethod == 'sibling' then
				ent:addSibling( instance )
				if self.copyLoc then	instance:setLoc( ent:getLoc() ) end
				if self.copyRot then	instance:setRot( ent:getRot() ) end
				if self.copyScl then	instance:setScl( ent:getScl() ) end
			elseif spawnMethod == 'root' then
				ent:getScene():addEntity( instance )				
				if self.copyLoc then	instance:setLoc( ent:getWorldLoc() ) end
				if self.copyRot then	instance:setRot( ent:getRot() ) end
				if self.copyScl then	instance:setScl( ent:getScl() ) end
			end
		end
	end
	if self.destroyOnSpawn then
		ent:destroy()
	end
	return instance
end
