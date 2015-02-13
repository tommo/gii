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
module 'mock'

--------------------------------------------------------------------
CLASS: MSprite ( RenderComponent )
	:MODEL {
		Field 'sprite' :asset( 'msprite' ) :getset('Sprite');
		Field 'default' :string() :selection( 'getClipNames' );
		Field 'autoPlay' :boolean();
	}

wrapWithMoaiPropMethods( MSprite, 'prop' )

mock.registerComponent( 'MSprite', MSprite )
mock.registerEntityWithComponent( 'MSprite', MSprite )
--------------------------------------------------------------------

function MSprite:__init()
	self.prop        = MOAIProp.new()
	self.driver      = MOAIAnim.new()
	self.spriteData = false
	self.currentClip = false
	self.playFPS     = 60
	self.playSpeed   = 1
	self.driver:reserveLinks( 3 ) --offset x & offset y & frame index	
	self.featureMask = {}
end

function MSprite:onAttach( entity )
	return entity:_attachProp( self.prop )
end

function MSprite:onDetach( entity )
	self:stop()
	return entity:_detachProp( self.prop )
end

function MSprite:onStart( entity )
	if self.autoPlay and self.default then
		self:play( self.default )
	end
end

function MSprite:setSprite( path )
	self:stop( true )
	self.spritePath = path 

	local spriteData, node = loadAsset( path )
	--TODO? assert asset node type
	if spriteData then
		self:stop( true )
		self.currentClip = false
		self.spriteData = spriteData
		local instance = MOAIGfxMaskedQuadListDeck2DInstance.new()
		instance:setSource( spriteData.frameDeck )
		self.deckInstance = instance
		-- self:_updateFeatureMask()
		self.prop:setDeck( instance )
		self.prop:setIndex( 1 )
		self.prop:forceUpdate()
	end

end

-- function MSprite:_updateFeatureMask()
-- 	if not self.deckInstance then return end
-- 	local instance = self.deckInstance
-- 	for i = 1, 64 do
-- 		instance:setMask( i, self.featureMask[ i ] ~= false )
-- 	end
-- end

function MSprite:getFeatureNames()
	if self.spriteData then
		return self.spriteData.featureNames
	end
	return {}
end

function MSprite:setFeatureHidden( featureName, value )
	if not self.deckInstance then return end
	local features = self.spriteData.features
	local bit = features and features[ featureName ] or 0
	self.deckInstance:setMask( bit, value ~= false )
	-- self.featureMask[ bit ] = value ~= false
	-- if not self.deckInstance then return end
end

function MSprite:setupFeatures( featureNames )
	if not self.deckInstance then return end
	local features = self.spriteData.features
	if not features then return end
	local instance = self.deckInstance
	for i = 1, 64 do --hide all
		instance:setMask( i, true )
	end
	for i, featureName in ipairs( featureNames ) do
		local bit = features[ featureName ]
		if bit then
			instance:setMask( bit, false ) --show target feature
		end
	end
end

--------------------------------------------------------------------
local defaultShader = MOAIShaderMgr.getShader( MOAIShaderMgr.DECK2D_SHADER )

function MSprite:setShader( shaderPath )
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


function MSprite:getSprite()
	return self.spritePath
end

function MSprite:getSpriteData()
	return self.spriteData
end

function MSprite:getClipNames()
	local data = self.spriteData
	if not data then return nil end
	local result = {}
	for k,i in pairs( data.animations ) do
		table.insert( result, { k, k } )
	end
	return result
end

function MSprite:setScissorRect( r )
	return self.prop:setScissorRect( r )
end

function MSprite:getClipTable()
	local data = self.spriteData
	if not data then 
		_error('animation not load', 2)
		return nil
	end
	return data.animations
end

function MSprite:getClip( name )
	local data = self.spriteData
	if not data then 
		_error('animation not load', 2)
		return nil
	end
	return data.animations[ name ]
end

function MSprite:hasClip( name )
	local data = self.spriteData
	return data and data.animations[ name ]~=nil
end

function MSprite:getClipLength( name )
	local clip = name and self:getClip( name ) or self.currentClip
	if clip then return clip.length * self.playFPS end
end

function MSprite:setClip( name, mode )
	if self.currentClip and self.currentClip.name == name then return false end

	local clip = self:getClip( name )
	if not clip then 
		_error( 'animation clip not found:'..name )
		return
	end
	self.currentClip=clip
	if self.driver then self.driver:stop() end
	---bind animcurve to driver
	local driver       = MOAIAnim.new()
	local indexCurve   = clip.indexCurve
	local offsetXCurve = clip.offsetXCurve
	local offsetYCurve = clip.offsetYCurve

	driver:reserveLinks( 3 )
	driver:setLink( 1, indexCurve,   self.prop, MOAIProp.ATTR_INDEX )
	-- driver:setLink( 2, offsetXCurve, self.prop, MOAIProp.ATTR_X_LOC )
	-- driver:setLink( 3, offsetYCurve, self.prop, MOAIProp.ATTR_Y_LOC )
	driver:setMode( mode or clip.mode or MOAITimer.NORMAL )

	self.driver = driver

	self:setFPS(self.playFPS)
	self:apply( 0 )
	self:setTime( 0 )

	return true
end

-----------
function MSprite:setFPS( fps )
	self.playFPS = fps
	self:setSpeed( self.playSpeed )
end

function MSprite:getFPS()
	return self.playFPS
end

function MSprite:setSpeed( speed )
	speed = speed or 1
	self.playSpeed = speed
	self.driver:setSpeed( speed * self.playFPS )
end

function MSprite:getSpeed()
	return self.playSpeed
end

function MSprite:setTime( time )
	return self.driver:setTime( time )
end

function MSprite:apply( time )
	return self.driver:apply( time / self.playFPS )
end

-----------Play control
function MSprite:play( clipName, mode )
	if self:setClip( clipName, mode ) then return self:start() end
end

function MSprite:resetAndPlay( clipName, mode )
	if self:setClip( clipName, mode ) then  --playing a new clip
		return self:start()
	else --same as playing clip
		self:setTime( 0 )
		self:apply( 0 )
		return self:start()
	end
end

function MSprite:start()
	self.driver:start()
	return self.driver
end

function MSprite:reset()
	self:setTime( 0 )
end

function MSprite:stop( reset )
	self.driver:stop()
	if reset then return self:reset() end
end

function MSprite:pause( paused )
	self.driver:pause( paused )
end

function MSprite:isPaused()
end

function MSprite:wait()
	return MOAICoroutine.blockOnAction( self.driver )
end

function MSprite:isPlaying()
	return self.driver:isBusy()
end

function MSprite:setBlend( b )
	self.blend = b	
	setPropBlend( self.prop, b )
end

function MSprite:setVisible( f )
	return self.prop:setVisible( f )
end

function MSprite:isVisible()
	return self.prop:isVisible()
end
