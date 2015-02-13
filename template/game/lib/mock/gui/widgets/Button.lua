module 'mock'

CLASS: GUIButton ( GUIButtonBase )
	:MODEL{
		'----';
		Field 'deckNormal'  :asset('deck2d\\..*')   :getset('DeckNormal');
		Field 'deckPress'   :asset('deck2d\\..*')   :getset('DeckPress');
		-- Field 'deckHover'   :asset('deck2d\\..*')   :getset('Deck');
		-- Field 'deckDisabled'   :asset('deck2d\\..*')   :getset('Deck');
	}


function GUIButton:onLoad()
	self.prop = self:attachInternal( DeckComponent() )
end

function GUIButton:onPress	( touch, x, y )
	self:setState 'up'
	self:emit('button.up',self)
end

function GUIButton:onRelease( touch, x, y )
	self:setState 'normal'
	self:emit( 'button.down', self )
	if self:inside(x,y) then
		
		if self.option.sound then
			self:playSound(self.option.sound)
		end

		self:emit('button.click',self)		
		local onClick=self.onClick
		if onClick then return onClick(self) end
		
	end
end

function GUIButton:inside(x,y)
	return self.prop:inside(x,y)
end
