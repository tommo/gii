local sqrt,atan2=math.sqrt,math.atan2
local min,max=math.min,math.max
local sin   = math.sin
local asin   = math.asin
local cos   = math.cos
local tan   = math.tan
local atan2 = math.atan2
local pi    = math.pi
local D2R   = pi/180
local R2D   = 180/pi


function euler2quat( x,y,z )
    local r = x * D2R
    local p = y * D2R
    local y = z * D2R
    return
        cos(r/2)*cos(p/2)*cos(y/2)+
        sin(r/2)*sin(p/2)*sin(y/2),

        sin(r/2)*cos(p/2)*cos(y/2)-
        cos(r/2)*sin(p/2)*sin(y/2),

        cos(r/2)*sin(p/2)*cos(y/2)+
        sin(r/2)*cos(p/2)*sin(y/2),

        cos(r/2)*cos(p/2)*sin(y/2)-
        sin(r/2)*sin(p/2)*cos(y/2)
end

function quat2euler( w, x, y, z )
    local euler = {0,0,0}    
    local rx = atan2(2*(w*x+y*z), 1-2*(x*x+y*y)) * R2D
    local ry = asin(2*(w*y-z*x)) * R2D
    local rz = atan2(2*(w*z+x*y),1-2*(y*y+z*z)) * R2D
    return rx, ry, rz
end
