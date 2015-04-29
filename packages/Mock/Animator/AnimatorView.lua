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
	self.targetAnimatorData       = mock.AnimatorData()
	self.currentTrack     = false 
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
	--TODO: real target data
	return self.targetAnimatorData
end

function AnimatorView:setTargetAnimator( targetAnimator )
	self.targetAnimator = targetAnimator
	self.targetRootEntity = targetAnimator and targetAnimator._entity	
	self.targetClip = false
	self.currentTrack = false
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
	--affirm track
	local parent = self:findParentTrackGroup()
	if not parent then return end
	local track = mock.AnimatorTrackField()	
	parent:addChild( track )
	track:initFromObject( target, fieldId, self.targetRootEntity )
	local key = track:addKey()
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
end

function AnimatorView:updateKeyCurveMode( key, mode )
end

function AnimatorView:updateKeyCurvate( key, c1, c2 )
end


view = AnimatorView()
