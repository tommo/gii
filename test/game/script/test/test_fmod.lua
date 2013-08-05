function OnTestStart()
	 -- MOAIFmodEx.init()
	assert(
		MOAIFmodEventMgr.init{
		["soundMemoryMB"]              =  32 ;
		["rsxMemoryMB"]                =  0 ;
		["voiceLRUBufferMB"]           =  0 ;
		["voiceLRUMaxMB"]              =  0 ;
		["nVirtualChannels"]           =  256 ;
		["nRealChannels"]              =  32 ;
		["nPCMCodecs"]                 =  16 ;
		["nADPCMCodecs"]               =  32 ;
		["nCompressedCodecs"]          =  32 ;
		["nMaxInputChannels"]          =  6 ;
		["enableSoundSystem"]          =  true ;
		["enableDistantLowpass"]       =  false ;
		["enableEnvironmentalReverb"]  =  true ;
		["enableNear2DBlend"]          =  false ;
		["enableAuditioning"]          =  true ;
		["enableProfiling"]            =  true ;
		["enableFsCallbacks"]          =  false ;
		["disableSound"]               =  false ;
		["dopplerScale"]               =  0 ;
	}
		, 'fmod designer not loaded' )

	local sampleName = 'examples/FeatureDemonstration/Basics/BasicEvent'
	local sampleName2 = 'examples/FeatureDemonstration/Basics/SimpleEvent'
	local sampleName3 = 'examples/FeatureDemonstration/Basics/Oneshot Event'
	local sampleName4 = 'examples/AdvancedTechniques/Car'
	assert( MOAIFmodEventMgr.loadProject( '../media/examples.fev' ), 'project not loaded' )
	-- print(MOAIFmodEventMgr.getMemoryStats())
	MOAIFmodEventMgr.loadGroup( 'examples/FeatureDemonstration', true, true  )
	MOAIFmodEventMgr.loadGroup( 'examples/New 2011', true, true  )
	MOAIFmodEventMgr.loadGroup( 'examples/AdvancedTechniques', true, true  )
	-- print()
	local evt = MOAIFmodEventMgr.playEvent2D( sampleName, true )
	assert(evt)
	print(MOAIFmodEventMgr.getMemoryStats())
	print('duration', MOAIFmodEventMgr.getEventDuration(  sampleName ))
	print('valid', evt:isValid() )
	print('name', evt:getName() )
	print('chan', evt:getNumChannels() )
	print('tempo', evt:getTempo() )
	print('freq', evt:getDominantFrequency() )
	print('vol', evt:getVolume() )

	MOAIFmodEventMgr.playEvent2D( sampleName2, true )
	print()
	MOAIFmodEventMgr.playEvent2D( sampleName3, true )
	print()
	local evt = MOAIFmodEventMgr.playEvent2D( sampleName4, true )
	evt:setParameter( 'rpm', 5000 )
	evt:setParameter( 'load', .5 )
	-- evt:keyOff('CyclePoint')
	print()


	-- print(MOAIFmodEx.getMemoryStats())

	-- local sound = MOAIFmodExSound.new()
	-- sound:load('data/BonusPing.wav')

	-- local chan = MOAIFmodExChannel.new()
	-- chan:play( sound )

end
