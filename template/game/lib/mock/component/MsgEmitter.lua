CLASS: MsgEmitter ()
	:MODEL{		
		Field 'msg' :string();
		Field 'arg' :string();
	}

mock.registerComponent( 'MsgEmitter', MsgEmitter )

function MsgEmitter:__init()
	self.msg = ''
	self.arg = false
end

function MsgEmitter:onStart( ent )
	if self.msg and self.msg~='' then
		return ent:tell( self.msg, self.arg, self )
	end	
end
