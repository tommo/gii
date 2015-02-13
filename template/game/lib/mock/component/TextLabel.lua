module 'mock'

local getBuiltinShader          = MOAIShaderMgr. getShader
local DECK2D_TEX_ONLY_SHADER    = MOAIShaderMgr. DECK2D_TEX_ONLY_SHADER
local DECK2D_SHADER             = MOAIShaderMgr. DECK2D_SHADER
local FONT_SHADER               = MOAIShaderMgr. FONT_SHADER

CLASS: TextLabel ( RenderComponent )
	:MODEL{
		'----';
		Field 'text'          :string()  :set('setText') :widget('textbox');
		'----';
		Field 'stylesheet'    :asset('stylesheet') :getset( 'StyleSheet');
		Field 'defaultStyle'  :string()  :label('default') :set('setDefaultStyle') :selection( 'getStyleNames' );
		'----';
		Field 'rectLimit'     :boolean() :set( 'setRectLimit' ); --TODO:update this
		Field 'size'          :type('vec2') :getset( 'Size' );
		Field 'alignment'     :enum( EnumTextAlignment )  :set('setAlignment')  :label('align H');
		Field 'alignmentV'    :enum( EnumTextAlignmentV ) :set('setAlignmentV') :label('align V');
		Field 'wordBreak'     :boolean()  :set('setWordBreak') :label('break word');
	}

function TextLabel:__init(  )
	local box = MOAITextBox.new()
	box:setStyle( getFallbackTextStyle() )
	box:setScl( 1,-1,1 )
	self.box  = box
	self.text = ''
	self.blend = 'alpha'
	self.alignment  = 'left'
	self.alignmentV = 'top'
	self:setSize( 100, 100 )
	self.defaultStyle = 'default'
	self.styleSheet = false
	self:setStyleSheet( getDefaultStyleSheet() )
	self.rectLimit = true
	self:useDeckShader()	
	self.wordBreak = false
	-- self:useFontShader()
end

function TextLabel:onAttach( entity )
	entity:_attachProp( self.box )
end

function TextLabel:onDetach( entity )
	entity:_detachProp( self.box )
end

--------------------------------------------------------------------
function TextLabel:setBlend( b )
	self.blend = b
	setPropBlend( self.box, b )
end

function TextLabel:setWordBreak( wbreak )
		self.wordBreak = wbreak
		self.box:setWordBreak( wbreak and MOAITextLabel.WORD_BREAK_CHAR or MOAITextLabel.WORD_BREAK_NONE )
	end

local defaultShader = MOAIShaderMgr.getShader( MOAIShaderMgr.DECK2D_SHADER )
function TextLabel:setShader( shaderPath )
	self.shader = shaderPath	
	if shaderPath then
		local shader = mock.loadAsset( shaderPath )
		if shader then
			local moaiShader = shader:getMoaiShader()
			return self.prop:setShader( moaiShader )
		end
	end
	self.prop:setShader( defaultShader )
end

--------------------------------------------------------------------
function TextLabel:setDefaultStyle( styleName )
	self.defaultStyle = styleName or 'default'
	self:updateStyles()
end

function TextLabel:setStyleSheet( sheetPath ) 
	local box = self.box
	self.styleSheetPath = sheetPath
	self.styleSheet = loadAsset( sheetPath )
	self:updateStyles()
end

function TextLabel:updateStyles()
	if self.styleSheet then
		self.styleSheet:applyToTextBox( self.box, self.defaultStyle )	
	end
end

function TextLabel:getStyleSheet()
	return self.styleSheetPath
end

function TextLabel:getStyleNames()
	local sheet = mock.loadAsset( self.styleSheetPath )
	if not sheet then return nil end
	local result = {}
	for i, name in pairs( sheet:getStyleNames() ) do
		table.insert( result, { name, name } )
	end
	return result
end

function TextLabel:setRectLimit( limit )
	self.rectLimit = limit
	self:updateRect()
end

function TextLabel:getSize()
	return self.w, self.h
end

function TextLabel:setSize( w, h )
	if w == false then
		self.rectLimit = false
	else
		self.w = w or 100
		self.h = h or 100
	end
	self:updateRect()
end

function TextLabel:updateRect()
	if not self.rectLimit then
		self.box:setRectLimits( false, false )
	else
		local w, h = self.w, self.h
		local alignH = self.alignment
		local alignV = self.alignmentV
		local x,y
		if alignH == 'left' then
			x = 0
		elseif alignH == 'center' then
			x = -w/2
		else --'right'
			x = -w
		end
		if alignV == 'top' then
			y = 0
		elseif alignV == 'center' then
			y = -h/2
		else --'right'
			y = -h
		end
		self.box:setRect( x, y, x + w, y + h )
	end
	self.box:setString( self.text ) --trigger layout
end
	
function TextLabel:setText( text )
	self.text = text or ''
	self.box:setString( text )
end

function TextLabel:setTextf( pattern, ... )
	return self:setText( string.format( pattern, ... ) )
end

function TextLabel:getText( )
	return self.text
end

function TextLabel:appendText( text )
	return self.text .. text
end

function TextLabel:appendTextf( pattern, ... )
	return self:appendText( string.format( pattern, ... ) )
end

--------------------------------------------------------------------
local textAlignments = {
	center    = MOAITextLabel.CENTER_JUSTIFY,
	left      = MOAITextLabel.LEFT_JUSTIFY,
	right     = MOAITextLabel.RIGHT_JUSTIFY,
	top       = MOAITextLabel.TOP_JUSTIFY,
	bottom    = MOAITextLabel.BOTTOM_JUSTIFY,
	baseline  = MOAITextLabel.BASELINE_JUSTIFY,
}

function TextLabel:setAlignment( align )
	align = align or 'left'
	self.alignment = align
	return self:_updateAlignment()
end

function TextLabel:setAlignmentV( align )
	align = align or 'top'	 
	self.alignmentV = align
	return self:_updateAlignment()
end

function TextLabel:_updateAlignment()	
	self.box:setAlignment( textAlignments[ self.alignment ], textAlignments[ self.alignmentV ] )
	return self:updateRect()
end

function TextLabel:getBounds()
	return self.box:getBounds()	
end

function TextLabel:drawBounds()
	GIIHelper.setVertexTransform( self._entity:getProp() )
	if self.rectLimit then
		local x1,y1, x2,y2 = self.box:getRect()	
		MOAIDraw.drawRect( x1,-y1,x2,-y2 )
	end
end

function TextLabel:inside( x, y, z, pad )
	return self.box:inside( x,y,z, pad )	
end

function TextLabel:setScissorRect( s )
	self.box:setScissorRect( s )
end

function TextLabel:useFontShader()
	self.box:setShader( getBuiltinShader(FONT_SHADER) )
end

function TextLabel:useDeckShader()
	self.box:setShader( getBuiltinShader(DECK2D_SHADER) )
end

--------------------------------------------------------------------
local defaultShader = MOAIShaderMgr.getShader( MOAIShaderMgr.DECK2D_SHADER )
function TextLabel:setShader( shaderPath )
	self.shader = shaderPath	
	if shaderPath then
		local shader = mock.loadAsset( shaderPath )
		if shader then
			local moaiShader = shader:getMoaiShader()
			return self.box:setShader( moaiShader )
		end
	end
	self.box:setShader( defaultShader )
end

registerComponent( 'TextLabel', TextLabel )
registerEntityWithComponent( 'TextLabel', TextLabel )
wrapWithMoaiPropMethods( TextLabel, 'box' )
