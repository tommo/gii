----------------------------------------------------------------
-- Copyright (c) 2010-2011 Zipline Games, Inc. 
-- All Rights Reserved. 
-- http://getmoai.com
----------------------------------------------------------------
-- dofile"MOAIInterfaces.lua"
NO_WINDOW=true
function OnTestStart()
	MOAISim.openWindow ( "test", 320, 480 )

	viewport = MOAIViewport.new ()
	viewport:setSize ( 320, 480 )
	viewport:setScale ( 320, 480 )

	layer = MOAILayer2D.new ()
	layer:setViewport ( viewport )
	MOAISim.pushRenderPass ( layer )

	longstring='！度ペ殩꭮ルロ !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~在大到こ带程为主失模次そ链元锁义素の奇所游へ子录よ全教传落师经欢获戏单条典治潜来统兽种里合回量イ起崛分エ热上线于对金黄球个有一角独咒完连ス长式。力成徒学チ语的开迎得ート记譯首うン初最'
	charcodes = ' abcdefg你好'
	texts = {'abc','你好','def','这是','没有预存的字符串',longstring}

	font = MOAIFont.new ()
	font:loadFromTTF ( '/Users/tommo/res/fonts/msyh.ttf', longstring, 12, 95 )

	textbox = MOAITextBox.new ()
	textbox:setString ( 'a' )
	textbox:setFont ( font )
	textbox:setTextSize ( 12, 95 )
	textbox:setRect ( -150, -230, 150, 230 )
	textbox:setYFlip ( true )
	layer:insertProp ( textbox )

	MOAICoroutine.new():run(function()
		for i, t in ipairs(texts) do 
			textbox:setString(t)
			textbox:setTextSize ( 12, math.random()*80+10 )
			for i=1, 100 do coroutine.yield() end
		end
	end
	)

	MOAICoroutine.new():run(function()
		while true do
			for i=1, 10 do coroutine.yield()  end
			io.flush()
		end
	end
	)
end