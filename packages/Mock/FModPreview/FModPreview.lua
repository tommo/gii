--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------
CLASS: FModPreview ( mock.Entity )
function FModPreview:onLoad()
	self.prop = self:addProp{
		blend = 'alpha'
	}
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self.zoom = 1
	self.soundSource = self:attach( mock.SoundSource() )
	self.playingEvent = false
end

function FModPreview:setEvent( path )
	if path then
		local event = mock.loadAsset( path )
		self.target = event
	else
		if self.playingEvent then
			self:togglePlaying()
		end
	end
end

function FModPreview:togglePlaying()
	if self.playingEvent then
		self:stopPlaying()
	else
		self:startPlaying()		
	end
end

function FModPreview:stopPlaying()
	if self.playingEvent then
		_stat( 'stop playing preview' )
		self.playingEvent:stop()
		self.playingEvent = false
	end
end

function FModPreview:startPlaying()
	_stat( 'playing preview' )
	self.playingEvent = self.soundSource:playEvent2D( self.target:getFullName() )
end


function FModPreview:onMouseUp( btn )
	if btn == 'left' then
		self:togglePlaying()
	end
end

-- function FModPreview:onMouseMove( x, y )
-- 	if self.dragging then
-- 		local x0, y0 = unpack( self.dragFrom )
-- 		local dx, dy = x - x0, y - y0
-- 		scn.camera:setLoc( dx, -dy )
-- 		updateCanvas()
-- 	end
-- end


preview = scn:addEntity( FModPreview() )
