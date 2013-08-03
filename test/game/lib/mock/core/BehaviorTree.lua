--------------------------------------------------------------------
--[[
	Behavior Tree implementation by Tommo.zhou
	Note:
		* structure = (multiple CONTEXT Instances) -> (single Tree Instance)
		* the implementaion heavily relies on tail-recursive feature of Lua
		* the concurrent selector code might be a little messy...

]]
--------------------------------------------------------------------
local remove, insert = table.remove, table.insert
local ipairs, pairs = ipairs, pairs

module 'mock'

--------------------------------------------------------------------
local function randi( k )
	 return math.floor( math.random() * k ) + 1
end

local function makeShuffleList( range )
	local t = {}
	for i = 1, range do
		t[i] = i
	end
	for i = range, 2, -1 do
		local k = randi( i )
		t[ k ], t[ i ] = t[ i ], t[ k ]
	end
	return t
end

--------------------------------------------------------------------
---Action ( base class for userdefined object behavior )
--------------------------------------------------------------------
CLASS: BTAction ()
	:MEMBER{
		serialize = false,
		start = false,
		stop = false
	}

function BTAction:step( dt )
	--pass
	return 'ok'
end

--------------------------------------------------------------------
-- BTContext: used as a component
CLASS: BTContext ()

local startCountDown = 0
function BTContext:__init()
	self._actionTable = {}
	self._runningQueue = {}
	self._runningQueueNeedShrink = false
	self._tree = false
	self._active = true
	self._activeActions = {}

	self._evaluateInterval = 10
	--use different countdown start value to make the update sparse
	startCountDown = startCountDown + 1
	self._evaluateCountDown = startCountDown % self._evaluateInterval
	self._conditions = {}
	
end

function BTContext:onAttach( owner )
	self._owner = owner
	--attach self to scene update 
	owner.scene:addUpdateListener( self )
end

function BTContext:onDetach( owner )
	owner.scene:removeUpdateListener( self )
	self._owner = nil
	self._activeActions = nil
end

function BTContext:getOwner()
	return self._owner
end

function BTContext:setActive( a )
	self._active = a
end

function BTContext:isActive()
	return self._active
end

function BTContext:setTree( tree, validate )
	self._tree = tree
	if validate then self:validateActions() end
end


---------
function BTContext:setActionTable( actions )
	if not actions then error( 'action table expected', 2 ) end
	self._actionTable = actions
end

function BTContext:validateActions()
	return self._tree.root:validate( self )
end

function BTContext:requestAction( actionNode )
	local _activeActions = self._activeActions
	local action = _activeActions[ actionNode ]
	--TODO: should we recreate action every time??
	if action then return action end

	local name = actionNode.actionName
	local actionClas = self._actionTable[ name ]
	if not actionClas then
		error( 'unregistered action class:'..name, 2 )
	end
	local action = actionClas()	
	self._activeActions[ actionNode ] = action
	
	return action
end

function BTContext:setConditionTable( t )
	self._conditions = t
end

function BTContext:getConditionTable()
	return self._conditions
end

function BTContext:getCondition( name )
	return self._conditions[ name ]
end

function BTContext:setCondition( name, v )
	self._conditions[ name ] = v
end

---------
function BTContext:scheduleUpdate()
	self._evaluateCountDown = 0
end

function BTContext:completeEvaluation( res )
	--TODO: delegate?
	-- print('>> done <<\n')
	self._runningQueue = {}
	return 'complete'
end

function BTContext:onUpdate( dt )
	local running = self:updateRunningNodes( dt )
	if not running and self._evaluateCountDown <= 0 then
		self._evaluateCountDown = self._evaluateInterval
		self._tree.root:execute( self )
	else
		self._evaluateCountDown = self._evaluateCountDown - 1
	end
end

function BTContext:updateRunningNodes( delta )
	local _runningQueue = self._runningQueue
	local count = #_runningQueue
	if count == 0 then return false end
	for i = 1, count do 
		--only execute currently available nodes, new nodes left to next update
		local node = _runningQueue[ i ]
		if node then --might have already removed
			if node:update( self, delta ) == 'complete' then return 'complete' end
		else --no more execution pending
			break
		end
	end
	--shrink running queue?
	if self._runningQueueNeedShrink then
		local newQueue = {}
		local j = 1
		for i, node in ipairs( _runningQueue ) do
			if node then newQueue[ j ] = node ; j = j + 1 end
		end
		self._runningQueue = newQueue
	end
	return true
end

