require 'Class'


local function getPropName( p )
	return p.name or ''
end
local function setPropName( p, n )
	p.name = n
end

Model( MOAIProp, 'MOAIProp' ):update{
	Field 'name' : type('string') :get( getPropName ) :set( setPropName )
}
