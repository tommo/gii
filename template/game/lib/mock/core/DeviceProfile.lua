module 'mock'

CLASS: DeviceProfile ()
	:MODEL{
		Field 'name';
		Field 'screenProfiles' :array( ScreenProfile );
	}

function DeviceProfile:getAttr( key ) --for capacity query
	return nil
end


