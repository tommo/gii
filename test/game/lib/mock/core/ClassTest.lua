require 'Class'

CLASS: Foo()
function Foo:__init()
	print 'init foo'
end


CLASS: Bar( Foo )
function Bar:__init()
	print 'init bar'
end

Bar()