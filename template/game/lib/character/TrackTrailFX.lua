module 'character'

--------------------------------------------------------------------
CLASS: EventTrailFX ( CharacterActionEvent )
	:MODEL{
		Field 'texture'  :asset('texture');
		Field 'color'    :type( 'color' ) :getset( 'Color' );
		Field 'blend'    :enum( mock.EnumBlendMode );
		Field 'loc' :type('vec3') :getset('Loc');
		'----';
		Field 'trailSpeed' :int() :range( 1, 10 ) :widget('slider');
		'----';
		Field 'forHero' :boolean();
	}

function EventTrailFX:__init()
	self.easeType = MOAIEaseType.EASE_IN
	self.transform = MOAITransform.new()
	self.texture = mock.findAsset( 'trail', 'texture' )
	self.color   = {1,1,.5,1}
	self.blend = 'add'
	self.trailSpeed = 5
	self.forHero     = false
end

function EventTrailFX:onStart( state )
end

function EventTrailFX:isResizable()
	return true
end

function EventTrailFX:getLoc()
	return self.transform:getLoc()
end

function EventTrailFX:setLoc( x,y,z )
	return self.transform:setLoc( x,y,z )
end

function EventTrailFX:getColor()
	return unpack( self.color )
end

function EventTrailFX:setColor( r,g,b,a )
	self.color = { r,g,b,a }
end

--------------------------------------------------------------------
CLASS: EventTrailFXArc ( EventTrailFX )
	:MODEL {
		Field 'radius' ;
		Field 'trailLength' ;
		Field 'angle0' ;
		Field 'angle1' ;
		
	}
function EventTrailFXArc:__init()
	self.radius      = 100
	self.trailLength = 70
	self.angle0      = 0
	self.angle1      = 90
end

local function _onTrailStop( node )
	local prop = node.prop
end

function EventTrailFXArc:start( state, pos )
	local duration = self.length/1000 / state.throttle
	if duration == 0 then return end
	local tex = mock.loadAsset( self.texture )
	if not tex then return end
	local target = state.target
	local ent = target:getEntity()	
	--todo: cache this
	local deck = MOAISectionDeck.new()	
	local moaiTex, uv = tex:getMoaiTextureUV()
	deck:setTexture( moaiTex )
	deck:setUVRect( unpack( uv ) )
	local prop = MOAIProp.new()
	prop:setDeck( deck )
	local x,y,z = self.transform:getLoc()
	prop:setPiv( -x, -y, 5 )
	prop:setScl( target.mirrorX and -1 or 1, target.mirrorY and -1 or 1, 1 )
	if self.forHero then
		local head   = target:getParam( 'hero-trail-head',   0 )
		local length = target:getParam( 'hero-trail-length', self.trailLength )
		local radius = head + length + self.radius - self.trailLength
		deck:setRadius( radius, length )
	else
		deck:setRadius( self.radius, self.trailLength )
	end
	setPropBlend( prop, self.blend )
	ent:_attachProp( prop )
	prop:setColor( unpack( self.color ) )
	local a0, a1 = self.angle0, self.angle1
	deck:setSection( a0, a0, 10 )
	local delay = ( 1 - self.trailSpeed/10 ) * 4 + 1
	prop:seekColor( 0,0,0,0, duration*.7*delay, MOAIEaseType.SHARP_EASE_OUT )
	local action = deck:seekAngle0( a0+(a1-a0)*.7, duration * delay, MOAIEaseType.SOFT_EASE_IN )
	deck:seekAngle1( a1, duration, MOAIEaseType.EASE_IN )	
	action:setListener( MOAIAction.EVENT_STOP, function()
		ent:_detachProp( prop )
	end
	)
end

function EventTrailFXArc:onBuildGizmo()
	local giz = mock_edit.SimpleBoundGizmo()
	giz:setTarget( self )
	linkLoc( giz:getProp(), self.transform )
	linkScl( giz:getProp(), self.transform )
	linkRot( giz:getProp(), self.transform )
	return giz
end

local setColor = MOAIGfxDevice.setPenColor
local setWidth = MOAIGfxDevice.setPenWidth
local function drawSectionDeckGizmo( x,y, radius, length, a0, a1 )
	setWidth( 1 )
	MOAIDraw.drawCircle( 0,0, 5 )
	setColor( 1,0,1 )
	MOAIDraw.drawArc( 0,0, radius, a0, a1 )
	MOAIDraw.drawArc( 0,0, radius-length, a0, a1 )
	setColor( .5,.2,0 )
	MOAIDraw.drawRadialLine( 0,0, a0, radius-length, radius )
	setWidth( 2 )
	setColor( 1,1,0 )
	MOAIDraw.drawRadialLine( 0,0, a1, radius-length, radius )
	setWidth( 1 )
end

