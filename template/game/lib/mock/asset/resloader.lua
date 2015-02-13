--[[
* MOCK framework for Moai

* Copyright (C) 2012 Tommo Zhou(tommo.zhou@gmail.com).  All rights reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining
* a copy of this software and associated documentation files (the
* "Software"), to deal in the Software without restriction, including
* without limitation the rights to use, copy, modify, merge, publish,
* distribute, sublicense, and/or sell copies of the Software, and to
* permit persons to whom the Software is furnished to do so, subject to
* the following conditions:
*
* The above copyright notice and this permission notice shall be
* included in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
]]
require 'mock.asset.ParticleHelper'
require 'mock.asset.ParticleProcs'

globalTextScale=0.5
useScaledText=false
originTextSize=30

globalDeckScale=0.5
useHalfTexture=false

local strictResMT={
	__index=function(t,k)
		return error('RES NOT FOUND:'..k or 'NIL',2)
	end
}

local resFilePrefix = 'data/'
local resFlags = {}

function setResPrefix(p)
	resFilePrefix = p
end

function setResFlag(n,v)
	resFlags[n]=v==nil and true or v
end

local function extendTable(src,dst)
	for k,v in pairs(dst) do
		if src[k]==nil then src[k]=dst[k] end
	end
	return src
end

local function fixpath(p)
	p=string.gsub(p,'\\','/')
	return p
 end

local function extractDir(p)
	p=fixpath(p)
	return string.match(p, ".*/")
end

local ttype=function(o)
	local tt=type(o)
	if tt~='userdata' then return tt end
	if o.getClassName then
		return o:getClassName()
	end
	return tt
end

local defaultPatchLayout={
	rows={
		{0.25,false},
		{0.5,true},
		{0.25,false}
	},
	columns={
		{0.25,false},
		{0.5,true},
		{0.25,false}
	}
}

local defaultTextureOption={
	smooth=false,
	mipmap=false,
	wrap=false,
	bind=false
}

local textureTable={}

local function __releaseAllResource()
end


local function setTextureOption(tex,option)
	option = option and extendTable(option , defaultTextureOption) or defaultTextureOption
	
	if option.smooth then 
		tex:setFilter(
			option.mipmap and MOAITexture.GL_LINEAR_MIPMAP_LINEAR
				or	MOAITexture.GL_LINEAR
			)
	else
		tex:setFilter(
			option.mipmap and MOAITexture.GL_NEAREST_MIPMAP_NEAREST
				or	MOAITexture.GL_NEAREST
			)
	end

	tex:setWrap(option.wrap)
	return tex
end


local function loadTexture(option)
	local file=option.file
	local tex=MOAITexture.new()
	setTextureOption(tex,option)
	tex:load(resFilePrefix..option.file, option.transform or MOAIImage.TRUECOLOR)
	textureTable[file]=tex

	return tex
end

function getTextureTable()
	return textureTable
end

function affirmAllTextures()
	assert(game.gfx,'not initialized yet')
	for k,t in pairs(textureTable) do
		t:affirm()
	end
end

function releaseTextures()
	assert(game.gfx,'not initialized yet')
	for k,t in pairs(textureTable) do
		t:release()
	end
end

local function loadShader(option)
	local vsh,fsh=option.vsh,option.fsh

	local shader=MOAIShader.new()
	shader:load(vsh,fsh)
	if option.name then shader.name=option.name end

	--setup variables

	if option.onLoad then option.onLoad(shader)	end
	local attrs = option.attributes or {'position', 'uv', 'color'}
	if attrs then
		for i, a in ipairs(attrs) do
			assert(type(a)=='string')
			shader:setVertexAttribute(i,a)
		end
	end

	local uniforms=option.uniforms
	local uniformTable = {}
	if uniforms then
		local count=#uniforms
		shader:reserveUniforms(count)
		for i, u in ipairs(uniforms) do
			local utype=u.type
			local uvalue=u.value
			local name=u.name

			if utype=='float' then
				shader:declareUniformFloat(i, name, uvalue or 0)
			elseif utype=='int' then
				shader:declareUniformInt(i, name, uvalue or 0)			
			elseif utype=='color' then
				shader:declareUniform(i,name,MOAIShader.UNIFORM_COLOR)
			elseif utype=='sampler' then
				shader:declareUniformSampler(i, name, uvalue or 1)
			elseif utype=='transform' then
				shader:declareUniform(i,name, MOAIShader.UNIFORM_TRANSFORM)
			elseif utype=='pen_color' then
				shader:declareUniform(i,name,MOAIShader.UNIFORM_PEN_COLOR)
			elseif utype=='view_proj' then
				shader:declareUniform(i,name,MOAIShader.UNIFORM_VIEW_PROJ)
			elseif utype=='world_view_proj' then
				shader:declareUniform(i,name,MOAIShader.UNIFORM_WORLD_VIEW_PROJ)
			end
			uniformTable[ name ] = i
		end
	end
	shader.uniformTable = uniformTable

	local _setAttr = shader.setAttr
	function shader:setAttr( name, v )
		local tt = type( name )
		if tt == 'number' then return _setAttr( self, name, v )  end
		local ut = self.uniformTable
		local id = ut[ name ]
		if not id then error('undefined uniform:'..name, 2) end
		_setAttr( self, id, v )
	end

	local _setAttrLink = shader.setAttrLink
	function shader:setAttrLink( name, v )
		local tt = type( name )
		if tt == 'number' then return _setAttrLink( self, name, v )  end
		local ut = self.uniformTable
		local id = ut[ name ]
		if not id then error('undefined uniform:'..name, 2) end
		_setAttrLink( self, id, v )
	end

	return shader
