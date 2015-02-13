
CLASS: TempoMusic ()
	:MODEL{
		Field 'music' :asset( 'fmod_event' );
		Field 'BPM' :meta{ step = 0.1 };
		Field 'slice' :int();
		Field 'offset' :meta{ step = 0.01 };
		Field 'accentOffset' :int();
		Field 'beatPoints': array( 'number' ) :no_edit();
		Field 'syncPoints': array( 'number' ) :no_edit();
		Field 'length'
	}

function TempoMusic:__init()
	self.music      = false
	self.BPM        = 120
	self.offset     = 0
	self.slice      = 4
	self.accentOffset = 0
	self.beatPoints = {}
	self.syncPoints = {}
	self.length     = 0
end

--------------------------------------------------------------------
local function loadTempoMusic( node )
	local data   = mock.loadAssetDataTable( node:getObjectFile('config') )
	local config = mock.deserialize( nil, data )	
	return config
end

mock.registerAssetLoader( 'tempo_music', loadTempoMusic )
