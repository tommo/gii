module 'mock_edit'

local iconTextureCache = {}
--------------------------------------------------------------------
CLASS: IconGizmo( Gizmo )
function IconGizmo:__init()
	self.iconProp = MOAIProp.new()
	self.iconDeck = MOAIGfxQuad2D.new()
	self.iconProp:setDeck( self.iconDeck )	
	self.pickingTarget = false
end

function IconGizmo:inheritVisible( prop )
	inheritVisible( self.iconProp, prop )
end

function IconGizmo:setTransform( transform )
	inheritLoc( self:getProp(), transform )
end

function IconGizmo:setPickingTarget( target )
	self.pickingTarget = target
end

local ATTR_LOCAL_VISIBLE = MOAIProp. ATTR_LOCAL_VISIBLE
local ATTR_VISIBLE = MOAIProp. ATTR_VISIBLE

function IconGizmo:setParentEntity( ent, propRole )
	self:setPickingTarget( ent )
	local prop = ent:getProp( propRole or 'render' )
	inheritVisible( self:getProp(), prop )
	inheritLoc( self:getProp(), prop )
end


function IconGizmo:getPickingTarget()
	return self.pickingTarget
end

function IconGizmo:setIcon( filename, scale )
	local path = gii.findDataFile( 'gizmo/'..filename )
	if not path then 
		_warn( 'gizmo icon not found', filename )
		return
	end	
	local tex = iconTextureCache[ path ]
	if not tex then
		tex = MOAITexture.new()
		tex:load( path )
		iconTextureCache[ path ] = tex
	end
	self.iconTexture = tex
	self.iconDeck:setTexture( tex )
	local w, h = tex:getSize()
	scale = scale or 1
	self.iconDeck:setRect( -w/2 * scale, -h/2 * scale, w/2 * scale, h/2 * scale )
	self.iconProp:forceUpdate()
end

function IconGizmo:onLoad()
	self:_attachProp( self.iconProp )
	self:enableConstantSize()
end

function IconGizmo:onDestroy()
	Gizmo.onDestroy( self )
	self:_detachProp( self.iconProp )
end

function IconGizmo:isPickable()
	return self.pickingTarget and true or false
end

function IconGizmo:getPickingProp()
	return self.iconProp
end
