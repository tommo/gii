module 'mock'

--[[
	FMOD Designer Only
]]

function initFmodDesigner()
	if not MOAIFmodEventMgr then return end
	--TODO: accept config from startup script
	local MOAIFmodEventMgrReady = MOAIFmodEventMgr.init{
			["soundMemoryMB"]              =  16 ;
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
			["enableDistantLowpass"]       =  true ;
			["enableEnvironmentalReverb"]  =  true ;
			["enableNear2DBlend"]          =  true ;
			["enableAuditioning"]          =  false ;
			["enableProfiling"]            =  false ;
			["enableFsCallbacks"]          =  false ;
			["disableSound"]               =  false ;
			["dopplerScale"]               =  0 ;
		}

	if not MOAIFmodEventMgrReady then
		--TODO:LOG alert?
		_error('Fmod not initialized...')
	else
		_stat('Fmod ready...')
	end

end
-- function loadFmodProject( path )
-- 	MOAIFmodEventMgr.loadProject( path )
-- end

-- function loadFmodProject( path )
-- 	MOAIFmodEventMgr.loadProject( path )
-- end