end

function createFrameBuffer(w,h,option)
	local tex=MOAITexture.new()
	tex:initFrameBuffer(w,h)
	return setTextureOption(tex,option)
end


local function loadSound(option)
	local buf=MOAIUntzSampleBuffer.new()
	buf:load(resFilePrefix..option.file)
	return buf
end



local defaultGfxQuadOption={
	-- rect={0,0,32,32},
	-- uv={0,0,1,1}
}

local function _loadTexture(tex)
	local tt=ttype(tex)
	local realtex
	if tt=='string' then
		
		realtex=MOAITexture.new()
		setTextureOption(realtex,defaultTextureOption)

		realtex:load(resFilePrefix..tex)

	elseif tt=='MOAIDataBuffer' then
		realtex=MOAITexture.new()
		setTextureOption(realtex,defaultTextureOption)
		realtex:load(tex)
		
	elseif tt=='MOAITexture' then
		realtex=tex

	elseif tt=='table' then
		realtex=loadTexture(tex)
		
	else
		error('unknown texture type:'..tt)
	end
	return realtex
end


local floor=math.floor
local function _getQuadRect(origin,w,h,rotated)
	
	local x0,y0=0,0
	if type(origin)=='string' then
		if origin=='center' then 
			x0,y0=-w/2,-h/2
		elseif origin=='left-top' then
			x0,y0=0,0
		elseif origin=='left-center' then
			x0,y0=0,-h/2
		elseif origin=='left-bottom' then
			x0,y0=0,-h
		elseif origin=='right-top' then
			x0,y0=-w,0
		elseif origin=='right-center' then
			x0,y0=-w,-h/2
		elseif origin=='right-bottom' then
			x0,y0=-w,-h
		elseif origin=='center-top' then
			x0,y0=-w/2,0
		elseif origin=='center-center' then
			x0,y0=-w/2,-h/2
		elseif origin=='center-bottom' then
			x0,y0=-w/2,-h
		end
	elseif origin then
		x0,y0=-origin[1],-origin[2] 
	end
	local x1,y1=x0+w,y0+h

	
	if rotated then
		return floors(-y1,-x1,-y0,-x0)
	else
		return floors(x0,-y1,x1,-y0)
	end

	
end

local function loadGfxQuad(data)
	extendTable(data,defaultGfxQuadOption)
	local quad=MOAIGfxQuad2D.new()
	local tex=_loadTexture(data.texture)
	local w,h=tex:getSize()

	quad:setTexture(tex)
	quad.texture=tex
	local rect=data.rect
	if not rect then
		quad:setRect(_getQuadRect(data.origin,w,h,data.rotated or false))
	else
		quad:setRect(unpack(rect))
	end
	if data.uv then quad:setUVRect(unpack(data.uv)) end
	return quad
end

