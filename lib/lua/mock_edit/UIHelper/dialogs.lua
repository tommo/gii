module 'mock_edit'

local dialogs = gii.importPythonModule 'gii.qt.dialogs'

function requestString( title, prompt )
	return dialogs.requestString( title, prompt )
end

function requestProperty( title, target )
	return dialogs.requestProperty( title, target )
end

function requestConfirm( title, msg, level )
	return dialogs.requestConfirm( title, msg, level )
end

function alertMessage( title, msg, level )
	return dialogs.alertMessage( title, msg, level )
end

function popInfo( title, msg )
	return alertMessage( title, msg or title, 'info' )
end

function popQuestion( title, msg )
	return alertMessage( title, msg or title, 'question' )
end

function popWarning( title, msg )
	return alertMessage( title, msg or title, 'warning' )
end

function popCritical( title, msg )
	return alertMessage( title, msg or title, 'critical' )
end

