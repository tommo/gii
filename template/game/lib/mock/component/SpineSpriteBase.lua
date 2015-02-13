module 'mock'

CLASS: SpineSpriteBase ()
	:MODEL{
		Field 'shader' :asset('shader') :set( 'setShader' );
		Field 'preAlpha' :boolean();
		'----';
		Field 'sprite' :asset('spine') :getset('Sprite') :label('Sprite');
	}

function SpineSpriteBase:__init()
	self.skeleton  = self:_createSkeleton()
	self.propInserted  = false
	self.preAlpha = false
end

function SpineSpriteBase:_createSkeleton()
	return MOAISpineSkeleton.new()
end

function SpineSpriteBase:onAttach( entity )
	entity:_attachProp( self.skeleton )
end

function SpineSpriteBase:onDetach( entity )
	entity:_detachProp( self.skeleton )
	self.skeleton:forceUpdateSlots()
end

function SpineSpriteBase:setSprite( path, alphaBlend )
	alphaBlend = alphaBlend~=false
	self.spritePath   = path	
	self.skeletonData = loadAsset( path )
	if self.skeletonData  then
		local entity = self._entity
		if entity then
			entity:_detachProp( self.skeleton )		
			self.skeleton  = self:_createSkeleton()
			self.skeleton:load( self.skeletonData, 0.001, not self.preAlpha )
			entity:_attachProp( self.skeleton )
		else
			self.skeleton:load( self.skeletonData, 0.001, not self.preAlpha )
		end
		self:updateShader()
	end
end

function SpineSpriteBase:getSprite()
	return self.spritePath
end

function SpineSpriteBase:setMixTable( t )
	self.mixTable = t
end

function SpineSpriteBase:getMixTable()
	return self.mixTable
end

function SpineSpriteBase:affirmClip( name )
	local t = self.skeletonData._animationTable
	return t[ name ]
end

function SpineSpriteBase:getClipLength( name )
	--TODO
	return 1
end

function SpineSpriteBase:setShader( shaderPath )
	self.shader = shaderPath	
	self:updateShader()
end

local defaultShader = MOAIShaderMgr.getShader( MOAIShaderMgr.DECK2D_SHADER )
function SpineSpriteBase:updateShader()
	if self.skeleton then
		if self.shader then
			local shader = mock.loadAsset( self.shader )
			if shader then
				local moaiShader = shader:getMoaiShader()
				return self.skeleton:setShader( moaiShader )
			end
		end
		self.skeleton:setShader( defaultShader )
	end
end
