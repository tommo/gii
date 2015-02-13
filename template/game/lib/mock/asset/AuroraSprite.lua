module ('mock')

local function AuroraSpriteLoader( node )
	--[[
		sprite <package>
			.moduletexture <texture>
			.modules <uvquad[...]>
			.frames  <deck_quadlist>
	]]	
	local data = loadAssetDataTable( node:getObjectFile('def') )
	local textures = {}
	local texRects = {}
	local uvRects  = {}

	--load images
	for i, image in pairs( data.images ) do
		
		if i>1 then error("multiple image not supported") end

		local imgFile = node:getSiblingPath( image.file )
		local tex, texNode = loadAsset( imgFile )
		if not tex then 
			_error( 'cannot load sprite texture', imgFile )
			return nil
		end
		local mtex, uvRect = tex:getMoaiTextureUV() 
		textures[ i ] = mtex
		local tw, th = mtex:getSize()
		local ox, oy = 0, 0 --todo
		texRects[ i ] = { tw, th, ox, oy } 
		
	end

	local deck = MOAIGfxQuadListDeck2D.new()
	deck:reservePairs( data.partCount ) --one pair per frame component
	deck:reserveQuads( data.partCount ) --one quad per frame component
	deck:reserveUVQuads( #data.modules ) --one uv per module
	deck:reserveLists( #data.frames ) --one list per frame

	deck:setTexture( textures[1] )

	for i, m in ipairs( data.modules ) do
		if m.type == 'image' then
			local x, y, w, h = unpack( m.rect )
			local texRect = texRects[ m.image+1 ]
			local tw, th, ox, oy = unpack( texRect )
			local u0, v0, u1, v1 = (x+ox+0.1)/tw, (y+oy+0.1)/th, (x+ox+w)/tw, (y+oy+h)/th
			m.uv = {u0, v0, u1, v1}
			deck:setUVRect(i, u0, v0, u1, v1)
		end
	end

	local partId = 1
	for i, frame in ipairs( data.frames ) do
		local basePartId = partId
		for j, part in ipairs( frame.parts ) do
			local uvId = part.module
			local x0, y0, x1, y1 = unpack( part.rect )
			deck:setRect(partId, x0, -y1, x1, -y0)
			deck:setPair(partId, uvId, partId)
			partId = partId + 1
		end
		deck:setList( i, basePartId, partId - basePartId )
	end
	preloadIntoAssetNode( node:getChildPath('frames'), deck )

	--animations	
	local EaseFlat   = MOAIEaseType.FLAT
	local EaseLinear = MOAIEaseType.LINEAR
	local animations = {}
	for i, animation in ipairs( data.animations ) do
		local name = animation.name
		--create anim curve
		local indexCurve   = MOAIAnimCurve.new()
		local offsetXCurve = MOAIAnimCurve.new()
		local offsetYCurve = MOAIAnimCurve.new()
		local count = #animation.frames
		
		indexCurve  :reserveKeys( count + 1 )
		offsetXCurve:reserveKeys( count + 1 )
		offsetYCurve:reserveKeys( count + 1 )

		--TODO: support flags? or just forbid it!!!!
		local offsetEaseType = EaseLinear
		local ftime = 0
		for fid, frame in ipairs( animation.frames ) do			
			local ox, oy = unpack( frame.offset )
			offsetXCurve:setKey( fid, ftime, ox, offsetEaseType )
			offsetYCurve:setKey( fid, ftime, -oy, offsetEaseType )
			indexCurve  :setKey( fid, ftime, frame.id, EaseFlat )
			local delay = frame.time
			delay = math.max( delay, 1 )
			ftime = ftime + delay  --will use anim:setSpeed to fit real playback FPS

			if fid == count then --copy last frame to make loop smooth
				offsetXCurve:setKey( fid + 1, ftime, ox, offsetEaseType )
				offsetYCurve:setKey( fid + 1, ftime, -oy, offsetEaseType )
				indexCurve  :setKey( fid + 1, ftime, frame.id, EaseFlat )
			end
		end
		animations[ name ] = {
			offsetXCurve = offsetXCurve,
			offsetYCurve = offsetYCurve,
			indexCurve   = indexCurve,
			length       = ftime,
			name         = name,
		}
	end

	local sprite = {
		frameDeck  = deck,
		animations = animations,
		texture    = tex
	}

	return sprite
end


registerAssetLoader( 'aurora_sprite', AuroraSpriteLoader )
