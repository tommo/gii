
NO_WINDOW = true
--------------------------------------------------------------------
--TEST CODE
--------------------------------------------------------------------
function OnTestStart()

	module 'mock'
	local function makeTestAction( output, result )
		local testAction = BTAction()
		function testAction:step( context )
			print( output )
			return result or 'ok'
		end
		return testAction
	end

	local function makeTestLongAction( output, steps, result )
		local i = 0
		local testAction = BTAction()
		function testAction:step( context )
			i = i + 1
			print( output, 'step:', i )
			if i >= steps then return result end
			return 'running'
		end
		function testAction:exit( context )
			i = 0
			print('exit', output)
		end
		return testAction
	end

	local context = BTContext()
	local tree = BehaviorTree()
	context:setTree( tree )

	--------------------------------------------------------------------
	-- ---test data
	-- local sequece = tree.root:addNode( SequenceSelector() )
	-- 	sequece:addNode( makeTestLongAction( 'long-ok-1', 2, 'ok' ) )
	-- 	-- sequece:addNode( makeTestLongAction( 'long-ok-1', 2, 'ok' ) )
	-- 	-- sequece:addNode( makeTestAction( 'action-ok-1', 'ok' ) )
	-- 	sequece:addNode( DecoratorAlwaysOK() ):addNode( makeTestAction( 'action-fail', 'fail' ) )
	-- 	sequece:addNode( DecoratorNot() ):addNode( makeTestAction( 'action-fail-3', 'fail' ) )
	-- 	local concurrent1 = sequece:addNode( ConcurrentAndSelector() )	
	-- 		concurrent1:addNode( makeTestLongAction( 'con-ok-1', 3, 'ok' ))
	-- 		local concurrent2 = concurrent1:addNode( ConcurrentOrSelector())
	-- 			concurrent2:addNode( makeTestLongAction( '>con-ok-2', 2, 'fail' ))
	-- 			concurrent2:addNode( makeTestLongAction( '>con-ok-3', 2, 'ok' ))
	-- 	sequece:addNode( makeTestAction( 'action-fail-2', 'fail' ) )

	-- for i = 1 , 10 do
	-- 	print('------------')
	-- 	context:update()
	-- end



	--------------------------------------------------------------------
	-- ---RANDOM NODE TEST
	-- local shuffled = tree.root:addNode( ShuffledSequenceSelector() )
	-- for i= 1, 10 do
	-- 	shuffled:addNode( makeTestAction('act-'..i) )
	-- end
	-- math.randomseed( os.time() / os.clock() )
	-- context:update()


	--------------------------------------------------------------------
	--condition test
	local p = tree.root:addNode( PrioritySelector() )
		local fight = p:addNode( BTCondition('enemy.seen') ):addNode( SequenceSelector() )
			fight:addNode( makeTestAction( 'enemy spotted!' ) ) --shout out
			local weapon = fight:addNode( PrioritySelector() )
				weapon:addNode( BTCondition( 'rifle.ready' ) ):addNode( makeTestAction( 'shoot with rifle' ) )
				weapon:addNode( BTCondition( 'pistol.ready' ) ):addNode( makeTestAction( 'shoot with pistol' ) )
				weapon:addNode( makeTestAction( 'melee attack!!' ) )
		local rest = p:addNode( BTCondition('self.tired') ):addNode( SequenceSelector() )
			rest:addNode( BTCondition('food.ready') ):addNode( makeTestLongAction( 'eating food...', 2 ) )
			rest:addNode( BTCondition('water.ready') ):addNode( makeTestLongAction( 'drinking water...', 2 ) )
			rest:addNode( makeTestAction( 'satisfied!!' ) )
		p:addNode( makeTestAction( 'section clear. do nothing.' ) )

	context['enemy.seen'] = false
	context:update()

	print('-------------')
	context['enemy.seen'] = true
	context:update()

	print('-------------')
	context['pistol.ready'] = true
	context:update()

	print('-------------')
	context['rifle.ready'] = true
	context:update()

	print('-------------')
	context['enemy.seen'] = false
	context['self.tired'] = true
	context['food.ready'] = true
	context['water.ready'] = true
	context:update()

	print('-------------')
	context:update()

	print('-------------')
	context:update()

end

