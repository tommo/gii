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
CLASS: AuroraSprite ()
wrapWithMoaiPropMethods( AuroraSprite, 'prop' )

function AuroraSprite:__init( option )
	self.prop        = MOAIProp.new()
	self.driver      = MOAIAnim.new()
	self.spriteAsset = false
	self.currentClip = false
	self.playFPS     = 60
	self.playSpeed   = 1

	self.driver:reserveLinks( 3 ) --offset x & offset y & frame index
	if option then
		if option.fps then self.playFPS = option.fps end
		if option.sprite then	self:load( option.sprite ) end
		setupMoaiProp( self.prop, option )
	end
end

function AuroraSprite:onAttach( entity )
	return entity:_attachProp( self.prop )
end

function AuroraSprite:onDetach( entity )
	self:stop()
	return entity:_detachProp( self.prop )
end

function AuroraSprite:load( spriteAsset )
	self:stop()
	self.spriteAsset = spriteAsset
	self.prop:setDeck( spriteAsset.frameDeck )
	self.prop:setIndex( 0 )
end

function AuroraSprite:setScissorRect( r )
	return self.prop:setScissorRect( r )
end

function AuroraSprite:getClipTable()
	local asset = self.spriteAsset
	if not asset then error('animation not load', 2) end
	return asset.animations
end

function AuroraSprite:getClip( name )
	local asset = self.spriteAsset
	if not asset then error('animation not load', 2) end
	return asset.animations[ name ]
end

function AuroraSprite:getClipLength( name )
	local clip = name and self:getClip( name ) or self.currentClip
	if clip then return clip.length * self.playFPS end
end

function AuroraSprite:setClip( name, mode )
	if self.currentClip and self.currentClip.name == name then return false end

	local clip = self:getClip( name )
	if not clip then error( 'animation clip not found:'..name, 2 ) end
	self.currentClip=clip
	if self.driver then self.driver:stop() end
	---bind animcurve to driver
	local driver       = MOAIAnim.new()
	local indexCurve   = clip.indexCurve
	local offsetXCurve = clip.offsetXCurve
	local offsetYCurve = clip.offsetYCurve

	driver:reserveLinks( 3 )
	driver:setLink( 1, indexCurve,   self.prop, MOAIProp.ATTR_INDEX )
	driver:setLink( 2, offsetXCurve, self.prop, MOAIProp.ATTR_X_LOC )
	driver:setLink( 3, offsetYCurve, self.prop, MOAIProp.ATTR_Y_LOC )
	driver:setMode( mode or clip.mode or MOAITimer.NORMAL )

	self.driver = driver

	self:setFPS(self.playFPS)
	self:apply( 0 )
	self:setTime( 0 )

	return true
end

-----------
function AuroraSprite:setFPS( fps )
	self.playFPS = fps
	self:setSpeed( self.playSpeed )
end

function AuroraSprite:getFPS()
	return self.playFPS
end

function AuroraSprite:setSpeed( speed )
	speed = speed or 1
	self.playSpeed = speed
	self.driver:setSpeed( speed * self.playFPS )
end

function AuroraSprite:getSpeed()
	return self.playSpeed
end

function AuroraSprite:setTime( time )
	return self.driver:setTime( time )
end

function AuroraSprite:apply( time )
	return self.driver:apply( time / self.playFPS )
end

-----------Play control
function AuroraSprite:play( clipName, mode )
	if self:setClip( clipName, mode ) then return self:start() end
end

function AuroraSprite:resetAndPlay( clipName, mode )
	if self:setClip( clipName, mode ) then  --playing a new clip
		return self:start()
	else --same as playing clip
		self:setTime( 0 )
		self:apply( 0 )
		self:start()
	end
end

function AuroraSprite:start()
	self.driver:start()
end

function AuroraSprite:reset()
	self:setTime( 0 )
end

function AuroraSprite:stop( reset )
	self.driver:stop()
	if reset then return self:reset() end
end

function AuroraSprite:pause( paused )
	self.driver:pause( paused )
end

function AuroraSprite:isPaused()
end

function AuroraSprite:wait()
	return MOAICoroutine.blockOnAction( self.driver )
end

function AuroraSprite:isPlaying()
	return self.driver:isBusy()
end