function BTContext:addRunningNode( n, action )
	return insert( self._runningQueue, n )
end

function BTContext:removeRunningChildNodes( parentNode )
	self._runningQueueNeedShrink = true
	local _runningQueue = self._runningQueue
	local _activeActions = self._activeActions
	for i, node in ipairs( _runningQueue ) do
		if node and node:hasParent( parentNode ) then
			--stop this & exclude this in new queue
			--TODO: stop the nodes in reversed order?
			local action = _activeActions[ node ]
			-- _activeActions[ node ] = nil
			local stop = action.stop
			if stop then stop( action, self ) end
			_runningQueue[ i ] = false --remove later
		end		
	end
end

function BTContext:removeRunningNode( nodeToRemove )
	self._runningQueueNeedShrink = true
	local _activeActions = self._activeActions
	local _runningQueue = self._runningQueue
	--just remove one node
	for i, node in ipairs( _runningQueue ) do
		if node == nodeToRemove then
			_runningQueue[ i ] = false
			-- _activeActions[ nodeToRemove ] = nil
			break
		end
	end
end

function BTContext:saveState()
	--TODO:...
end

function BTContext:loadState( data )
	--TODO:...
end

--------------------------------------------------------------------
--------------------------------------------------------------------
CLASS: BehaviorTree ()
function BehaviorTree:__init()
	self.root = BTRootNode()
end

local function loadNode( data )	
	local nodeType, value, children = data.type, data.value, data.children
	if nodeType == 'commented' then 
		return false --ignore
	end
	local class = assert( BehaviorTreeNodeTypes[ nodeType ], 'unknown node type:'..tostring(nodeType) )
	local node = class()
	if nodeType == 'condition' or nodeType == 'condition_not' then
		if value:sub( -2, -1 ) == '()' then
			node.conditionName = value:sub( 1, -3 )
			node.conditionType = 'call'
		else
			node.conditionName = value
			node.conditionType = 'field'
		end

	elseif nodeType == 'action' then
		node.actionName = value
		--TODO: redirect action to object ?	
	end
	if children then
		for i, childData in ipairs( children ) do
			local childNode = loadNode( childData )
			if childNode then	node:addNode( childNode ) end
		end
	end

	return node
end

function BehaviorTree:load( data )
	self.root = loadNode( data )	
	return self
end


--------------------------------------------------------------------
--BTNode: base class of behavior tree nodes
--@ execute( context )  reimplement this for specific behavior
--------------------------------------------------------------------
CLASS: BTNode ()
function BTNode:__init()
	self.name = 'BTNode'
	self.parentNode = false
	self.depth = 0 --depth in tree
end

function BTNode:execute( context )
	error('not implemented execute in :'..self:getType())
end

function BTNode:validate( context )
	return true
end

function BTNode:getType() --for debug purpose
	return 'BTNode'
end

function BTNode:addNode( n )
	error( 'no subnode or targetnode support for '..self:getType(),2)
end


BTNode.cancel = false

function BTNode:hasParent( node )
	if node.depth >= self.depth then return false end
	local p = self.parentNode
	while p do
		if p == node then return true end
		p = p.parentNode
	end
	return false
end

function BTNode:returnUpLevel( res, context )
	return self.parentNode:resumeFromChild( self, res, context )
end


--------------------------------------------------------------------
--Action Node in behavior tree, can have 'running' state
--------------------------------------------------------------------
CLASS: BTActionNode ( BTNode )
function BTActionNode:__init( name )
	self.actionName = name
end

function BTActionNode:getType()
	return 'Action'
end

function BTActionNode:execute( context )
	local act = context:requestAction( self )
	local start = act.start
	if start then start( act, context, self ) end
	return self:update( context, 0, true )
end

function BTActionNode:update( context, delta, fromExecute )
	local act = context._activeActions[ self ]
	local res = act:step( context, delta, self )	
	assert ( 
		res == 'ok' or res == 'fail' or res=='running', 
		string.format('invalid action return value inside %s: %s', self.actionName, tostring( res ) )
		)
	if res ~= 'running' then
		return self:returnUpLevel( res, context )
	end
	if fromExecute then
		--first time we run the update, put it in queue
		context:addRunningNode( self )
	end
	return 'running'
end

function BTActionNode:returnUpLevel( res, context )
	context:removeRunningNode( self )
	local act = context._activeActions[ self ]
	local stop = act.stop
	if stop then stop( act, context, self ) end
	return self.parentNode:resumeFromChild( self, res, context )
end

function BTActionNode:validate( context )
	assert( context:requestAction( self ), 'action not registered for:'..self.actionName )
