module 'mock'

--------------------------------------------------------------------
--[[
there are 3 kinds of component in MOCK:
	1. MOAIProp ( generic onAttach/onDetach injected)
	2. MOAIObject extended with onAttach/onDetach methods
	3. Pure Lua class
]]
--------------------------------------------------------------------


--------------------------------------------------------------------
-------Component management
--------------------------------------------------------------------
local componentRegistry = {}
function registerComponentType( name, creator )
	assert( not componentRegistry[ name ], 'duplicated component type:'..name )
	componentRegistry[ name ] = creator
end

function getComponentRegistry()
	return componentRegistry
end

function getComponentType( name )
	return componentRegistry[ name ]
end


-----------Place holder class for component 
CLASS: Component ( Actor ) --just a place holder

-----------convert MOAIProp into attachable components
local onAttachProp = function( self, entity )
	return entity:_attachProp( self )
end

local onDetachProp = function( self, entity )
	return entity:_detachProp( self )
end

function injectMoaiPropComponentMethod( clas )
	injectMoaiClass( clas, {
		onAttach = onAttachProp,
		onDetach = onDetachProp,
		setupProp      = setupMoaiProp,
		setupTransform = setupMoaiTransform,
		})
end

injectMoaiPropComponentMethod( MOAIProp )
injectMoaiPropComponentMethod( MOAIProp2D )
injectMoaiPropComponentMethod( MOAITextBox )
injectMoaiPropComponentMethod( MOAIParticleSystem )
injectMoaiPropComponentMethod( MOAITextBox )

--------------------------------------------------------------------



