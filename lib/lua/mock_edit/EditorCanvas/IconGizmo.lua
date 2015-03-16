module 'mock_edit'

local iconTextureCache = {}
--------------------------------------------------------------------
CLASS: IconGizmo( CanvasHandle )
function IconGizmo:__init()
	self.iconProp = MOAIProp.new()
	self.iconDeck = MOAIGfxQuad2D.new()
	self.iconProp:setDeck( self.iconDeck )	
	self.target = false
end

function IconGizmo:setTarget( target )
	self.target = target
end

function IconGizmo:setTransform( transform )	
	inheritLoc( self:getProp(), transform )
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
end

function IconGizmo:onDestroy()
	CanvasHandle.onDestroy( self )
	self:_detachProp( self.iconProp )
end
