module 'mock'

_fontPlaceHolder = false

function getFontPlaceHolder()
	if _fontPlaceHolder then return _fontPlaceHolder end
	-- read the font in from the file
	local font = require 'mock.asset.arial'

	-- load the font image back in
	local buffer = MOAIDataBuffer.new()
	local dataString = require 'mock.asset.arial_png'
	buffer:setString( dataString )
	local image = MOAIImage.new ()
	image:loadFromBuffer( buffer )
	-- set the font image
	font:setCache ()
	font:setReader ()
	font:setImage ( image )
	font.size = 10
	-- local font = MOAIFont.new()
	_fontPlaceHolder = font
	return _fontPlaceHolder
end