module 'mock'

CLASS: PrefabContainer ( mock.Entity )
	:MODEL{
		'----';
		Field 'prefab' :asset( 'prefab' ) :set( 'setPrefab' );
		'----';
		Field 'resetLoc' :boolean() :onset( 'refreshPrefab' );
		Field 'resetScl' :boolean() :onset( 'refreshPrefab' );
		Field 'resetRot' :boolean() :onset( 'refreshPrefab' );
		'----';
		Field 'autoSpawn' :boolean();
		-- Field 'resetLayer' :boolean();
	}

registerEntity( 'PrefabContainer', PrefabContainer )

function PrefabContainer:__init()
	self.prefab   = false
	self.instance = false
	self.resetTransform = true
	self.resetLoc = true
	self.resetScl = false
	self.resetRot = false
	self.autoSpawn = true
	-- self.resetLayer = false
end

function PrefabContainer:refreshPrefab()
	if not self.loaded then return end

	if self.instance then
		self.instance:destroyWithChildrenNow()
		self.instance = false
	end
	
	if self.prefab then
		local instance = loadPrefab( self.prefab )
		if not instance then return end
		self:addInternalChild( instance )
		--todo: layer
		self.instance = instance
		if self.resetLoc then	instance:setLoc( 0,0,0 )	end
		if self.resetRot then	instance:setRot( 0,0,0 )	end
		if self.resetScl then	instance:setScl( 1,1,1 )	end
	end	
end

function PrefabContainer:setPrefab( path )
	self.prefab = path
	self:refreshPrefab()
end

function PrefabContainer:getInstance()
	return self.instance
end

function PrefabContainer:onLoad()
	self.loaded = true
	self:refreshPrefab()
end
