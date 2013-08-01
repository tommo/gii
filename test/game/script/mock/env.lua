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

require 'mock.core.utils'
require 'mock.core.signal'
require 'mock.core.Class'
require 'mock.core.ClassHelpers'

require 'mock.core.MOAIInterfaces'
require 'mock.core.MOAIHelpers'

require 'mock.tools.DebugHelper'
require 'mock.tools.LogHelper'

require 'mock.core.BehaviorTree'
require 'mock.core.Actor'
require 'mock.core.FSM'

require 'mock.core.MOAIActionHelpers'
require 'mock.core.MOAIPropHelpers'


----------------Core Modules
require 'mock.core.Misc'
----asset
require 'mock.core.AssetLibrary'

----input
require 'mock.core.InputManager'
require 'mock.core.InputRecorder'
require 'mock.core.InputSignal'

----audio
require 'mock.core.Audio'


----game
require 'mock.core.Entity'
require 'mock.core.Component'
require 'mock.core.Scene'
require 'mock.core.Game'
require 'mock.core.EntityHelper'


----------------Asset Loaders
require 'mock.asset.all'
require 'mock.asset.resloader'  --FIXME: removed this when finished porting

----------------Builtin Components
require 'mock.component.all'


----tools
require 'mock.tools.UserAction'


---prefabs
require 'mock.prefabs.PlaceHolder'

---preset
require 'mock.preset.simpleAnimation'


--------------------------------------------------------------------
----EDITOR?
if rawget( _G, 'moei' ) then
	local moei = rawget( _G, 'moei' )
	-- require 'mock.moei'
end

--------------------------------------------------------------------
----Let's POLLUTE THE GLOBAL ENV
--------------------------------
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


