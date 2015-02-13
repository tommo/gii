module 'mock'

TEXTURE_ASYNC_LOAD = false

--------------------------------------------------------------------
local texturePlaceHolder      = false
local texturePlaceHolderImage = false

function getTexturePlaceHolderImage( w, h )
	if not texturePlaceHolderImage then
		w, h = w or 32, h or 32
		texturePlaceHolderImage = MOAIImage.new()
		texturePlaceHolderImage:init( w, h )
		texturePlaceHolderImage:fillRect( 0,0, w, h, 0, 1, 0, 1 )
	end
	return texturePlaceHolderImage
end

function getTexturePlaceHolder()
	if not texturePlaceHolder then
		texturePlaceHolder = MOAITexture.new()
		texturePlaceHolder:load( getTexturePlaceHolderImage( 32, 32 ) )		
	end
	return texturePlaceHolder
end


--------------------------------------------------------------------
CLASS: ThreadTextureLoadTask ( ThreadImageLoadTask )
	:MODEL{}

function ThreadTextureLoadTask:setTargetTexture( tex )
	self.texture = tex
end

function ThreadTextureLoadTask:setDebugName( name )
	self.debugName = name
end

function ThreadTextureLoadTask:onComplete( img )
	self.texture:load ( img, self.imageTransform, self.debugName or self.filename )
	self.texture:affirm()	
end

function ThreadTextureLoadTask:onFail()
	_warn( 'failed load texture file:', filePath )
	self.texture:load( getTexturePlaceHolderImage(), self.imageTransform, self.debugName or self.filename )
end


function ThreadTextureLoadTask:toString()
	return '<textureLoadTask>' .. self.imagePath .. '\t' .. ( self.debugName or '')
end
