module 'mock_edit'

--------------------------------------------------------------------
local currentSceneView = false

function getCurrentSceneView()
	return currentSceneView
end


--------------------------------------------------------------------
CLASS:SceneView ( CanvasView )

function SceneView:onInit()
	self:connect( 'scene.pre_serialize',    'preSceneSerialize'    )
	self:connect( 'scene.post_deserialize',  'postSceneDeserialize' )
	self:readConfig()
	self.gizmoManager:updateConstantSize()
	self.itemManager:updateAllItemScale()
end

function SceneView:readConfig()
	local cfg = self.scene:getMetaData( 'scene_view' )
	if not cfg then return end
	local cameraCfg = cfg['camera']
	if cameraCfg then
		self.camera:setLoc( unpack(cameraCfg['loc']) )
		self.navi.zoom = cameraCfg['zoom']
		local cameraCom = self.camera:getComponent( mock_edit.EditorCanvasCamera )
		cameraCom:setZoom( cameraCfg['zoom'] )
	end
end

function SceneView:focusSelection()
	local selection = gii.getSelection( 'scene' )
	for _, e in ipairs( selection ) do
		if isInstance( e, mock.Entity ) then
			self.camera:setLoc( e:getWorldLoc() )
		end
	end
	--todo: fit viewport to entity bound/ multiple selection
	self:updateCanvas()
end

function SceneView:preSceneSerialize( scene )
	if scene ~= self.scene then return end
	local cam = self.camera
	self.scene:setMetaData(
		'scene_view',
		{
			camera = {
				loc = { cam:getLoc() },
				zoom = cam:getComponent( mock_edit.EditorCanvasCamera ):getZoom(),
			}
		}
	)
end

function SceneView:postSceneDeserialize( scene )
	if scene ~= self.scene then return end
	self.gizmoManager:refresh()
end

function SceneView:makeCurrent()
	currentSceneView = self
end

function SceneView:onDestroy()
	if currentSceneView == self then
		currentSceneView = false
	end
end



--------------------------------------------------------------------
CLASS: SceneViewFactory ()
function SceneViewFactory:__init()
	self.priority = 0
end

function SceneViewFactory:createSceneView( scene, env )
	local view = SceneView( env )
	return view
end

--------------------------------------------------------------------
local function prioritySortFunc( a, b )
	return  a._priority < b._priority
end

local SceneViewFactories = {}
function registerSceneViewFactory( key, factory, priority )
	SceneViewFactories[key] = factory
end

function createSceneView( scene, env )
	local factoryList = {}
	for k, f in pairs( SceneViewFactories ) do
		table.insert( factoryList, f )
	end
	table.sort( factoryList, prioritySortFunc )

	for i, factory in pairs( factoryList ) do
		local view = factory:createSceneView( scene, env )
		if view then
			view:setName( '__EDITOR_SCENE_VIEW')
			return view
		end
	end
	
	--fallback
	return SceneView( env )
end