function EventTrailFXArc:drawBounds()
	local x,y = self:getLoc()
	drawSectionDeckGizmo( x,y, self.radius, self.trailLength, self.angle0, self.angle1 )
end

--------------------------------------------------------------------
CLASS: EventTrailFXRay ( EventTrailFX )
	:MODEL{
		Field 'trailWidth';
		Field 'trailLength';
		Field 'direction' :range( 0, 360 ) :widget( 'slider' ) :set('setDirection');
}
function EventTrailFXRay:__init()
	self.trailWidth     = 100
	self.trailLength    = 100
	self.direction = 0
end

function EventTrailFXRay:setDirection( direction )
	self.transform:setRot( 0,0,direction - 90 )
	self.direction = direction
end

function EventTrailFXRay:start( state, pos )
	local duration = self.length/1000 / state.throttle
	if duration == 0 then return end
	local tex = mock.loadAsset( self.texture )
	if not tex then return end
	local target = state.target
	local ent = target:getEntity()	
	--todo: cache this
	local deck = MOAIGfxQuad2D.new()	
	local moaiTex, uv = tex:getMoaiTextureUV()
	deck:setTexture( moaiTex )
	deck:setUVRect( unpack( uv ) )
	local w = self.trailWidth
	local h = self.trailLength
	deck:setRect( -w/2, 0, w/2, -h )
	local prop = MOAIProp.new()
	prop:setDeck( deck )
	setPropBlend( prop, self.blend )
	ent:_attachProp( prop )
	prop:setColor( unpack( self.color ) )
	local dir = self.direction - 90
	local delay = ( 1 - self.trailSpeed/10 ) * 4 + 1
	prop:seekColor( 0,0,0,0, duration * delay*0.9, MOAIEaseType.SHARP_EASE_OUT )
	local x1, y1 = self.transform:getLoc()
	local dx, dy = vecAngle( dir + 90 - 180, self.trailLength )
	local x0, y0 = x1 + dx, y1 + dy
	local mx = target.mirrorX and -1 or 1
	local my = target.mirrorY and -1 or 1
	prop:setLoc( x0 * mx , y0 * my, 5 )
	if target.mirrorY then dir = 180 - dir  end
	if target.mirrorX then dir = - dir  end
	prop:setRot( 0,0, dir )
	
	local action = prop:seekAttr(
		MOAIProp.ATTR_Y_SCL, 0.5, duration * delay * 1.1, MOAIEaseType.SOFT_EASE_IN
	)
	local ddx, ddy = -dx , -dy
	if target.mirrorX then ddx = - ddx end
	if target.mirrorY then ddy = - ddy end
	prop:moveLoc( ddx, ddy, 5, duration * delay, MOAIEaseType.SOFT_EASE_IN )
	action:setListener( MOAIAction.EVENT_STOP, function()
		ent:_detachProp( prop )
	end
	)
end


function EventTrailFXRay:onBuildGizmo()
	local giz = mock_edit.SimpleBoundGizmo()
	giz:setTarget( self )
	linkLoc( giz:getProp(), self.transform )
	linkScl( giz:getProp(), self.transform )
	linkRot( giz:getProp(), self.transform )
	return giz
end

local setColor = MOAIGfxDevice.setPenColor
local setWidth = MOAIGfxDevice.setPenWidth
local function drawRayTrailGizmo( x,y, width, length, direction )
	setWidth( 1 )
	setColor( 1,0,1 )
	MOAIDraw.drawArrow( 0,-length, 0,0 )
	MOAIDraw.drawRect( -width/2, -length, width/2, 0 )
end

function EventTrailFXRay:drawBounds()
	local x,y = self:getLoc()
	drawRayTrailGizmo( x,y, self.trailWidth, self.trailLength, self.direction )
end

--------------------------------------------------------------------
-- CLASS: EventTrailFXSlotTrail (CharacterActionEvent)
-- 	:MODEL {
-- 		Field 'targetSlot' :string();
-- 		Field 'width';		
-- }


--------------------------------------------------------------------
CLASS: TrackTrailFX ( CharacterActionTrack )
	:MODEL{}

function TrackTrailFX:__init()
	self.name = 'trailFX'
end

function TrackTrailFX:getType()
	return 'trailFX'
end

function TrackTrailFX:getEventTypes()
	return { 'arc', 'ray' }
end

function TrackTrailFX:createEvent( evType )
	if evType == 'arc' then
		return EventTrailFXArc()
	elseif evType == 'ray' then
		return EventTrailFXRay()
	else
		return false
		-- return EventTrailFXSlot()
	end
end

function TrackTrailFX:toString()
	return '<trail>'.. tostring( self.name )
end

--------------------------------------------------------------------
registerCharacterActionTrackType( 'TrailFX', TrackTrailFX )