end

--------------------------------------------------------------------
--------------------------------------------------------------------
CLASS: BTCondition ( BTNode )
function BTCondition:__init( conditionName )
	self.conditionName = conditionName
end

function BTCondition:getType()
	return 'Condition'
end

function BTCondition:setCondition( name )
	self.conditionName = name
end

function BTCondition:addNode( node )
	--single child node
	assert( not self.targetNode, 'condtion node can only have ONE target node.' )
	self.targetNode = node
	node.parentNode = self
	node.depth = self.depth + 1
	return node
end

function BTCondition:execute( context )
	local res = context:getCondition( self.conditionName )
	if res then
		local target = self.targetNode
		if target then --condition node can link a child node
			return target:execute( context )
		else
			return self:returnUpLevel( 'ok', context )
		end
	else
		return self:returnUpLevel( 'fail', context )
	end
end

function BTCondition:resumeFromChild( child, res, context )
	return self:returnUpLevel( res, context )
end

function BTCondition:validate( context )
	if self.targetNode then return self.targetNode:validate( context ) end
	return true
end

--------------------------------------------------------------------
CLASS: BTConditionNot ( BTCondition )
function BTConditionNot:getType()
	return 'ConditionNot'
end

function BTConditionNot:execute( context )
	local res = context:getCondition( self.conditionName )
	if not res then
		local target = self.targetNode
		if target then --condition node can link a child node
			return target:execute( context )
		else
			return self:returnUpLevel( 'ok', context )
		end
	else
		return self:returnUpLevel( 'fail', context )
	end
end

--------------------------------------------------------------------
--COMPOSITION
--------------------------------------------------------------------
--base class of composition nodes such as priority / sequence/ concurrent
--------------------------------------------------------------------
CLASS: BTCompositedNode ( BTNode )
function BTCompositedNode:__init( name )
	self.children = {}
	self.childrenCount = 0
	self.name = name
end

function BTCompositedNode:getType() --for debug purpose
	return 'BTCompositedNode'
end

function BTCompositedNode:resumeFromChild( node, result, context )
	error ('implement resumeFromChild !!')
end

--The tree must be constructed from top down,  to ensure right depth value
function BTCompositedNode:validate( context )
	for i, nn in ipairs( self.children ) do
		if not nn:validate( context ) then return false end
	end
	return true
end

function BTCompositedNode:addNode( node )
	node.parentNode = self
	node.depth = self.depth + 1
	insert( self.children, node )
	self.childrenCount = #self.children
	return node
end

function BTCompositedNode:removeNode( node ) --might be useful for editor?
	node.parentNode = false
	local children = self.children
	for i, nn in ipairs( children ) do
		if nn == node then
			remove( children, i )
			self.childrenCount = #children
			break
		end
	end
	return node
end

--------------------------------------------------------------------
--------------------------------------------------------------------
CLASS: BTPrioritySelector ( BTCompositedNode )
function BTPrioritySelector:getType()
	return 'BTPrioritySelector'
end

function BTPrioritySelector:execute( context )
	local index = context[ self ] or 1
	local child = self.children[ index ]
	if not child then
		context[ self ] = false
		return self:returnUpLevel( 'fail', context )
	end
	--run child node
	context[ self ] = index + 1
	return child:execute( context )
end

function BTPrioritySelector:resumeFromChild( child, res, context )
	if res == 'ok' then  --done
		context[ self ] = false
		return self:returnUpLevel( 'ok', context )
	end 
	return self:execute( context )
end


--------------------------------------------------------------------
CLASS: BTRootNode ( BTPrioritySelector )
function BTRootNode:getType()
	return 'RootNode'
end

function BTRootNode:returnUpLevel( res, context )
	return context:completeEvaluation( res )
end



--------------------------------------------------------------------
CLASS: BTSequenceSelector ( BTCompositedNode )
function BTSequenceSelector:getType()
	return 'BTSequenceSelector'
end

function BTSequenceSelector:execute( context )
	local index = context[ self ] or 1
	local child = self.children[ index ]
	if not child then
		context[ self ] = false
		return self:returnUpLevel( 'ok', context )
	end
	--run child node
	context[ self ] = index + 1
	return child:execute( context )
end

function BTSequenceSelector:resumeFromChild( child, res, context )
	if res == 'fail' then  --done
		context[ self ] = false
		return self:returnUpLevel( 'fail', context )
	end 
	return self:execute( context )
end