function loadSpriteSheet(t)
	local w,h=t.w or 32,t.h or 32
	local deck=MOAIGfxQuadDeck2D.new()
	local tex=_loadTexture(t.texture)
	local tw,th=tex:getSize()
	local col,row=math.floor(tw/w),math.floor(th/h)
	local count=t.count or col*row
	deck:reserve(count)
	deck:setTexture(tex)
	local origin=t.origin
	local rect=t.rect
	local x0,y0,x1,y1
	if not rect then 
		x0,y0,x1,y1=_getQuadRect(origin or 'center',w,h)
	else
		x0,y0,x1,y1=unpack(rect)
	end
	local idx=1
	local ud,vd=w/tw,h/th
	for y= 0, row-1 do
		for x=0,col-1 do
			deck:setRect(idx,x0,y0,x1,y1)
			deck:setUVRect(idx,ud*x,vd*y,ud*(x+1),vd*(y+1))
			idx=idx+1
			if idx>count then break end
		end
		if idx>count then break end
	end 
	
	return deck
end


local function loadFont(f)
	local size=f.size or 64
	local charCodes=f.charset or 	" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,:.?!{}()<>+_="
	local font 
	local ftype=f.type
	if ftype=='font' then
		font = MOAIFont.new ()
		font:load ( resFilePrefix..f.file)

		local preload=f.preload

		if preload then
			if type(preload)=='number' then
				font:preloadGlyphs(charCodes,preload,72)
			elseif type(preload=='table') then
				for i,size in pairs(preload) do
					font:preloadGlyphs(charCodes,size,72)
				end
			end
		end

	elseif ftype=='bitmap' then
		--todo!!
	elseif ftype=='bmfont' then
		font = MOAIFont.new ()
		font:loadFromBMFont ( resFilePrefix..f.file )
		font:preloadGlyphs(charCodes,size)
		font.size=f.size
		
	elseif ftype=='serialized.font' then
		local file = io.open ( resFilePrefix..f.file..luaExtName, 'r' )
		font = loadstring ( file:read ( '*all' ))()
		file:close ()
		-- load the font image back in
		local image = MOAIImage.new ()
		image:load ( resFilePrefix..f.file..'.png', 0 )
		-- print( resFilePrefix..f.file..'.png')
		-- set the font image
		font:setCache ()
		font:setReader ()
		font:setImage ( image )
		font.size=f.size
	else
		return error('unknown font type:'..ftype)
	end
	font.noScale=f.noScale
	return font
end

local function _expandColor(c)
	local tt=type(c)
	if tt=='string' then
		return hexcolor(c)
	elseif tt=='table' then
		return unpack(c)
	else
		return error('unknown color format')
	end
end

function loadTextStyle(s,fonts)
	local style=MOAITextStyle.new()
	local font=s.font
	if type(font)=='string' then
		assert(fonts,'no font table specified')
		font=fonts[font]
		assert(font,'font not found:'..s.font)
	end
	
	if s.color then	style:setColor(_expandColor(s.color)) end
	style:setFont(font)

	if useScaledText and not ( font.noScale or s.noScale )  then
		local size=s.size or font.size or  12
		local fsize=font.size or originTextSize
		local scale=(s.scale or 1) * size/fsize
		style:setSize(fsize)
		style:setScale(scale)
	else
		style:setScale((s.scale or 1) *globalTextScale)
		local size=s.size or font.size or 12	
		style:setSize(size/globalTextScale)
	end
	style.data=s
	return style
end

function loadTextStyleSheet(s, fonts)
	local t={}
	local default=s.default
	
	for n, d in pairs(s) do
		local style=loadTextStyle(d,fonts)
		style.name=n
		t[n]=style
	end
	return setmetatable(t,strictResMT)
end

function loadRes(t)
	local tt=t.type
	local o=false
	if tt=='texture' then
		o=loadTexture(t)
	elseif tt=='sound' then
		o=loadSound( t)
	elseif tt=='quad' then
		o=loadGfxQuad(t)
	elseif tt=='sheet' then
		o=loadSpriteSheet(t)
	-- elseif tt=='tile' then

	elseif tt=='font' or tt=='bmfont' or tt=='serialized.font' then
		o=loadFont(t)
	elseif tt=='shader' then
		o=loadShader(t)
	elseif tt=='styles' then
		o=loadTextStyleSheet(t)
	elseif tt=='gleed' then
		o=loadGleed(t)
	end
	return o
end

function loadResTable(r,res)
	res=res or {}
	for k,t in pairs(r) do
		res[k]=loadRes(t)
	end
	return setmetatable(res,strictResMT)
end

