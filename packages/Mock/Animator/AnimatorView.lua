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

	self.retainedEntityState = false
	self.objectRecordingState = {}
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

function AnimatorView:getTargetAnimatorDataPath()
	if not self.targetAnimator then return nil end
	return self.targetAnimatorDataPath
end

function AnimatorView:setTargetAnimator( targetAnimator )
	self:restoreEntityState()
	self.retainedRecordingState = false
	
	self.targetAnimator = targetAnimator
	self.targetRootEntity = targetAnimator and targetAnimator._entity	
	self.targetClip = false
	self.currentTrack = false
	self.dirty = false

	if self.targetAnimator then
		self.targetAnimatorData = self.targetAnimator:getData()
		self.targetAnimatorDataPath = self.targetAnimator:getDataPath()
	else
		self.targetAnimatorData = false
		self.targetAnimatorDataPath = false
	end
	
	mock.setAnimatorEditorTarget( self.targetRootEntity )

end

function AnimatorView:getPreviousTargeClip( targetAnimator )
	local data = self:getTargetAnimatorData()
	if not data then return nil end
	return data.previousTargetClip
end

function AnimatorView:setTargetClip( targetClip )
	self:restoreEntityState()
	self.retainedRecordingState = false
	self.targetClip = targetClip
	self.currentTrack = false
	if self.targetClip then
		self:collectEntityRecordingState()
	end
end

function AnimatorView:setCurrentTrack( track )
	self.currentTrack = track
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

	--create track if not found
	if not track then
		local parent = self:findParentTrackGroup()
		if not parent then return end
		local model = Model.fromObject( target )
		local fieldType = model:getFieldType( target, fieldId )
		local trackClass = mock.getAnimatorTrackFieldClass( fieldType )
		if trackClass then
			track = trackClass()
		else
			_warn( 'field is not keyable', fieldType )
			return false
		end
		parent:addChild( track )
		track:setTargetObject( target, self.targetRootEntity )
		track:setFieldId( fieldId )
		track:init()
	end

	local keys = { 
		track:createKey( 
			self.currentTime,
			{
				target = target,
				root   = self.targetRootEntity
			}
		)
	}
	track:collectObjectRecordingState( self.targetAnimator, self.retainedRecordingState )
	self:markClipDirty()
	return keys
end

function AnimatorView:addKeyForEvent( target, eventId )
end

function AnimatorView:addKeyForSelectedTrack( track )
	local target = track:getTargetObject( self.targetRootEntity )
	local keys = {
		track:createKey(
			self.currentTime,
			{
				target = target,
				root   = self.targetRootEntity
			}
		)
	}
	track:collectObjectRecordingState( self.targetAnimator, self.retainedRecordingState )
	self:markClipDirty()
	return keys
end

function AnimatorView:addCustomAnimatorTrack( target, trackClasId )
	local parent = self:findParentTrackGroup()
	if not parent then return end
	local classes = mock.getCustomAnimatorTrackTypesForObject( target )
	local clas = classes[ trackClasId ]
	local track = clas()
	parent:addChild( track )
	track:setTargetObject( target, self.targetRootEntity )
	track:init()
	track:collectObjectRecordingState( self.targetAnimator, self.retainedRecordingState )
	self:markClipDirty()
	return track
end

function AnimatorView:removeKey( key )
	local track = key:getTrack()
	assert( track )
	track:removeKey( key )
	self:markTrackDirty( track )
	return true
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

function AnimatorView:updateTimelineKeyMode( key, mode )
	key:setTweenMode( mode )
	self:markTrackDirty()
end

function AnimatorView:updateTimelineKeyCurveValue( key, value )
	key:setCurveValue( value )
	self:markTrackDirty()
end

function AnimatorView:updateTimelineKeyBezierPoint( key, bpx0, bpy0, bpx1, bpy1 )
	key:setBezierPoints( bpx0, bpy0, bpx1, bpy1 )
	self:markTrackDirty()
end

function AnimatorView:updateTimelineMarker( marker, pos )
	marker:setPos( pos )
	self:markTrackDirty()
end

function AnimatorView:updateKeyTweenMode( key, mode )
	key:setTweenMode( mode )
	self:markTrackDirty()
end

function AnimatorView:startPreview( t )
	self.prevClock = false
	if self.currentTime >= self.targetClip:getLength() then
		self:applyTime( 0 )
	end
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
	self.previewState = self.targetAnimator:_loadClip( self.targetClip, true )
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
	if self.currentTime >= self.targetClip:getLength() then
		--preview stop
		if not self.previewRepeat then
			return false, self.currentTime
		end
	end
	return true, self.currentTime
end


function AnimatorView:markObjectFieldRecording( obj, fieldId )
	local state = self.objectRecordingState[ obj ]
	if not state then
		state = {}
		self.objectRecordingState[ obj ] = state
	end
	local model = Model.fromObject( obj )
	state[ fieldId ] = { model:getFieldValue( fieldId ) }
end

function AnimatorView:collectEntityRecordingState()
	if not self.targetAnimator then return end
	local clip   = self.targetClip
	local retainedState = clip:collectObjectRecordingState( self.targetAnimator )
	self.retainedRecordingState = retainedState
end

function AnimatorView:restoreEntityState()
	if not self.retainedRecordingState then return end
	self.retainedRecordingState:applyRetainedState()
end

function AnimatorView:markTrackDirty( track )
	--TODO: update track only
	self:markClipDirty()
end

function AnimatorView:markClipDirty()
	self.targetClip:clearPrebuiltContext()
	self:clearPreviewState()
	self:markDataDirty()
end

function AnimatorView:markDataDirty()
	self.dirty = true
end

function AnimatorView:renameClip( clip, name )
	clip.name = name
end

function AnimatorView:renameTrack( track, name )
	track.name = name
end

function AnimatorView:cloneKey( key )
	--todo
end

function AnimatorView:cloneTrack( track )
	--todo
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
	
	if self.targetAnimator:isInstance( mock.EmbedAnimator ) then return true end
	
	local dataPath = self.targetAnimator:getDataPath()
	--FIXME: animator data path might get removed
	assert( dataPath )

	local node = mock.getAssetNode( dataPath )
	mock.serializeToFile( self.targetAnimatorData, node:getObjectFile( 'data' )  )
	self.dirty = false
	return true
end


view = AnimatorView()
