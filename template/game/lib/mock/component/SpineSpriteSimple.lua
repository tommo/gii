module 'mock'

CLASS: SpineSpriteSimple ( SpineSprite )
	:MODEL{
	}

registerComponent( 'SpineSpriteSimple', SpineSpriteSimple )

function SpineSpriteSimple:_createSkeleton()
	return MOAISpineSkeletonSimple.new()
end

function SpineSpriteSimple:onDetach( entity )
	self:stop()
	entity:_detachProp( self.skeleton )
end

--todo: hide some unavailabe functions