function loadTPS( root )
	local texture=loadTexture({file=root.texture})
	local decks={}
	local names=root.names
	local data=root[1]
	for name, id in pairs(names) do
		local deck=MOAIGfxQuad2D.new()
		local prim=data.prims[id]
		local quad,uv=data.quads[prim.q], data.uvRects[prim.uv]
		
		deck:setTexture(texture)
		deck.texture=texture
		deck:setRect(quad.x0,quad.y0,quad.x1,quad.y1)
		deck:setUVRect(uv.x0,uv.y0,uv.x1,uv.y1)
		local nn=string.match(name,'(.*)%.')
		decks[nn]=deck
	end
	return decks
end

local ResPack={
	-- __reload=function(self) --reload texture only

	-- end,
	__affirm=function(self)
		for i,t in pairs(self.__textures) do
			t:affirm()
		end
	end,

	__release=function(self)
		for i,t in pairs(self.__textures) do
			t:softRelease()
		end
	end
}

local ResPackMT={
	__index=function(t,k)
		local v=ResPack[k]
		if not v then return error('Res not found:'..k) end
		return v
	end
}

function loadPack( file ,option, settings,half)
	-- if settings then table.foreach(settings,print) print(settings) end
	local f, err = loadfile( resFilePrefix..file )
	if not f then
		print( MOAIFileSystem.getWorkingDirectory() )
		print (err)
		error( 'error loading pack:'..file, 2 )
	end
	local data = {}
	setfenv(f,data)
	f()
	option=option or {}

	local name     = data.name
	local textures = {}
	local decks    = {}
	local dir      = extractDir(file) or ''

	local wildcardSettings
	local normalSettings

	if settings then
		wildcardSettings={}
		normalSettings={}
		for k,v in pairs(settings) do
			if string.endwith(k,'*') then --wildcard
				wildcardSettings[string.sub(k,1,-2)]=v
			else
				normalSettings[k]=v
			end
		end
	end

	for i=1,data.texCount do
		
		local tex=false
		-- if useHalfTexture then
		-- 		--try @half
		-- 	local f1=dir..name..'_'..i..'@half'
		-- 	if MOAIFileSystem.checkFileExists(resFilePrefix..f1..'.pvr') and resFlags['PVR'] then
		-- 		option.file=f1..'.pvr'
		-- 		tex=loadTexture(option)
		-- 	elseif MOAIFileSystem.checkFileExists(resFilePrefix..f1..'.png')  then
		-- 		option.file=f1..'.png'
		-- 		tex=loadTexture(option)
		-- 	end
			
		-- end

		if not tex then
			local f1=dir..name..'_'..i
			if half then f1=f1..'@half' end
			if MOAIFileSystem.checkFileExists(resFilePrefix..f1..'.pvr') and resFlags['PVR'] then
				option.file=f1..'.pvr'
			else
				option.file=f1..'.png'
			end
			tex=loadTexture(option)
		end

		textures[i]=tex
	end

	local center=option.center
	local deforigin=option.origin

	for i,f in ipairs(data.files) do
		
	
		local tex=textures[f.atlasId]
		local name=f.name

		local nn=string.match(name,'([^@]*)[%.@]')
		local s
		
		if settings then
			s= normalSettings and normalSettings[nn] 
			if not s then
				local wildSize=0
				for k,v in pairs(wildcardSettings) do
					if string.startwith(nn,k) and #k>wildSize then
						wildSize=#k
						s=v
						break
					end
				end
			end
		end

		-- print('setting:',nn,s and 'found' or 'no',settings)
		local double=false
		if name:match('@double') then
			double=true
		end
		if s then
			if s.rename then
				nn=s.rename
			end
		end
		s=s or {}

		local deck
		local stype=s.type
		
		if stype=='tileset' then
			local class=MOAITileDeck2D
			if s.customDeckClass then class= s.customDeckClass end
			deck=class.new()
			deck:setTexture(tex)

			local w,h=32,32
			local tw,th=f.w,f.h
			local col,row
			local ox,oy=0,0
			local gutterx,guttery=0,0

			if s.offset then ox,oy=unpack(s.offset)	end
			if s.gutter then gutterx,guttery=unpack(s.gutter)	end
			if s.tileSize then w,h=unpack(s.tileSize) end

			local w1,h1=w+gutterx, h+guttery			
			if s.size then 
				col,row=unpack(s.size)
			else
				col,row=math.floor(tw/w1),math.floor(th/h1)
			end
			col=col==0 and 1 or col
			row=row==0 and 1 or row

			-- deck:setSize(col,row, w,h, ox,oy)
			---TODO: different method for tile size
			local origin=s.origin or deforigin
			local rect=s.rect

			local x0,y0,x1,y1
			if not rect then 
				x0,y0,x1,y1=_getQuadRect(origin or 'left-top',w,h,f.rotated)
			else
				x0,y0,x1,y1=unpack(rect)
			end
			-- print(tw,w1,th,h1)
			assert(col>0 and row>0, 'invalid tileset size:'..f.name)
			if f.rotated then
				-- error('dont rotate tileset')
				
				deck:setUVRect(f.u,f.v,f.u1,f.v1)
				deck:setRect(x0,y1,x1,y0)
				deck:setSize(col,row)
			
				local t1=MOAITransform.new()
				t1:setRot(0,0,90)
				t1:setScl(h/w,h/w)
				deck:transform(t1)
				-- deck:transformUV(t1)
			else
				local u0,v0,u1,v1=f.u,f.v,f.u1,f.v1
				local tu=w/tw*(u1-u0)
				local tv=h/th*(v1-v0)
				local tu1=w1/tw*(u1-u0)
				local tv1=h1/th*(v1-v0)
				local ou=ox/tw*(u1-u0)
				local ov=oy/th*(v1-v0)

				deck:setSize(col,row,tu1,tv1,u0+ou,v0+ov,tu,tv)
				x0,y0,x1,y1=x0/w,y0/h,x1/w,y1/h
				-- deck:setRect(x0,y0,x1,y1)
			end
			
			deck.tileSize={w,h}

		elseif stype=='sheet' then
			local w,h=s.cellW or 32,s.cellH or 32
			deck=MOAIGfxQuadDeck2D.new()
			local tw,th=f.w,f.h
			local col,row=math.floor(tw/w),math.floor(th/h)
			local count=s.cellCount or col*row
			deck:reserve(count)
			deck:setTexture(tex)
			local origin=s.origin or deforigin
			local rect=s.rect
			local x0,y0,x1,y1
			if not rect then 
				x0,y0,x1,y1=_getQuadRect(origin or 'center',w,h,f.rotated)
			else
				x0,y0,x1,y1=unpack(rect)
			end
			local idx=1

			if f.rotated then

				local vd,ud=w/tw*(f.v1-f.v),h/th*(f.u1-f.u)

				for y= 0, row-1 do
					for x=0,col-1 do
						deck:setRect(idx,x0,y1,x1,y0)
						deck:setUVRect(idx,
							f.u1-ud*(y+1),vd*x+f.v,
							f.u1-ud*(y+2),vd*(x+1)+f.v)
						idx=idx+1
						if idx>count then break end
					end
					if idx>count then break end
				end 

				local t1=MOAITransform.new()
				t1:setRot(0,0,90)
				t1:setScl(h/w,h/w)
				deck:transform(t1)
				-- deck:transformUV(t1)
			else

				local ud,vd=w/tw*(f.u1-f.u),h/th*(f.v1-f.v)

				for y= 0, row-1 do
					for x=0,col-1 do
						deck:setRect(idx,x0,y1,x1,y0)
						deck:setUVRect(idx,
							ud*x+f.u,vd*y+f.v,
							ud*(x+1)+f.u,vd*(y+1)+f.v)
						idx=idx+1
						if idx>count then break end
					end
					if idx>count then break end
				end 
			end

		elseif stype=='patch' then
			
			local layout=s.layout or defaultPatchLayout
			local rows,cols=layout.rows,layout.columns
			local patch = MOAIStretchPatch2D.new ()
			
			patch:setTexture (tex)
			patch:reserveRows (#rows)
			for i=1, #rows do
				local r=rows[i]
				patch:setRow(i,r[1],r[2])
			end

			patch:reserveColumns (#cols)
			for i=1, #cols do
				local r=cols[i]
				patch:setColumn(i,r[1],r[2])
			end

			patch:reserveUVRects ( 1 )
			patch:setUVRect ( 1, f.u,f.v1,f.u1,f.v)

			local x0,y0,x1,y1
			if s.rect then
				x0,y0,x1,y1=unpack(s.rect)
			elseif s.origin or deforigin then
				-- local origin=s.origin
				-- local ox,oy=origin[1],origin[2]
				x0,y0,x1,y1=_getQuadRect(s.origin or deforigin,f.w,f.h)
				-- patch:setRect(-ox,-oy,f.w-ox,f.h-oy)
			elseif not (s.nocenter) and (s.center or center) then
				x0,y0,x1,y1=-f.w/2,-f.h/2,f.w/2,f.h/2
			else
				x0,y0,x1,y1=0,0,f.w,f.h
			end
			patch:setRect(x0,y0,
						  x1,y1)
			
			patch.patchWidth=(f.w)
			patch.patchHeight=(f.h)
			
			deck=patch
			-- if f.rotated then
			-- 	local t1=MOAITransform.new()

			-- 	t1:setRot(0,0,90)
			-- 	t1:setScl(f.h/f.w,f.w/f.h)
			-- 	deck:transform(t1)
			-- 	-- deck:transformUV(t1)
			-- end
		else

			deck=MOAIGfxQuad2D.new()
			deck:setTexture(tex)
			deck:setUVRect(f.u,f.v1,f.u1,f.v)

			if double then
				f.w,f.h=f.w*2,f.h*2
			end
			
			if s.rect then
				deck:setRect(unpack(s.rect))
			elseif s.origin or deforigin then
				-- local origin=s.origin
				-- local ox,oy=origin[1],origin[2]
				deck:setRect(_getQuadRect(s.origin or deforigin,f.w,f.h,f.rotated))
				-- deck:setRect(-ox,-oy,f.w-ox,f.h-oy)
			elseif not (s.nocenter) and (s.center or center) then
				deck:setRect(-f.w/2,-f.h/2,f.w/2,f.h/2)
			else
				deck:setRect(0,0,f.w,f.h)
			end


			if f.rotated then
				local t1=MOAITransform.new()
				t1:setRot(0,0,90)
				deck:transform(t1)
			end
		end

		deck.__type=stype
		decks[nn]=deck

	end
	decks.__textures=textures
	return setmetatable(decks,ResPackMT)
end

function mergeResPack(packs)
	local output={}

	for i,pack in ipairs(packs) do
		for k,res in pairs(pack) do
			if output[k] then return error('Assets with duplicated name:'..k) end
			output[k]=res
		end
	end

	return setmetatable(output,ResPackMT)
end

function makeAnimCurve(data)
	local c=MOAIAnimCurve.new()
	for i, k in ipairs(data) do
		c:setKey(i,k.time,k.v,k.ease,k.weight)
	end
	return c
end

function makeLinearAnimCurve(from,to,step,fps,ease)
	fps=fps or 60
	step=step or 1
	ease=ease or MOAIEaseType.FLAT
	local interval=1/fps
	local c=MOAIAnimCurve.new()
	local f=1
	local t=0
	local count=math.floor((to-from)/step)+1
	c:reserveKeys(count)
	for i = from,to,step do
		c:setKey(f,t,i,ease)
		f=f+1
		t=t+interval
	end
	return c
end

function makeTextureDeck(t,origin,scalex,scaley)
	local w,h=t:getSize()
	local deck=MOAIGfxQuad2D.new()
	
	scalex=scalex or 1
	scaley=scaley or 1

	deck:setTexture(t)
	
	local asize=t.actualSize

	local x0,y0,x1,y1
	if asize then
		local aw,ah=asize[1],asize[2]
		x0,y0,x1,y1=_getQuadRect(origin,aw,ah)
		deck:setUVRect(0,0,aw/w,ah/h)
	else
		x0,y0,x1,y1=_getQuadRect(origin,w,h)
		deck:setUVRect(0,0,1,1)
	end
	deck.originRect={x0,y0,x1,y1}
	deck:setRect(x0*scalex,y0*scaley,x1*scalex,y1*scaley)
	-- print(x0*scalex,y0*scaley,x1*scalex,y1*scaley)
	return deck
end

local fullScreenDecks={}
function makeFullScreenTextureDeck(t) --for framebuffer
	local w,h
	local asize=t.actualSize
	local gfx=game.gfx

	if asize then
		w,h=asize[1],asize[2]
	else
		w,h=t:getSize()
	end
	local sx,sy=gfx.w/w,gfx.h/h
	local deck= makeTextureDeck(t,'center',sx,sy)
	deck.size={w,h}
	fullScreenDecks[deck]=true
	return deck
end


function updateFullScreenDecks()
	local gfx=game.gfx
	for d in pairs(fullScreenDecks) do
		local size=d.size
		local w,h=size[1],size[2]
		local sx,sy=gfx.w/w,gfx.h/h
		local x0,y0,x1,y1=
			unpack(d.originRect)
		-- print(gfx.w,gfx.h,sx,sy)

		d:setRect(x0*sx,y0*sy,x1*sx,y1*sy)		
	end
end