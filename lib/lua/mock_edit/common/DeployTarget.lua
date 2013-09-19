module 'mock_edit'

--------------------------------------------------------------------
CLASS: DeployTarget ()
	:MODEL{		
		Field "name"      :string() :noedit();
		Field "lastBuild" :int()    :noedit(); --timestamp
		Field "state"     :string() :noedit();		
	}
function DeployTarget:__init()
	self.name = 'TARGET'
end

function DeployTarget:getIcon()
	return nil
end

function DeployTarget:getType()
	return "target"
end

--------------------------------------------------------------------
local deployTargetTypeRegistry = {}

function registerDeployTargetType( name, targetClass )
	deployTargetTypeRegistry[ name ] = targetClass
end

function getDeployTargetTypeRegistry()
	return deployTargetTypeRegistry
end

--------------------------------------------------------------------
CLASS: DeploySceneEntry ()
	:MODEL{
		Field 'path'  :string();
		Field 'alias' :string();
		Field 'entry' :boolean();
	}

---------------------------------------------------------------------
CLASS: DeployManagerConfig ()
	:MODEL{
		Field 'scenes'  :array( DeploySceneEntry );
		Field 'targets' :array( DeployTarget );
	}

function DeployManagerConfig:__init()
	self.scenes  = {}
	self.targets = {}
end

function DeployManagerConfig:addDeployTarget( typeName )
	local clas = deployTargetTypeRegistry[ typeName ]
	assert( clas )
	local target = clas()
	table.insert( self.targets, target )
	return target
end

function DeployManagerConfig:removeDeployTarget( target )
	for i,t in ipairs( self.targets ) do
		table.remove( self.targets, i )
		break
	end
end

function DeployManagerConfig:clear()
	self.scenes  = {}
	self.targets = {}
end

function DeployManagerConfig:getTargets()
	return self.targets
end