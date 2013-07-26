context        = false
-------
currentSheet = false
currentFont = false
currentFontSize = 20
currentText  ='Hello, GII!'
currentDefault = false
function recreateTextBox()
	textbox=MOAITextBox.new()
	textbox:setYFlip( true )

	textbox:setBlendMode( MOAIProp.GL_SRC_ALPHA,MOAIProp.GL_ONE_MINUS_SRC_ALPHA ) 
	textbox:setShader( MOAIShaderMgr.getShader(MOAIShaderMgr.FONT_SHADER) )
	local w,h =context:getSize()
	textbox:setRect(-w/2 ,-h/2, w/2, h/2)	
	context:insertProp(textbox)	
end

function onLoad()
	context = gii.createEditCanvasContext()
	context.layer:showDebugLines( true )
	-- MOAIDebugLines.setStyle ( MOAIDebugLines.TEXT_BOX, 1, 1, 1, 1, 1 )
	-- MOAIDebugLines.setStyle ( MOAIDebugLines.TEXT_BOX_LAYOUT, 1, 0, 0, 1, 1 )
	-- MOAIDebugLines.setStyle ( MOAIDebugLines.TEXT_BOX_BASELINES, 1, 1, 0, 0, 1 )
	recreateTextBox()
end

function onResize(w,h)
	context:resize(w,h)
	textbox:setRect(-w/2 ,-h/2, w/2, h/2)	
end

function updateText()
	if currentAlign=='Align Left' then
		textbox:setAlignment( MOAITextBox.LEFT_JUSTIFY )
	elseif currentAlign=='Align Right' then
		textbox:setAlignment( MOAITextBox.RIGHT_JUSTIFY )
	elseif currentAlign=='Align Center' then
		textbox:setAlignment( MOAITextBox.CENTER_JUSTIFY )
	end

	textbox:setString( currentText or '' )
	textbox:forceUpdate()

	_owner:updateCanvas()
end

function setText( text )
	currentText = text
	updateText()
end

function setAlign( align )
	currentAlign = align
	updateText()
end

local _fu = gii.fromUnicode

local function createStyle( data )
	local style = MOAITextStyle.new()
	local name = _fu(data.name)
	local font = mock.loadAsset( _fu(data.font) )
	local size = data.size
	local color = gii.listToTable(data.color)
	style:setFont( font )
	style:setSize( size )
	style:setColor( unpack(color) )
	return name, style
end

function setStyleSheet( sheet )
	recreateTextBox()
	currentSheet = sheet
	local styles = sheet.styles
	currentDefault = false
	for data in python.iter( styles ) do
		local name, style = createStyle( data )
		if not currentDefault or name == 'default' then
			currentDefault = name
			textbox:setStyle( style )			
		end
		textbox:setStyle( name, style )
	end
	updateText()
end

function updateStyle( data )
	if not currentSheet then return end
	local name, style = createStyle( data )
	textbox:setStyle( name, style )
	if currentDefault == name then
		textbox:setStyle( style )
	end
	textbox:forceUpdate()
	_owner:updateCanvas()
end
