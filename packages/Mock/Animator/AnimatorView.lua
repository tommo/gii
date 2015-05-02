local findTopLevelEntities       = mock_edit.findTopLevelEntities
local getTopLevelEntitySelection = mock_edit.getTopLevelEntitySelection
local isEditorEntity             = mock_edit.isEditorEntity

--------------------------------------------------------------------
CLASS: AnimatorView ()
	:MODEL{}

function AnimatorView:__init()
	self.targetAnimator   = false
	self.targetRootEntity = false
	self.targetClip       = false
	self.targetAnimatorData  = false
	self.currentTrack     = false 
	self.currentTime = 0
	self.previewTimeStep = 1/30
	self.prevClock = 0
	self.dirty = false
end

function AnimatorView:setupTestData()
	testClip = mock.AnimatorClip()
	
	testGroup = mock.AnimatorTrackGroup()
	testGroup.name = 'group'

	testClip:getRoot():addChild( testGroup )
	testTrack = mock.AnimatorTrack()
	testTrack.name = 'track'
	for i = 1, 8 do
		local key = testTrack:addKey( rand( 0, 5 ) )
	end
	testGroup:addChild( testTrack )
	testGroup1 = mock.AnimatorTrackGroup()
	testGroup1.name = 'group'
	testGroup:addChild( testGroup1 )
	testTrack = mock.AnimatorTrack()
	testTrack.name = 'track'
	testGroup1:addChild( testTrack )
	for i = 1, 8 do
		local key = testTrack:addKey( rand( 0, 5 ) )
	end
	
	return testClip
end

function AnimatorView:findTargetAnimator()
	local selection = gii.getSelection( 'scene' )
	--find a parent animator
	if #selection ~= 1 then --only single selection allowed( for now )
		return nil
	end

	local ent = selection[1]
	if not isInstance( ent, mock.Entity ) then
		return nil
	end

	while ent do
		local animator = ent:getComponent( mock.Animator )
		if animator then return animator end
		ent = ent.parent
	end

	return nil
end

function AnimatorView:getTargetAnimatorData()
	if not self.targetAnimator then return nil end
	return self.targetAnimatorData
end

function AnimatorView:setTargetAnimator( targetAnimator )
	self.targetAnimator = targetAnimator
	self.targetRootEntity = targetAnimator and targetAnimator._entity	
	self.targetClip = false
	self.currentTrack = false
	self.dirty = false
	--TODO: real target data
	if self.targetAnimator then
		self.targetAnimatorData = self.targetAnimator:getData()
	else
		self.targetAnimatorData = false
	end
end

function AnimatorView:getPreviousTargeClip( targetAnimator )
	local data = self:getTargetAnimatorData()
	if not data then return nil end
	return data.previousTargetClip
end

function AnimatorView:setTargetClip( targetClip )
	self.targetClip = targetClip
	self.currentTrack = false
end

function AnimatorView:setCurrentTrack( track )
	self.currentTrack = track
end

function AnimatorView:addClip()
	local clip = self.targetAnimatorData:addClip( 'New Clip' )
	return clip
end

function AnimatorView:removeClip( clip )
	self.targetAnimatorData:removeClip( clip )
	return true
end


function AnimatorView:addKeyForField( target, fieldId )
	--find existed track
	local track
	local trackList = self.targetClip:getTrackList()
	for _, t in ipairs( trackList ) do
		if t:isInstance( mock.AnimatorTrackField ) then
			if t:isMatched( target, fieldId, self.targetRootEntity ) then
				track = t
				break
			end
		end
	end

	if not track then
		local parent = self:findParentTrackGroup()
		if not parent then return end
		track = mock.AnimatorTrackField()	
		parent:addChild( track )
		track:initFromObject( target, fieldId, self.targetRootEntity )
	end

	local key = track:addKey()
	local value = track.targetField:getValue( target )
	key.value = value
	key.pos   = self.currentTime
	return key
end

function AnimatorView:addKeyForEvent( target, eventId )
end


function AnimatorView:removeKey( key )
	local track = key:getTrack()
	if track then track:removeKey( key ) end
end

function AnimatorView:findParentTrackGroup()
	if not self.targetClip then return nil end
	local parent = self.currentTrack 
	while parent do
		if parent:isInstance( mock.AnimatorTrackGroup ) then
			break
		end
		parent = parent.parent
	end
	parent = parent or self.targetClip:getRoot()
	return parent
end

function AnimatorView:addTrackGroup()
	local parent = self:findParentTrackGroup()
	if not parent then return end
	local group = mock.AnimatorTrackGroup()
	group.name = 'New Group'
	parent:addChild( group )
	return group
end


function AnimatorView:removeTrack( track )
	track.parent:removeChild( track )
	return true
end

function AnimatorView:updateTimelineKey( key, pos, length )
	key:setPos( pos )
	key:setLength( length )
	self:markTrackDirty()
end

function AnimatorView:updateKeyCurveMode( key, mode )
end

function AnimatorView:updateKeyCurvate( key, c1, c2 )
end

function AnimatorView:startPreview( t )
	self.prevClock = false
	return true
end

function AnimatorView:stopPreview()
	return true
end

function AnimatorView:gotoStart()
	return true
end

function AnimatorView:gotoEnd()
	return true
end

function AnimatorView:applyTime( t )
	if self.targetClip then
		if not self.previewState then self:preparePreivewState() end
		self.previewState:apply( t )
		self.currentTime = self.previewState:getTime()
	else
		self.currentTime = t
	end
	return self.currentTime
end

function AnimatorView:preparePreivewState()
	self.previewState = self.targetAnimator:_loadClip( self.targetClip )
	self.previewState:setMode( self.previewRepeat and MOAITimer.LOOP or MOAITimer.NORMAL )
	self.prevClock = false
	return true
end


function AnimatorView:doPreviewStep()
	local dt
	local clock = os.clock()
	if not self.prevClock then
		dt = 0
	else
		dt = clock - self.prevClock
	end
	self.prevClock = clock
	self:applyTime( self.currentTime + dt )
	return self.currentTime
end

function AnimatorView:markTrackDirty( track )
	--TODO: update track only
	self:markClipDirty()
	self.dirty = true
end

function AnimatorView:markClipDirty()
	self.targetClip:clearPrebuiltContext()
	self:clearPreviewState()
	self.dirty = true
end

function AnimatorView:renameClip( clip, name )
	clip.name = name
end

function AnimatorView:renameTrack( track, name )
	track.name = name
end

function AnimatorView:clearPreviewState()
	if self.previewState then
		self.previewState:stop()
	end
	self.previewState = false
end

function AnimatorView:togglePreviewRepeat( toggle )
	self.previewRepeat = toggle
	if self.previewState then
		self.previewState:setMode( self.previewRepeat and MOAITimer.LOOP or MOAITimer.NORMAL )
	end
end

function AnimatorView:saveData()
	if not self.dirty then return end
	if not( self.targetAnimator and self.targetAnimatorData ) then return end
	local dataPath = self.targetAnimator:getDataPath()
	assert( dataPath )
	local node = mock.getAssetNode( dataPath )
	mock.serializeToFile( self.targetAnimatorData, node:getObjectFile( 'data' )  )
	self.dirty = false
	return true
end

view = AnimatorView()
