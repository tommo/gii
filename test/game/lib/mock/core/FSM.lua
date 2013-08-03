module 'mock'

local stateCollectorMT
local setmetatable=setmetatable
local rawget,rawset=rawget,rawset
local pairs=pairs

stateCollectorMT = {
	__index = function( t, k )
		local __state = t.__state
		local __id    = t.__id
		return setmetatable({
			__state = __state and __state..'.'..k or k,
			__id    = __id and __id..'_'..k or '_FSM_'..k,
			__data  = t.__data,
			__class = t.__class
		}	,stateCollectorMT)
	end,

	--got state method
	__newindex=function( t, action, func ) 
		local name  = t.__state
		local id    = t.__id
		local data  = t.__data
		local class = t.__class
		--todo:validation
		local state = data[name]

		if not state then 
			return error( "undefined state:"..name, 2 )
		elseif state.type == 'group' then
			return error( "cannot assign action to state group:"..name, 2 )
		end

		if action~='step' and action~='enter' and action~='exit' then
			return error('unsupported state action:'..action)
		end
		--save under fullname
		local methodName = id..'__'..action
		rawset ( class, methodName, func )
	end

}

---DEAD LOCK DEBUG HELPER
local DEADLOCK_THRESHOLD = 100 
local DEADLOCK_TRACK     = 5

---add FSM state collector/ controller to target class
local function applyFSMTrait( targetClass, FSMData )
	assert(targetClass,'Target Class required')
	assert(FSMData,'FSM Data required')
	
	-----fsm state method collector
	local fsm=setmetatable({
		__state = false,
		__id    = false,
		__data  = FSMData,
		__class = targetClass
		}	,stateCollectorMT)
	targetClass.fsm=fsm
	
	--generate functions
	local pollMsg  = targetClass.pollMsg
	local setState = targetClass.setState

	--for deadlock detection
	local switchCount   = 0  
	local trackedStates = {}

	for name, stateBody in pairs( FSMData ) do
		local id         = stateBody.id     --current state id
		local jump       = stateBody.jump   --transition trigger by msg
		local outStates  = stateBody.next   --transition trigger by state return value

		local localName  = stateBody.localName		
		local stepname   = id .. '__step'
		local exitname   = id .. '__exit'
		local entername  = id .. '__enter'
		--generated function
		local function stateStep( self, dt )
			----PRE STEP TRANSISTION
			local nextState
			local transMsg, transMsgArg
			--find triggering msg (pre phase)
			while true do
				transMsg, transMsgArg = pollMsg(self)
				if not transMsg then break end
				nextState = jump and jump[ transMsg ]
				if nextState then break end
			end
			--if not switching, run a step under current state
			if not nextState then
				---STEP
				local step = self[ stepname ]
				local out  = true
				--step return name of next state
				if step then out = step( self, dt ) end
				
				----POST STEP TRANSISTION
				if out and outStates then --approach next state
					nextState = outStates[ out ]
					if not nextState then
						print( '! error in state:'..name )
						if type( out ) ~= 'string' then
							return error( 'output state name expected' )
						end
						error( 'output state not found:'..tostring( out ) )
					end
				else
					--find triggering msg (post phase)
					while true do
						transMsg, transMsgArg = pollMsg( self )
						if not transMsg then return end
						nextState = jump and jump[ transMsg ]
						if nextState then break end
					end				
				end

			end

			--DEADLOCK DETECTOR
			switchCount = switchCount + 1
			if switchCount > DEADLOCK_THRESHOLD then 
				table.insert( trackedStates, name )
				if switchCount > DEADLOCK_THRESHOLD + DEADLOCK_TRACK then
					--state traceback
					print( "state switch deadlock:" )
					for i, s in ipairs( trackedStates ) do 
						print( i, s )
					end
					game:debugStop()
					error('TERMINATED') --terminate
				end
			end
			
			--TRANSITION
			local nextStateName = nextState.name
			local exit = self[ exitname ]
			if exit then --exit previous state
				exit( self, nextStateName, nextState.localName, transMsg, transMsgArg )
			end
			setState( self, nextStateName )
			local enter = self[ nextState.entername ]
			if enter then --entering new state
				enter( self, name, localName, transMsg, transMsgArg )
			end
			--activate and enter new state handler
			local nextFunc = nextState.func
			self.currentStateFunc = nextFunc
			return nextFunc( self, dt )
		end

		stateBody.func      = stateStep
		stateBody.entername = entername
		stateBody.exitname  = exitname

	end
	
	function targetClass:updateFSM( dt )
		local func = self.currentStateFunc
		if func then 
			switchCount = 0
			return func( self, dt )
		end
	end
	
	function targetClass:forceChangeState(s)
		local data=FSMData[s]
		if not data then error('state not defined:'..s) end
		error('not implemented')
		--TODO: implement this
	end

	--use for make state-specific variable table
	function targetClass:getEnv( name ) 
		local envtable = self.envtable
		if not envtable then
			envtable = {}
			self.envtable = envtable
		end
		local t = envtable[ name ]
		if not t then
			t={}
			envtable[ name ]=t
		end
		return t
	end

	--set entry
	targetClass.currentStateFunc = FSMData['start'].func
	return fsm

end

Actor.applyFSMTrait = applyFSMTrait
