require 'mock'
function addLayer()
	local l = mock.game:addLayer( 'layer' )
	return l
end

function setLayerName( l, name )
	l:setName( name )
end


function moveLayerUp( l )
	local layers = mock.game.layers
	local i = table.find( layers, l )
	assert ( i )
	if i <= 1 then return end
	table.remove( layers, i )
	table.insert( layers, i - 1 , l )	
end

function moveLayerDown( l )
	local layers = mock.game.layers
	local i = table.find( layers, l )
	assert ( i )
	if i >= #layers then return end
	table.remove( layers, i )
	table.insert( layers, i + 1 , l )	
end

function removeLayer( l )
	mock.game:removeLayer( l )
end

