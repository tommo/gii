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
	testGroup:addChild( testTrack )
	for i = 1, 20 do
		testTrack2 = mock.AnimatorTrack()
		testTrack2.name = 'track-2'
		testClip:getRoot():addChild( testTrack2 )
	end
	return testClip
end

function setEditTarget( target )
	editTarget = target
end
