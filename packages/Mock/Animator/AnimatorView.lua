CLASS: AnimatorView ()
	:MODEL{}

function AnimatorView:loadTestData()
end


function setupTestData()
	testClip = mock.AnimatorClip()
	
	testGroup = mock.AnimatorTrackGroup()
	testGroup.name = 'group'

	testClip:getRoot():addChild( testGroup )
	testTrack = mock.AnimatorTrack()
	testTrack.name = 'track'
	for i = 1, 8 do
		local key = testTrack:addKey( rand( 0, 5 ) * 1000 )
	end
	testGroup:addChild( testTrack )
	testGroup1 = mock.AnimatorTrackGroup()
	testGroup1.name = 'group'
	testGroup:addChild( testGroup1 )
	testTrack = mock.AnimatorTrack()
	testTrack.name = 'track'
	testGroup1:addChild( testTrack )
	for i = 1, 8 do
		local key = testTrack:addKey( rand( 0, 5 ) * 1000 )
	end
	
	return testClip
end

function setEditTarget( target )
	editTarget = target
end
