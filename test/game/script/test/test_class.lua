function OnTestStart()
	CLASS: BaseBase ()

	function BaseBase:onUpdate()
	end

	CLASS: Base ( BaseBase )

	function Base:onUpdate()
	end


	CLASS: Derived ( Base )
		:MEMBER{}
		
	function Derived:__onInit()
	end

	function Derived:onUpdate()
	end


	local d=Derived()
	assert(d.onUpdate~=Base.onUpdate)
	assert(d.__super==Base)
end