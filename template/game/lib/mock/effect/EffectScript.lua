module 'mock'

CLASS: EffectScript ( EffectNode )
	:MODEL{
		Field 'script' :string()  :no_edit(); --will use a custom script box for widget
	}

function EffectScript:__init()
	self.script = [[
function onUpdate( fxState, dt )
	--update script
end
	]]
	self._onUpdate = false
end

function EffectScript:onBuild()
	local chunk, err = loadstring( self.script )
	if chunk then
		local env = {}
		setfenv( chunk, env )
		chunk()
		self._onUpdate = env.onUpdate
		self._onLoad   = env.onLoad
	end
end

function EffectState:onLoad( fxState )
	if self._onLoad then
		self._onLoad( fxState )
	end
	if self._onUpdate then
		fxState:addUpdateListener( self )
	end
end

function EffectScript:onUpdate( fxState, dt ) --only run when callback exists
	return self._onUpdate( fxState, dt )
end

registerEffectNodeType(
	'script',
	EffectScript
)
