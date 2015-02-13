--[[
* MOCK framework for Moai

* Copyright (C) 2012 Tommo Zhou(tommo.zhou@gmail.com).  All rights reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining
* a copy of this software and associated documentation files (the
* "Software"), to deal in the Software without restriction, including
* without limitation the rights to use, copy, modify, merge, publish,
* distribute, sublicense, and/or sell copies of the Software, and to
* permit persons to whom the Software is furnished to do so, subject to
* the following conditions:
*
* The above copyright notice and this permission notice shall be
* included in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
]]

luaExtName = luaExtName or '.lua'
--------------------------------------------------------------------
module( 'mock',  package.seeall )

-- package.path = './?'..luaExtName
function packagePath(p)
	package.path = package.path..';'..p..'/?'..luaExtName
	package.path = package.path..';'..p..'/?/init'..luaExtName
end


module( 'mock.env', package.seeall )

print( 'LUA Version:', _VERSION )

require 'mock.core'
--------------------------------------------------------------------
require 'mock.task.basic'

----------------Asset Loaders
require 'mock.asset'
require 'mock.asset.resloader'  --FIXME: removed this when finished porting


----------------GUI system
require 'mock.gui'

----------------Builtin Components
require 'mock.component'
require 'mock.entity'

----Effects
require 'mock.effect'

----tools
require 'mock.tools'

---prefabs
require 'mock.prefabs.PlaceHolder'

---preset
require 'mock.preset.simpleAnimation'


--------------------------------------------------------------------
----Let's POLLUTE THE GLOBAL ENV
--------------------------------------------------------------------
function mock.injectGlobalSymbols( env )
	local globalSymbols = {
		'Entity',
		'GlobalEntity',
		'SingleEntity',
		'Scene',
		'game',

		'packagePath',
	}	
	env = env or _G
	for i, k in ipairs( globalSymbols ) do
		rawset( env, k, mock[ k ] )
	end
end

mock.injectGlobalSymbols( _G )

--------------------------------------------------------------------
----INIT
--------------------------------------------------------------------
function mock.init( configPath, fromEditor )
	mock.game:loadConfig( configPath,fromEditor )
end

function mock.start( option )
	mock.game:openEntryScene( option )
	mock.game:start()
end

function mock.printtable( t )
	for k,v in pairs( t ) do
		print (k,v)
	end
end

local shit = MOAIProp.new()
function mock.getShit()
	return {[shit] = true }
end