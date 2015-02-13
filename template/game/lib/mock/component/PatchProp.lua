module ( 'mock' )

CLASS: PatchProp ()
	:MODEL{
		Field 'deck' :asset( 'deck2d\\.stretchpatch') :set('setDeck')
	}	
wrapWithMoaiPropMethods( PatchProp, '_prop' )

registerComponent( 'PatchProp', PatchProp )

function PatchProp:__init( option )
	local prop = MOAIProp.new()
	self._prop = prop
	self:setDeck( option.deck )
	local size     = option.size
	local w,h
	if size then
		w=size[1] or 100
		h=size[2] or 100
	else
		w=100
		h=100
	end
	self:setSize(w,h)
	return setupMoaiProp( prop, option )
end

function PatchProp:onAttach( entity )
	return entity:_attachProp( self._prop )
end

function PatchProp:onDetach( entity )
	return entity:_detachProp( self._prop )
end

function PatchProp:setDeck( deck )
	self.patchDeck = deck
	self.blendMode = option.blendMode
	prop:setDeck(deck)
	self.deckPath  = deck
	if deck then
		self.patchDeck = loadAsset( deck )
	else
		self.patchDeck = false
	end
end

function PatchProp:sizeToScl(w,h)
	local patch = self.patchDeck
	if patch then
		return w/patch.patchWidth,h/patch.patchHeight
	else
		return 1,1
	end
end

function PatchProp:sclToSize( sx, sy )	
	local patch=self.patchDeck
	if patch then
		return sx*patch.patchWidth,sy*patch.patchHeight
	else
		return sx, sy
	end
end

function PatchProp:getSize()
	return self:sclToSize(self._prop:getScl())
end

function PatchProp:setSize(w,h)
	self._prop:setScl(self:sizeToScl(w,h))
end

function PatchProp:seekSize(w,h, t, easeType) 
	--todo
	local sx,sy=self:sizeToScl(w,h)
	return self._prop:seekScl(sx,sy, nil, t, easeType)
end

function PatchProp:moveSize(dw,dh, t, easeType) 
	--todo
	local dx,dy=self:sizeToScl(dw,dh)
	return self._prop:moveScl(dx,dy, 0, t, easeType)
end

--------------

function Entity:addPatchProp( option )
	return self:attach( PatchProp( option ) )
end

updateAllSubClasses( Entity )
