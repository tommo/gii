module 'mock_edit'

--TODO: use a global configure for this
local ColorTable   = {}
local defaultColor = { 1,1,1,1 }

function addColor( name, r,g,b,a )
	ColorTable[ name ] = {r,g,b,a}
end

function addHexColor( name, hex, alpha )
	return addColor( name, hexcolor(hex, alpha) )
end

function applyColor( name )
	MOAIGfxDevice.setPenColor( getColor( name ) )
end

function getColor( name, state )
	local fullname = name
	if state then
		fullname = name .. ':' .. state
		local color = ColorTable[ fullname ]
		if color then 
			return unpack( color )
		end
	end
	local color = ColorTable[ name ] or defaultColor
	return unpack( color )
end