--------------------------------------------------------------------
CLASS: BTRandomSelector ( BTCompositedNode )
function BTRandomSelector:getType()
	return 'BTRandomSelector'
end

function BTRandomSelector:execute( context )
	local index = randi( self.childrenCount )
	local child = self.children[ index ]
	return child:execute( context )
end

function BTRandomSelector:resumeFromChild( child, res, context )
	return self:returnUpLevel( res, context )
end

--------------------------------------------------------------------
CLASS: BTShuffledSequenceSelector ( BTCompositedNode )
function BTShuffledSequenceSelector:getType()
	return 'BTShuffledSequenceSelector'
end

function BTShuffledSequenceSelector:execute( context )
	local executeList = context[ self ]
	if not executeList then
		executeList = makeShuffleList( self.childrenCount )
		context[ self ] = executeList
	end

	local index = remove( executeList )
	if index then
		local child = self.children[ index ]
		return child:execute( context )
	else
		--queue empty
		context[ self ] = false
		return self:returnUpLevel( 'ok', context )
	end
end

function BTShuffledSequenceSelector:resumeFromChild( child, res, context )
	if res == 'fail' then
		context[ self ] = false
		return self:returnUpLevel( 'fail', context )
	end
	return self:execute( context )
end

--------------------------------------------------------------------
--------------------------------------------------------------------
--fails when either of concurrent child node fails
CLASS: BTConcurrentAndSelector ( BTCompositedNode )
function BTConcurrentAndSelector:getType()
	return 'BTConcurrentAndSelector'
end

function BTConcurrentAndSelector:execute( context )
	local env = context[ self ]
	if not env then 
		env = { executeIndex = 0, okCount = 0 }
		context[ self ] = env
	end
	
	if env.executeIndex < self.childrenCount then --more to execute
		local index = env.executeIndex + 1
		local child = self.children[ index ]
		env.executeIndex = index
		local res = child:execute( context )
		if res == 'complete' then return 'complete' end --already gone back to root
		--assert( res == 'running' )
		return self:execute( context ) --loop to execute rest of the children
	end

	if env.okCount >= self.childrenCount then --all ok, now resume to parent
		--reset env
		env.executeIndex = 0
		env.okCount = 0 
		return self:returnUpLevel( 'ok', context )
	end

	return 'running'
end

function BTConcurrentAndSelector:resumeFromChild( child, res, context )
	local env = context[ self ]
	if res == 'fail' then --let other node die!
		--reset env
		env.executeIndex = 0
		env.okCount = 0 

		context:removeRunningChildNodes( self ) --remove all child node
		return self:returnUpLevel( 'fail', context )
	end
	--assert res == 'ok'
	env.okCount = env.okCount + 1
	return self:execute( context )
end

--------------------------------------------------------------------
--fails when both of concurrent child node fails
CLASS: BTConcurrentOrSelector ( BTCompositedNode )
--CONTEXT = failedChildCount
function BTConcurrentOrSelector:getType()
	return 'BTConcurrentOrSelector'
end

function BTConcurrentOrSelector:execute( context )
	local env = context[ self ]
	if not env then 
		env = { executeIndex = 0, failCount = 0, okCount = 0 }
		context[ self ] = env
	end
	
	if env.executeIndex < self.childrenCount then --more to execute
		local index = env.executeIndex + 1
		local child = self.children[ index ]
		env.executeIndex = index
		local res = child:execute( context )
		if res == 'complete' then return 'complete' end --already gone back to root
		--assert( res == 'running' )
		return self:execute( context ) --loop to execute rest of the children
	end

	if env.okCount + env.failCount >= self.childrenCount then --all ok, now resume to parent
		local fail = env.okCount == 0 
		--reset env
		env.executeIndex = 0
		env.failCount = 0 
		env.okCount = 0 
		return self:returnUpLevel( fail and 'fail' or 'ok', context )
	end

	return 'running'
end

function BTConcurrentOrSelector:resumeFromChild( child, res, context )
	local env = context[ self ]
	if res == 'fail' then --let other node die!
		env.failCount = env.failCount + 1
	else
		env.okCount = env.okCount + 1
	end
	return self:execute( context )
end




--------------------------------------------------------------------
--ok when either of concurrent child node ok
CLASS: BTConcurrentEitherSelector ( BTCompositedNode )
function BTConcurrentEitherSelector:getType()
	return 'BTConcurrentEitherSelector'
end

