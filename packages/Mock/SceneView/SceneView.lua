require 'mock.env'
require 'mock_edit'

--------------------------------------------------------------------
CLASS:SceneView ( mock_edit.CanvasView )

function SceneView:onInit()
	self:connect( 'scene.serialize',    'preSceneSerialize'    )
	self:connect( 'scene.deserialize',  'postSceneDeserialize' )
	self:readConfig()
end

function SceneView:readConfig()
	local cfg = self.scene.metaData[ 'scene_view' ]
	if not cfg then return end
	local cameraCfg = cfg['camera']
	if cameraCfg then
		self.camera:setLoc( unpack(cameraCfg['loc']) )
		self.camera:getComponent( mock_edit.EditorCanvasCamera ):setZoom( cameraCfg['zoom'] )
		self.navi.zoom = cameraCfg['zoom']
	end
end

function SceneView:updateCanvas()
	return _giiSceneView:scheduleUpdate()
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
	self.scene.metaData [ 'scene_view' ] = {
		camera = {
			loc = { cam:getLoc() },
			zoom = cam:getComponent( mock_edit.EditorCanvasCamera ):getZoom(),
		}
	}
end

function SceneView:postSceneDeserialize( scene )
	if scene ~= self.scene then return end
	self.gizmoManager:refresh()
end

--------------------------------------------------------------------
view = false

function openScene( scene )
	-- local ctx = gii.getCurrentRenderContext()	
	-- local gameActionRoot = game:getActionRoot()
	-- gii.setCurrentRenderContextActionRoot( game:getActionRoot() )
	view = scene:addEntity( SceneView( _M ) )
end

function closeScene()
	view = false
end

--------------------------------------------------------------------
function onResize( w, h )
	if view then view:onCanvasResize( w, h ) end
end

