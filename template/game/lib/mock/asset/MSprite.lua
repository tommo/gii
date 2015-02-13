module ('mock')

local function MSpriteLoader( node )
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
	local features = {}
	local featureNames = {}

	if data.features then
		for i, entry in pairs( data.features ) do
			features[ entry.name ] = entry.id
			featureNames[ i ] = entry.name
		end
	end
	--load images
	local count = 0
	for id, name in pairs( data.atlases ) do
		count = count+1
		if count>1 then error("multiple image not supported") end

		local imgFile = node:getSiblingPath( name )
		local tex, texNode = loadAsset( imgFile )
		if not tex then 
			_error( 'cannot load sprite texture', imgFile )
			return nil
		end
		local mtex, uvRect = tex:getMoaiTextureUV() 
		textures[ count ] = mtex
		local tw, th = tex:getSize()
		local ox, oy = 0, 0 --todo
		texRects[ id ] = { tw, th, ox, oy } 
	end

	local deck = MOAIGfxMaskedQuadListDeck2D.new()
	--count parts
	local partCount = 0
	for frameId, frame in pairs( data.frames ) do
		partCount = partCount + #frame.parts
	end

	local moduleCount = table.len( data.modules )
	local frameCount = table.len( data.frames )
	--
	deck:reservePairs( partCount ) --one pair per frame component
	deck:reserveQuads( partCount ) --one quad per frame component
	deck:reserveUVQuads( moduleCount ) --one uv per module
	deck:reserveLists( frameCount ) --one list per frame

	deck:setTexture( textures[1] )

	local moduleIdToIndex = {}
	local frameIdToIndex  = {}
	local i = 0
	for id, m in pairs( data.modules ) do
		i = i + 1
		moduleIdToIndex[ id ] = i
		local x, y, w, h = unpack( m.rect )
		local texRect = texRects[ m.atlas ]
		local tw, th, ox, oy = unpack( texRect )
		local u0, v0, u1, v1 = (x+ox+0.1)/tw, (y+oy+0.1)/th, (x+ox+w)/tw, (y+oy+h)/th
		m.uv = {u0, v0, u1, v1}
		m.index = i
		deck:setUVRect( i, u0, v0, u1, v1 )
	end

	local partIdx = 1
	local i = 0
	for id, frame in pairs( data.frames ) do
		i = i + 1
		frameIdToIndex[ id ] = i
		local basePartId = partIdx
		frame.index = i
		for j, part in ipairs( frame.parts ) do
			local m = data.modules[ part[1] ]
			local ox, oy = part[2], part[3]
			local _, _, w, h = unpack( m.rect )
			local x0, y0 = ox, oy
			local x1, y1 = x0 + w, y0 + h
			-- deck:setRect( partIdx, x0 + ox, y0 + oy, x1 + ox, y1 + oy )
			deck:setRect( partIdx, x0, -y0, x1, -y1 )
			local featureBit = m.feature or 0
			deck:setPair( partIdx, m.index, partIdx, featureBit )
			partIdx = partIdx + 1
		end
		deck:setList( i, basePartId, partIdx - basePartId )
	end
	preloadIntoAssetNode( node:getChildPath('frames'), deck )

	--animations
	local EaseFlat   = MOAIEaseType.FLAT
	local EaseLinear = MOAIEaseType.LINEAR
	local animations = {}
	for id, animation in pairs( data.anims ) do
		local name = animation.name
		local sequence = animation.seq
		--create anim curve
		local indexCurve   = MOAIAnimCurve.new()
		local offsetXCurve = MOAIAnimCurve.new()
		local offsetYCurve = MOAIAnimCurve.new()
		local count = #sequence

		indexCurve   : reserveKeys( count + 1 )
		offsetXCurve : reserveKeys( count + 1 )
		offsetYCurve : reserveKeys( count + 1 )

		--TODO: support flags? or just forbid it!!!!
		local offsetEaseType = EaseLinear
		local ftime = 0
		for fid, f in ipairs( sequence ) do

			local frameId, delay, ox, oy = unpack( f )
			local frame = data.frames[ frameId ]
			offsetXCurve:setKey( fid, ftime, ox, offsetEaseType )
			offsetYCurve:setKey( fid, ftime, -oy, offsetEaseType )
			indexCurve  :setKey( fid, ftime, frame.index, EaseFlat )

			delay = math.max( delay, 1 )
			ftime = ftime + delay  --will use anim:setSpeed to fit real playback FPS

			if fid == count then --copy last frame to make loop smooth
				offsetXCurve:setKey( fid + 1, ftime, ox, offsetEaseType )
				offsetYCurve:setKey( fid + 1, ftime, -oy, offsetEaseType )
				indexCurve  :setKey( fid + 1, ftime, frame.index, EaseFlat )
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
		texture    = tex,
		features   = features,
		featureNames   = featureNames,
	}

	return sprite
end


registerAssetLoader( 'msprite', MSpriteLoader )
