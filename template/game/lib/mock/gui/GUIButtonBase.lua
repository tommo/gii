module 'mock'

registerSignals{
	'ui.button.press',
	'ui.button.release',
	'ui.button.click',
}

CLASS: GUIButtonBase ( GUIWidget )
	:MODEL{
		'----';
		Field 'msg'  :string();
		Field 'data' :string();
		'----';
		Field 'eventTag'  :string();
		'----';
	}

function GUIButtonBase:__init()
	self.eventTag = false
end

function GUIButtonBase:onLoad()
end

function GUIButtonBase:_onPress	( touch, x, y )
	self:setState 'press'
	self:emit( 'ui.button.press', self )
	self:updateState()
	return self:onPress( touch, x, y )
end

function GUIButtonBase:onStateChange()
	return self:updateState()
end

function GUIButtonBase:_onRelease( touch, x, y )
	if self.state == 'disabled' then return end
	self:setState 'normal'
	self:emit( 'ui.button.release', self )
	local px,py,pz = self:getWorldLoc()
	if self:inside( x,y,pz, getDefaultTouchPadding() ) then
		self:emit( 'ui.button.click', self )
		local onClick=self.onClick
		if onClick then onClick( self ) end		
		if self.msg and self.msg~='' then
			self:getRootWidget():tell( self.msg, self.data, self )
		end
	end
	self:updateState()
	return self:onRelease( touch, x, y )
end

function GUIButtonBase:updateState()
end

---user callback
function GUIButtonBase:onClick()
end
