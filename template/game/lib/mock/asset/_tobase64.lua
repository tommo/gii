local buffer = MOAIDataBuffer.new()
print( buffer:load( 'null.ttf' ) )
print( buffer:getString() )
buffer:base64Encode()
buffer:setString( 
	string.format(
[[
	local data = MOAIDataBuffer.new()
	data:setString( '%s' )
	data:base64Decode()
	return data
]],
	buffer:getString()
	)
)

buffer:save( 'null_ttf.lua' )