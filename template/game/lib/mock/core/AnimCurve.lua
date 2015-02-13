module 'mock'
--TODO: a generic anim curve & attr manager

--------------------------------------------------------------------
--Simple helpers
--------------------------------------------------------------------

-- function simpleCurveAnim()
-- 	local anim = MOAIAnim.new()
-- end

function buildAnimCurve( keys )
	local curve = MOAIAnimCurve.new()
	local count = #keys
	curve:reserveKeys( count )
	for i, entry in ipairs( keys ) do
		local t, value, ease, weight = unpack( entry )
		curve:setKey( i, t, value, ease or MOAIEaseType.LINEAR, weight or 1 )
	end
	return curve
end

function buildAttrAnim( prop, attr, keys, animMode, asDelta )
	local curve = buildAnimCurve( keys )	
	local anim = MOAIAnim.new()
	anim:reserveLinks( 1 )
	anim:setLink( 1, curve, prop, attr, asDelta )
	anim:setMode( animMode or MOAITimer.NORMAL )	
	return anim, curve
end

function buildMultiAttrAnim( prop, attrs, keys, animMode, asDelta )
	local curve = buildAnimCurve( keys )	
	local anim = MOAIAnim.new()
	anim:setMode( animMode or MOAITimer.NORMAL )	
	local count = #attrs
	anim:reserveLinks( count )
	for i, attr in ipairs( attrs ) do
		anim:setLink( i, curve, prop, attr, asDelta )
	end
	return anim, curve
end

function buildSimpleRotationAnim( prop, from, to, duration, easeMode, animMode, asDelta )
	easeMode = easeMode or MOAIEaseType.LINEAR
	return buildAttrAnim(
			prop,
			MOAIProp.ATTR_Z_ROT,
			{
				{ 0, from },
				{ duration, to, easeMode },
			},
			animMode,
			asDelta
		)
end

