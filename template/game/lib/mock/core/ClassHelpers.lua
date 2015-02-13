function _wrapMethod( class, fieldname, methodname, arg, ... )
	local selfPart
	if fieldname:startwith( ':' ) then
		selfPart = 'self'..fieldname
	else
		selfPart = 'self.'..fieldname
	end
	local f = loadstring(
			string.format(
				"return function( self, ... ) return %s:%s( ... ) end",
				selfPart,
				methodname
			)
			)()
	class[methodname]=f
end

function _wrapMethods( class, fieldname, methodnames )
	for i,n in ipairs(methodnames) do
		_wrapMethod( class, fieldname, n )
	end
end

function _wrapAttrGetter(class,fieldname,attr,methodname)
	local selfPart
	if fieldname:startwith( ':' ) then
		selfPart = 'self'..fieldname
	else
		selfPart = 'self.'..fieldname
	end
	local f=loadstring(
		string.format(
			[[return function(self)
								return %s:getAttr(%d)
						end
			]]
			, selfPart, attr)
	)
	class[methodname] = f()
end

function _wrapAttrGetterBoolean(class,fieldname,attr,methodname)
	local selfPart
	if fieldname:startwith( ':' ) then
		selfPart = 'self'..fieldname
	else
		selfPart = 'self.'..fieldname
	end
	local f=loadstring(
		string.format(
			[[return function(self)
								return %s:getAttr(%d) ~= 0
						end
			]]
			,selfPart, attr )
	)
	class[methodname] = f()
end

function _wrapAttrSetter(class,fieldname,attr,methodname)
	local selfPart
	if fieldname:startwith( ':' ) then
		selfPart = 'self'..fieldname
	else
		selfPart = 'self.'..fieldname
	end
	local f=loadstring(
		string.format(
			[[return function(self, v )
								return %s:setAttr(%d, v )
						end
			]]
			,selfPart, attr )
		)
	class[methodname] = f()
end

function _wrapAttrSeeker(class,fieldname,attr,methodname)
	local selfPart
	if fieldname:startwith( ':' ) then
		selfPart = 'self'..fieldname
	else
		selfPart = 'self.'..fieldname
	end
	local f=loadstring(
		string.format(
			[[return function( self, v, t, easeType )
								return %s:seekAttr( %d, v, t, easeType )
						end
			]]
			,selfPart ,attr)
	)
	class[methodname] = f()
end

function _wrapAttrMover(class,fieldname,attr,methodname)
	local selfPart
	if fieldname:startwith( ':' ) then
		selfPart = 'self'..fieldname
	else
		selfPart = 'self.'..fieldname
	end
	local f=loadstring(
		string.format(
			[[return function( self, v, t, easeType )
								return %s:moveAttr( %d, v, t, easeType )
						end
			]]
			,selfPart ,attr)
	)
	class[methodname] = f()
end


function _wrapAttrGetSet( class, fieldname, attr, propertyName)
	_wrapAttrGetter( class, fieldname, attr, 'get'..propertyName )
	_wrapAttrSetter( class, fieldname, attr, 'set'..propertyName )
end

function _wrapAttrGetSetSeekMove( class, fieldname, attr, propertyName)
	_wrapAttrGetter( class, fieldname, attr, 'get'..propertyName )
	_wrapAttrSetter( class, fieldname, attr, 'set'..propertyName )
	_wrapAttrSeeker( class, fieldname, attr, 'seek'..propertyName )
	_wrapAttrMover( class, fieldname, attr, 'move'..propertyName )
end
