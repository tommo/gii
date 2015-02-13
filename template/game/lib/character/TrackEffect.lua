module 'character'

local function fixpath(p)
	p=string.gsub(p,'\\','/')
	return p
end

local function stripExt(p)
	return string.gsub( p, '%..*$', '' )
end

local function stripDir(p)
	p=fixpath(p)
	return string.match(p, "[^\\/]+$")
end

--------------------------------------------------------------------
CLASS: EventEffect ( CharacterActionEvent )
	:MODEL{
		Field 'effect' :asset( 'effect' );
		Field 'loop'   :boolean();
		Field 'layer'  :string();
		'----';
		Field 'spineSlot'  :string() :selection( 'getSpineSlotList' );
		Field 'followSlot' :boolean();
		'----';
		Field 'loc' :type('vec3') :getset('Loc');
		Field 'rot' :type('vec3') :getset('Rot');
		Field 'scl' :type('vec3') :getset('Scl');
		'----';
		Field 'stopWithEvent' :boolean();
	}

function EventEffect:__init()
	self.name   = 'effect'
	self.loop   = falsephong15
	self.effect = false
	self.followSlot = false
	self.spineSlot  = false
	self.transform  = MOAITransform.new()
	self.stopWithEvent = true
	self.layer      = false
end

function EventEffect:getSpineSlotList()
	local result = {
		{ '<none>', false }
	}
	local config = self:getRootConfig()
	local spinePath = config:getSpine()
	local spineData = mock.loadAsset( spinePath )
	if not spineData then return nil end
	for k,i in pairs( spineData._slotTable ) do
		table.insert( result, { k, k } )
	end
	return result
end

function EventEffect:setLoc( x,y,z )
	return self.transform:setLoc( x,y,z )
end

function EventEffect:getLoc()
	return self.transform:getLoc()
end

function EventEffect:setRot( x,y,z )
	return self.transform:setRot( x,y,z )
end

function EventEffect:getRot()
	return self.transform:getRot()
end

function EventEffect:setScl( x,y,z )
	return self.transform:setScl( x,y,z )
end

function EventEffect:getScl()
	return self.transform:getScl()
end

function EventEffect:isResizable()
	return true
end

function EventEffect:start( state, pos )
	local effect = self.effect
	if effect == '' then effect = nil end
	if not self.effect then return end
	local target = state.target

	local emEnt = mock.Entity()
	local em = mock.EffectEmitter()
	emEnt:attach( em )
	local layer = self.layer
	if layer == '' then layer = false end
	target:getEntity():addChild( emEnt, layer )
	local transform = self.transform
	em:setEffect( self.effect )

	local x,y,z    = transform:getLoc()
	local rx,ry,rz = transform:getRot()
	local sx,sy,sz = transform:getScl()
	local kx = target.mirrorX and -1 or 1
	local ky = target.mirrorY and -1 or 1
	
	sx = sx * kx
	sy = sy * ky
	x = x * kx
	y = y * ky
	
	if kx * ky == -1 then
		rz = - rz
	end

	em.prop:setLoc( x,y,z )
	em.prop:setRot( rx,ry,rz )
	em.prop:setScl( sx,sy,sz )
	em:start()
	local length = self.length/1000
	em:setActionOnStop( 'destroy' )
	if self.stopWithEvent then
		em:setDuration( length )
	end
	state.effectEmitters[ self.parent ][ em ] = true
end

function EventEffect:toString()
	if not self.effect then return '<nil>' end
	local name = stripExt( stripDir( self.effect ) )
	return self.loop and '<loop>'..name or name
end

--
function EventEffect:onBuildGizmo()
	local giz = mock_edit.SimpleBoundGizmo()
	giz:setTarget( self )
	linkLoc( giz:getProp(), self.transform )
	linkRot( giz:getProp(), self.transform )
	linkScl( giz:getProp(), self.transform )
	return giz
end

function EventEffect:drawBounds()
	MOAIDraw.drawEmitter( 0,0 )
end

--------------------------------------------------------------------
CLASS: TrackEffect ( CharacterActionTrack )
	:MODEL{
		Field 'layer'     :type('layer')  :no_nil();
}

function TrackEffect:__init()
	self.name  = 'fx'
	self.layer = false
end

function TrackEffect:getType()
	return 'effect'
end

function TrackEffect:createEvent()
	return EventEffect()
end

function TrackEffect:toString()
	return '<fx>' .. tostring( self.name )
end

function TrackEffect:start( state )
	--build MOAISpineAnimationTrack
	local target      = state.target
	local effectEmitters = state.effectEmitters
	if not effectEmitters then 
		effectEmitters = {}
		state.effectEmitters = effectEmitters
	end
	effectEmitters[ self ] = {}
end

function TrackEffect:stop( state )
	local emitterList = state.effectEmitters
	if not emitterList then return end
	
	local emitters = emitterList[ self ]
	if not emitters then return end

	local ent = state.target:getEntity()
	for em in pairs( emitters ) do
		if em._entity then
			ent:detach( em )
		end
	end
	state.effectEmitters[ self ] = nil
	
end

--------------------------------------------------------------------
registerCharacterActionTrackType( 'Effect', TrackEffect )
