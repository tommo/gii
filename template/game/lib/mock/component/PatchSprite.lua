module 'mock'
CLASS: PatchSprite ( DeckComponent )
	:MODEL{
		Field 'deck' :asset( 'deck2d\\.stretchpatch') :getset('Deck');
		Field 'size' :type( 'vec2' ) :getset('Size')
	}	

registerComponent( 'PatchSprite', PatchSprite )

function PatchSprite:setDeck( deck )
	local w,h = self:getSize()
	DeckComponent.setDeck( self,deck )
	self:setSize( w, h )
end

function PatchSprite:setWidth( w )	
	local sclX = self:sizeToScl( w, 1 )
	setSclX( self.prop, sclX )
end

function PatchSprite:setHeight( h )	
	local _,sclY = self:sizeToScl( 1, h )
	setSclY( self.prop, sclY )
end

function PatchSprite:sizeToScl(w,h)
	local patch = self:getMoaiDeck()
	if patch then
		local pw, ph = patch.patchWidth or w, patch.patchHeight or h
		return w / pw, h / ph
	else
		return w,h
	end
end

function PatchSprite:sclToSize( sx, sy )	
	local patch=self:getMoaiDeck()
	if patch then
		local pw, ph = patch.patchWidth or w, patch.patchHeight or h
		return sx*pw, sy*ph
	else
		return sx, sy
	end
end

function PatchSprite:getSize()
	return self:sclToSize( self.prop:getScl() )
end

function PatchSprite:setSize(w,h)
	self.prop:setScl( self:sizeToScl(w,h) )
end

function PatchSprite:seekSize(w,h, t, easeType) 
	local sx,sy=self:sizeToScl(w,h)
	return self.prop:seekScl( sx, sy, nil, t, easeType )
end

function PatchSprite:moveSize(dw,dh, t, easeType) 
	local dx,dy=self:sizeToScl(dw,dh)
	return self.prop:moveScl(dx,dy, 0, t, easeType)
end

