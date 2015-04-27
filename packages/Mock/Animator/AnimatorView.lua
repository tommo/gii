CLASS: AnimatorView ()
	:MODEL{}

function AnimatorView:loadTestData()
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

function AnimatorView:setEditTarget( target )
	editTarget = target
end

function AnimatorView:removeKey( key )
	local track = key:getTrack()
	if track then track:removeKey( key ) end
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
