module 'mock'

local defaultTextStyle = MOAITextStyle.new()
defaultTextStyle:setFont( getFontPlaceHolder() )
defaultTextStyle:setSize( 10 )

local textAlignments={
	center=MOAITextBox.CENTER_JUSTIFY,
	left=MOAITextBox.LEFT_JUSTIFY,
	right=MOAITextBox.RIGHT_JUSTIFY
}

local function countLine(s)
	local c = 0
	for _ in s:gmatch('\n') do
		c=c+1
	end
	return c
end

local function fitTextboxString( box, text, align)
	local style    = box:getStyle()
	local size     = style:getSize() * style:getScale()
	local textSize = #text
	local lines    = countLine(text) + 1
	if align=='center' then
		box:setRect( rectCenter( 0, 0, size * textSize, size * lines * 1.4 ) )
	elseif align=='right' then
		box:setRect( rect( 0, 0, -size * textSize, -size * lines * 1.4 ) )
	else
		box:setRect( rect( 0, 0, size * textSize, -size * lines * 1.4 ) )
	end
	box:setString( text )
end

---TextBox declarative creator
function TextBox( option )
	local box = MOAITextBox.new()

	box:setYFlip ( true )

	if option then
		local style = option.style or defaultTextStyle
		local hasfont = false
		---font style
		if style then
			if type(style) == 'table' then
				local defaultStyle = false
				for k, v in pairs( style ) do
					box:setStyle( k, v )
					if not defaultStyle then defaultStyle = v end
					if k=='default' then
						hasfont = true
						defaultStyle = v
					end
				end
				if defaultStyle then
					box:setStyle( defaultStyle )
				end
			else
				box:setStyle(style)
			end
		else
			local defaultSize = 20
			if option.font then
				hasfont = true
				defaultSize = option.font.size or 20
				box:setFont( option.font )
			end
			assert(hasfont,'No Font for textbox')
			local size = option.size or defaultSize
			box:setTextSize(size)
		end
		---format
		if option.align then 
			box:setAlignment( textAlignments[ option.align ] )
		end
		if option.lineSpacing then
			box:setLineSpacing( option.lineSpacing )
		end
		local text = option.text or option.string or ''
		---rect
		if option.rect then
			local x,y,x1,y1 = unpack( option.rect )
			if not x1 then x, y, x1, y1 = 0, 0, x, y end
			box:setRect( x, y, x1, y1 )
		else
			if option.autofit ~= false and #text >1 then
				fitTextboxString( box, text, option.align )
			end
		end
		box:setString( text )
		if not option.shader then option.shader='color-tex' end
		setupMoaiProp( box, option )
	end

	return box
end


function setDefaultTextStyle( style )
	defaultTextStyle = style
end

function getDefaultTextStyle()
	return defaultTextStyle
end


--backward compatiblity?
function Entity:addTextBox( option )
	return self:attach ( TextBox(option) )
end
updateAllSubClasses( Entity )