function BTConcurrentEitherSelector:execute( context )
	local env = context[ self ]
	if not env then 
		env = { executeIndex = 0, failCount = 0 }
		context[ self ] = env
	end
	if env.executeIndex < self.childrenCount then --more to execute
		local index = env.executeIndex + 1
		local child = self.children[ index ]
		env.executeIndex = index
		local res = child:execute( context )
		if res == 'complete' then return 'complete' end --already gone back to root
		--assert( res == 'running' )
		return self:execute( context ) --loop to execute rest of the children
	end

	if env.failCount >= self.childrenCount then --all ok, now resume to parent
		--reset env
		env.executeIndex = 0
		env.failCount = 0 
		return self:returnUpLevel( 'fail', context )
	end

	return 'running'
end

function BTConcurrentEitherSelector:resumeFromChild( child, res, context )
	local env = context[ self ]
	if res == 'ok' then --let other node die!
		--reset env
		env.executeIndex = 0
		env.failCount = 0 

		context:removeRunningChildNodes( self ) --remove all child node
		return self:returnUpLevel( 'ok', context )
	end
	--assert res == 'fail'
	env.failCount = env.failCount + 1
	return self:execute( context )
end


--------------------------------------------------------------------
--DECORATOR
---------------------------------------------------------------------
CLASS: BTDecorator ( BTNode )
function BTDecorator:getType()
	return 'Decorator'
end

function BTDecorator:addNode( node )
	--single child node
	assert( not self.targetNode, 'decoration node can only have ONE target node.' )
	self.targetNode = node
	node.parentNode = self
	node.depth = self.depth + 1
	return node
end

function BTDecorator:execute( context )
	return self.targetNode:execute( context )
end

function BTDecorator:validate( context )
	return self.targetNode:validate( context )
end
--------------------------------------------------------------------
CLASS: BTDecoratorNot ( BTDecorator )
function BTDecoratorNot:getType()
	return 'BTDecoratorNot'
end

function BTDecoratorNot:resumeFromChild( child, res, context )
	res = res == 'ok' and 'fail' or 'ok'
	return self:returnUpLevel( res, context )
end

--------------------------------------------------------------------
CLASS: BTDecoratorAlwaysOK ( BTDecorator )
function BTDecoratorAlwaysOK:getType()
	return 'BTDecoratorAlwaysOK'
end

function BTDecoratorAlwaysOK:execute( context )
	if self.targetNode then
		return self.targetNode:execute( context )
	else
		return self:returnUpLevel( 'ok', context )
	end
end

function BTDecoratorAlwaysOK:resumeFromChild( child, res, context )
	return self:returnUpLevel( 'ok', context )
end

--------------------------------------------------------------------
CLASS: BTDecoratorAlwaysFail ( BTDecorator )
function BTDecoratorAlwaysFail:getType()
	return 'BTDecoratorAlwaysFail'
end

function BTDecoratorAlwaysFail:execute( context )
	if self.targetNode then
		return self.targetNode:execute( context )
	else
		return self:returnUpLevel( 'fail', context )
	end
end

function BTDecoratorAlwaysFail:resumeFromChild( child, res, context )
	return self:returnUpLevel( 'fail', context )
end

--------------------------------------------------------------------
CLASS: BTDecoratorRepeatUntil ( BTDecorator )
function BTDecoratorRepeatUntil:getType()
	return 'BTDecoratorRepeatUntil'
end

function BTDecoratorRepeatUntil:resumeFromChild( child, res, context )
	if res == 'ok' then
		return self:returnUpLevel( 'ok', context )
	else --fail
		context:addRunningNode( self ) 
		return 'running'
	end
end

function BTDecoratorRepeatUntil:update( context )
	context:removeRunningNode( self ) 
	return self:execute( context )
end

--------------------------------------------------------------------

BehaviorTreeNodeTypes = {
	['root']              = BTRootNode ;
	['condition']         = BTCondition ;
	['condition_not']     = BTConditionNot ;
	['action']            = BTActionNode ;
	['priority']          = BTPrioritySelector ;
	['sequence']          = BTSequenceSelector ;
	['random']            = BTRandomSelector ;
	['shuffled']          = BTShuffledSequenceSelector ;
	['concurrent_and']    = BTConcurrentAndSelector ;
	['concurrent_or']     = BTConcurrentOrSelector ;
	['concurrent_either'] = BTConcurrentEitherSelector ;
	['decorator_not']     = BTDecoratorNot ;
	['decorator_ok']      = BTDecoratorAlwaysOK ;
	['decorator_fail']    = BTDecoratorAlwaysFail ;
	['decorator_repeat']  = BTDecoratorRepeatUntil ;
}
