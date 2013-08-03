module ( 'mock' )

CLASS: PatchProp ()
wrapWithMoaiPropMethods( PatchProp, '_prop' )

function PatchProp:__init( option )
	local deck=option.deck
	if not (deck and deck.__type=='patch') then error('non-patch deck',2) end

	self.patchDeck=deck
	local size=option.size
	self.blendMode=option.blendMode
	local w,h
	if size then
		w=size[1] or 100
		h=size[2] or 100
	else
		w=100
		h=100
	end
	local prop=MOAIProp.new()
	self._prop=prop
	prop:setDeck(deck)
	self:setSize(w,h)

	return setupMoaiProp( prop, option )
end

function PatchProp:onAttach( entity )
	return entity:_attachProp( self._prop )
end

function PatchProp:onDetach( entity )
	return entity:_detachProp( self._prop )
end

function PatchProp:sizeToScl(w,h)
	local patch=self.patchDeck
	return w/patch.patchWidth,h/patch.patchHeight
end

function PatchProp:sclToSize(sx,sy)
	local patch=self.patchDeck
	return sx*patch.patchWidth,sy*patch.patchHeight
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
