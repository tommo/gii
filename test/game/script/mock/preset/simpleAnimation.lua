
local function colorAnimations()
	local ATTR_R_COL=MOAIColor.ATTR_R_COL
	local ATTR_G_COL=MOAIColor.ATTR_G_COL
	local ATTR_B_COL=MOAIColor.ATTR_B_COL
	local ATTR_A_COL=MOAIColor.ATTR_A_COL

	local function seekAlpha(prop, t, a0, a1, easetype )
		if a0 then
			prop:setAttr(ATTR_A_COL, a0)
		end
		t=t or 0.5
		return prop:seekAttr(ATTR_A_COL, a1 or 1, t, easetype)
	end

	function fadeIn(prop,t,easetype)
		return seekAlpha(prop,t,0,1,easetype)
	end

	function fadeOut(prop, t, easetype)
		return seekAlpha(prop,t,nil,0,easetype)
	end
		
end

local function transformAnimations()
	function scaleIn(prop,t,easetype)
		prop:setScl(0,0,1)
		return prop:seekScl(1,1,1,t or 0.5,easetype)
	end
	function scaleOut(prop,t,easetype)
		return prop:seekScl(0,0,1,t or 0.5,easetype)
	end
end



colorAnimations()
transformAnimations()
