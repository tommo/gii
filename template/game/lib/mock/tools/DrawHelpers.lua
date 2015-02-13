local draw = MOAIDraw
local pi, sin, cos, atan2 = math.pi, math.sin, math.cos, math.atan2
local D2R = pi/180
local R2D = 180/pi

local drawLine = draw.drawLine
local fillFan  = draw.fillFan

--------------------------------------------------------------------
--ARROW
--------------------------------------------------------------------
function MOAIDraw.drawArrow( x,y, x1,y1, size, angle, solid )
	drawLine( x,y, x1,y1 )
	local dx = x1 - x
	local dy = y1 - y
	local a0 = atan2( dy, dx )
	angle = angle or 30
	local angle = angle * D2R
	size =  size or 20
	local a2 = a0 + angle
	local a3 = a0 - angle
	local x2,y2 = x1 - size * cos( a2 ), y1 - size * sin( a2 )
	local x3,y3 = x1 - size * cos( a3 ), y1 - size * sin( a3 )
	if solid then
		fillFan( x1,y1, x2,y2, x3,y3 )
	else
		drawLine( x1,y1, x2,y2 )
		drawLine( x1,y1, x3,y3 )
	end
end

function MOAIDraw.fillArrow( x,y, x1,y1, size, angle )
	return MOAIDraw.drawArrow( x,y, x1,y1, size, angle, true )
end

--------------------------------------------------------------------
--
--------------------------------------------------------------------

function MOAIDraw.drawEmitter( x,y, size )
	size =  size or 30
	MOAIDraw.drawCircle( x,y, size )
	MOAIDraw.drawCircle( x,y, size/6 )
	return MOAIDraw.fillArrow( x+size/6, y, x+size, y, size/3 )
end


--------------------------------------------------------------------
--------------------------------------------------------------------
local cos, sin = math.cosd, math.sind
function MOAIDraw.drawArc( x,y, r, a0,a1, step )
	a0 = a0 or 90
	a1 = a1 or 0
	step = step or 10
	r = r or 100
	local spans = math.abs( math.ceil( (a1-a0)/step ) )
	if spans == 0 then return end
	local astep = ( a1 - a0 )/spans
	local points = {}
	for i = 0, spans do
		local a = a0 + astep * i 
		local xx = cos( a ) * r + x
		local yy = sin( a ) * r + y
		points[ i*2+1 ] = xx
		points[ i*2+2 ] = yy
	end
	points[ spans*2 + 3 ] = nil --end the array
	return MOAIDraw.drawLine( points )
end

function MOAIDraw.drawRadialLine( x,y, angle, off0, off1 )
	local c,s
	c = cos( angle )
	s = sin( angle )	
	return MOAIDraw.drawLine( c * off0 + x, s * off0 + y, c * off1 + x, s * off1 + y )
end

-- function MOAIDraw.drawDottedLine( x,y, x1,y1, s1, s2 )
-- 	s1 = s1 or 5
-- 	s2 = s2 or 5	
-- end
