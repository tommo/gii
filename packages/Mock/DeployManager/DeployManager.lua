--------------------------------------------------------------------
config = mock_edit.DeployManagerConfig()

function loadDeployManagerConfig( configFile )
	local file = io.open( configFile, 'rb' )
	
	if not file then 
		_info('no deploy config file found')
		return
	end

	file:close()
	config:clear()
	mock.deserializeFromFile( config, configFile )
end

function saveDeployManagerConfig( configFile )
	mock.serializeToFile( config, configFile )
end


function getDeployTargetTypeRegistry()
	return mock_edit.getDeployTargetTypeRegistry()
end
