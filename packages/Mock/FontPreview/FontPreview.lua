context        = false
-------
currentFont = false
currentFontSize = 20
currentText  ='Hello, GII!'

function onLoad()
	context = gii.createEditCanvasContext()
	context.layer:showDebugLines( false )
	-- MOAIDebugLines.setStyle ( MOAIDebugLines.TEXT_BOX, 1, 1, 1, 1, 1 )
	-- MOAIDebugLines.setStyle ( MOAIDebugLines.TEXT_BOX_LAYOUT, 1, 0, 0, 1, 1 )
	-- MOAIDebugLines.setStyle ( MOAIDebugLines.TEXT_BOX_BASELINES, 1, 1, 0, 0, 1 )
	textbox=MOAITextBox.new()
	textbox:setYFlip( true )
	textbox:setBlendMode( MOAIProp.GL_SRC_ALPHA,MOAIProp.GL_ONE_MINUS_SRC_ALPHA ) 
	textbox:setShader( MOAIShaderMgr.getShader(MOAIShaderMgr.FONT_SHADER) )

	context:insertProp(textbox)	
end

function onResize(w,h)
	context:resize(w,h)
	textbox:setRect(-w/2 ,-h/2, w/2, h/2)	
end

function updateText()
	local style = MOAITextStyle.new()
	style:setFont( currentFont )
	style:setSize( currentFontSize )
	style:setColor( 1,1,1,1 )
	textbox:setStyle( style )
	textbox:setString( currentText )
	textbox:forceUpdate()
	_owner:updateCanvas()
end

function setFont( path )
	currentFont, node = mock.loadAsset( path )
	if not currentFont then return end
	if node.type == 'font_bmfont' then
		textbox:setShader( MOAIShaderMgr.getShader(MOAIShaderMgr.DECK2D_SHADER) )
	else
		textbox:setShader( MOAIShaderMgr.getShader(MOAIShaderMgr.FONT_SHADER) )
	end

	currentFontSize = currentFont.size or currentFontSize
	updateText()
end

function setFontSize( size )
	currentFontSize = size
	updateText()
end

function setText( text )
	currentText = text
	updateText()
end

