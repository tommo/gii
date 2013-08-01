context        = false
-------
currentFont = false
currentFontSize = 20
currentFontColor = {1,1,1,1}
currentText  ='Hello, Gii!'

function onLoad()
	context = gii.createEditCanvasContext()
	context.layer:showDebugLines( false )
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
	if not currentFont then return end

	local style = MOAITextStyle.new()
	style:setFont( currentFont )
	style:setSize( currentFontSize )
	style:setColor( unpack(currentFontColor) )
	textbox:setStyle( style )
	textbox:setString( currentText )
	textbox:forceUpdate()
	_owner:updateCanvas()
end

function updatePreview()
end


function updateStyle( data )
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

function setFont( fontPath )
	currentFont = mock.loadAsset(fontPath)
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

function setFontColor( r,g,b,a )
	currentFontColor = {r,g,b,a}
	updateText()
end