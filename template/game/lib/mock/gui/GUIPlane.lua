module 'mock'

CLASS: GUIPlane ( GUIWidget )
	:MODEL{
		Field 'size'       :type('vec2') :getset('Size');
	}

mock.registerGUIWidget( 'Plane', GUIPlane )

--------------------------------------------------------------------
function GUIPlane:setSize( w, h )
	if not w then
		w, h = self:getDefaultSize()
	end
	self.width, self.height = w, h
	self:setScissorRect( 0, 0, w, h )
end

--------------------------------------------------------------------
function GUIPlane:drawBounds()
	GIIHelper.setVertexTransform( self:getProp() )
	MOAIDraw.drawRect( 0,0, self:getSize() )
end

