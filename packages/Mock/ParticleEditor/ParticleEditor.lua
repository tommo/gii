--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------

local tmpConfig = mock.ParticleSystemConfig {
			states={
					{
						render=loadstring[[
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
						frequency = 0.1,
						emission  = 10,
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
				deck       = mock.loadAsset( 'decks/icons.deck2d/coin' )
		}

CLASS: ParticlePreview ( EditorEntity )

function ParticlePreview:onLoad()
	self:addSibling( CanvasGrid() )
	self:addSibling( CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self:attach( mock.DrawScript{ priority = 1000 } )

	self.psystem = self:attach( mock.ParticleSystem( tmpConfig ) )
	self.testEmitter = self.psystem:addEmitter( 'distance' )

	startUpdateTimer( 60 )
end

function ParticlePreview:onMouseDown( btn, x, y )
	if self.testEmitter then
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

function ParticlePreview:openParticleSystem( path )

end


local preview = scn:addEntity( ParticlePreview() )
