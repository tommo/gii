CLASS: UpdateListener ()
	:MODEL{
		Field 'active' :boolean() :isset('Active');
	}

function UpdateListener:__init()
	self.active = true
end

function UpdateListener:isActive()
	return self.active
end

function UpdateListener:setActive( a )
	self.active = a ~= false
end

function UpdateListener:onStart()
	self._entity.scene:addUpdateListener( self )
end

function UpdateListener:onDetach( entity )
	entity.scene:removeUpdateListener( self )
end

function UpdateListener:onUpdate( dt )
end

function UpdateListener:stop()
	self._entity:detach( self )
end