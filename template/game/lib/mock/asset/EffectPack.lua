module 'mock'

CLASS: EffectPack ()
	:MODEL{}

function EffectPack:__init()
	self.rootNode = EffectGroup()
	self.rootNode:setName('_root')
end

function EffectPack:findEffect( name )
	return self.rootNode:findChild( name )
end

