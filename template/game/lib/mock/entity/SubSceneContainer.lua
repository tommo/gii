module 'mock'

CLASS: FakeScene ()
	:MODEL{}

function FakeScene:__init( rootEntity )
	self.root = rootEntity
end

function FakeScene:init()
end

function FakeScene:addEntity( ent )
	self.root:addChild( ent )
end

--------------------------------------------------------------------
CLASS: SubSceneContainer ( mock.Entity )
	:MODEL{
		'----';
		Field 'scene' :asset( 'scene' ) :getset( 'ScenePath' );		
	}

registerEntity( 'SubSceneContainer', SubSceneContainer )

function SubSceneContainer:__init()
	self.scenePath   = false
	self.resetTransform = true
	self.resetLoc = true
	self.resetScl = false
	self.resetRot = false
	self.instance = false
end

function SubSceneContainer:refreshScene()
	if not self.loaded then return end	
	if self.instance then
		self.instance:destroyWithChildrenNow()
		self.instance = false
	end
	if self.scenePath then
		self.instance = mock.Entity()
		self:addInternalChild( self.instance )
		local fakeScn = FakeScene( self.instance )
		loadAsset( self.scenePath, { scene = fakeScn } )
	end	
end

function SubSceneContainer:setScenePath( path )
	self.scenePath = path
	self:refreshScene()
end

function SubSceneContainer:getScenePath()
	return self.scenePath
end

function SubSceneContainer:onLoad()
	self.loaded = true
	self:refreshScene()
end

function SubSceneContainer:getInstance()
	return self.instance
end
