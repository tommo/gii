--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------

CLASS:  ParticleSystemConfig()
	:MODEL{
		Field 'particles' :type('int') :meta{ min=0 };
		Field 'sprites'   :type('int') :meta{ min=0 };
		-- Field 'deck'      :asset('int') :hidden();
	}

function ParticleSystemConfig:__init()
	self.particles = 100
	self.sprites   = 100
	self.deck      = false

	self.emitters  = {}
	self.states    = {}
end

function ParticleSystemConfig:update()
end

function ParticleSystemConfig:addEmitterConfig( config )
	config = config or ParticleEmitterConfig()
	table.insert( self.emitters, config )
	return config
end

function ParticleSystemConfig:addStateConfig( config )
	config =  config or ParticleStateConfig() 
	table.insert( self.states, config )
	return config
end

--------------------------------------------------------------------
CLASS:  ParticleEmitterConfig()
	:MODEL {
		Field 'name'      :type('string');
		Field 'type'      :enum{ {'distance', 'distance'}, {'timed', 'timed' } };
		Field 'distance'  :type('number');
		Field 'frequency' :type('number');		
		Field 'magnitude' :type('number');		
		Field 'emission'  :type('number');		
	}

function ParticleEmitterConfig:__init()
	self.name      = 'emitter'
	self.type      = 'timed'
	self.distance  = 5
	self.frequency = 0.1
	self.magnitude = 0
	self.emission  = 10
end


--------------------------------------------------------------------
CLASS:  ParticleStateConfig()
	:MODEL {
		Field 'name'         :type('string') ;
		Field 'life'         :type('number') :range(0);
		Field 'initScript'   :type('string') :hidden();
		Field 'renderScript' :type('string') :hidden();
	}


function ParticleStateConfig:__init()
	self.name         = 'state'
	self.initScript   = ''
	self.renderScript = ''
	self.life         = 1
end

--------------------------------------------------------------------
local tmpConfig = mock.ParticleSystemConfig {
			states={
					{
						render=[[
							-- proc.p.moveAlong()
							sprite()
							proc.sp.align()
							proc.sp.transform{ sy=ease(-1,0), sx=1 }
							sp.opacity=ease(1,0)
						]],

						term=0.5
					},

				},

			emitters = {
					distance = {
						type      = 'distance',
						emission  = 1,
						magnitude = 1,
						distance  = 5,
						angle     = -90,
					},
					timed = {
						frequency = 0.01,
						emission  = 2,
						magnitude = 0,
						rect      = {-10,-10,10,10},
					},
				},

				particles  = 100;
				sprites    = 200;
				blend      = 'add',
				depthTest  = false,
				depthMask  = false,
				shader     = 'tex-color',
				deck       = mock.loadAsset( 'decks/mdd.deck2d/output_atlas' )
		}

CLASS: ParticlePreview ( EditorEntity )

function ParticlePreview:onLoad()
	self:addSibling( CanvasGrid() )
	self:addSibling( CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self:attach( mock.DrawScript{ priority = 1000 } )

	self.testSystem = self:attach( mock.ParticleSystem( tmpConfig ) )
	self.testEmitter = false 

	startUpdateTimer( 60 )
end

function ParticlePreview:onMouseDown( btn, x, y )
	if btn == 'left' and  self.testEmitter then
		self.testEmitter:setLoc( self:wndToWorld( x, y ) )		
	end
end

function ParticlePreview:onMouseMove( x, y )
	if self.testEmitter then
		if scn.inputDevice:isMouseDown('left') then
			self.testEmitter:setLoc( self:wndToWorld( x, y ) )		
		end
	end
end

function ParticlePreview:open( path )
	self.editingConfig = ParticleSystemConfig()
	self.editingConfig:addEmitterConfig().name = 'timed'
	self.editingConfig:addEmitterConfig().name = 'distance'
	self.editingConfig:addStateConfig()

	return self.editingConfig
end

function ParticlePreview:activateItem( item )
	local clas = getClass( item ) 
	if clas == ParticleStateConfig then

	elseif clas == ParticleEmitterConfig then
		if self.testEmitter then self.testEmitter:stop() end
		self.testEmitter = self.testSystem:addEmitter( item.name )		
	end

end


preview = scn:addEntity( ParticlePreview() )

