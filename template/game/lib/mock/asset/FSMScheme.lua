module 'mock'

---DEAD LOCK DEBUG HELPER
local DEADLOCK_THRESHOLD = 100 
local DEADLOCK_TRACK     = 5
local DEADLOCK_TRACK_ENABLED = true
--------------------------------------------------------------------
local function buildFSMScheme( scheme )
	-- assert(targetClass,'Target Class required')
	assert( scheme, 'FSM Data required' )
	
	--for deadlock detection
	local trackedStates = {}

	--
	local stateFuncs    = {}

	for name, stateBody in pairs( scheme ) do
		local id         = stateBody.id     --current state id
		local jump       = stateBody.jump   --transition trigger by msg
		local outStates  = stateBody.next   --transition trigger by state return value

		local localName  = stateBody.localName		
		local stepname   = id .. '__step'
		local exitname   = id .. '__exit'
		local entername  = id .. '__enter'
		--generated function
		local function stateStep( self, dt, switchCount )
			----PRE STEP TRANSISTION
			local nextState
			local transMsg, transMsgArg
		
			---STEP
			local step = self[ stepname ]
			local out  = true
			--step return name of next state
			if step then out = step( self, dt ) end
			
			----POST STEP TRANSISTION
			if out and outStates then --approach next state
				nextState = outStates[ out ]
				if not nextState then
					_error( '! error in state:'..name )
					if type( out ) ~= 'string' then
						return error( 'output state name expected' )
					end
					error( 'output state not found:'..tostring( out ) )
				end
			else
				--find triggering msg (post phase)
				while true do
					transMsg, transMsgArg = self:pollMsg()
					if not transMsg then return end
					nextState = jump and jump[ transMsg ]
					if nextState then break end
				end				
			end

			if DEADLOCK_TRACK_ENABLED then
				--DEADLOCK DETECTOR
				switchCount = switchCount + 1
				if switchCount == DEADLOCK_THRESHOLD then 
					trackedStates = {}
				elseif switchCount > DEADLOCK_THRESHOLD then
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
			end
			
			local nextStateBody
			local nextStateName
			--TRANSITION
			local tt = type( nextState )
			if tt == 'string' then --direct transition
				nextStateName = nextState
				local exit = self[ exitname ]
				if exit then --exit previous state
					exit( self, nextStateName, transMsg, transMsgArg )
				end

			else --group transitions
				local l = #nextState
				nextStateName = nextState[l]
				local exit = self[ exitname ]
				if exit then --exit previous state
					exit( self, nextStateName, transMsg, transMsgArg )
				end
				--extra state group exit/enter
				for i = 1, l-1 do
					local funcName = nextState[ i ]
					local func = self[ funcName ]
					if func then
						func( self, name, nextStateName, transMsg, transMsgArg )
					end
				end				
			end

			self:setState( nextStateName )
			nextStateBody = scheme[ nextStateName ]
			if not nextStateBody then
				error( 'state body not found:' .. nextStateName, 2 )
			end
			local enter = self[ nextStateBody.entername ]
			if enter then --entering new state
				enter( self, name, transMsg, transMsgArg )
			end

			--activate and enter new state handler
			local nextFunc = nextStateBody.func
			self.currentStateFunc = nextFunc
			return nextFunc( self, dt, switchCount )
			
		end

		stateBody.func      = stateStep
		stateBody.entername = entername
		stateBody.exitname  = exitname

	end
	local startEnterName = scheme['start'].entername
	local startFunc      = scheme['start'].func
	scheme[0] = function( self, dt )
		local f = self[ startEnterName ]
		if f then
			f( self ) --fsm.start:enter
		end
		self.currentStateFunc = startFunc
		return startFunc( self, dt, 0 )
	end

end

--------------------------------------------------------------------
function FSMSchemeLoader( node )
	local path = node:getObjectFile('def')
	local scheme = dofile( path )
	buildFSMScheme( scheme )
	return scheme
end

registerAssetLoader ( 'fsm_scheme', FSMSchemeLoader )
