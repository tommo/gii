module 'mock_edit'

CLASS: Gizmo ( EditorEntity )
	:MODEL{}

function Gizmo:enableConstantSize()
	local view = self.parent.parent
	local cameraListenerNode = MOAIScriptNode.new()
	cameraListenerNode:setCallback( function() self:updateConstantSize() end )
	local cameraCom = view:getCameraComponent()
	cameraListenerNode:setNodeLink( cameraCom.zoomControlNode )
	if cameraCom:isPerspective() then
		cameraListenerNode:setNodeLink( cameraCom:getMoaiCamera() )
	end
end

function Gizmo:updateConstantSize()
	local view = self.parent.parent
	local cameraCom = view:getCameraComponent()
	local factorZoom = 1/cameraCom:getZoom()
	local factorDistance = 1
	if cameraCom:isPerspective() then
		--TODO
	end
	local scl = factorZoom * factorDistance
	self:setScl( scl, scl, scl )
	self:forceUpdate()
end

function Gizmo:setTarget( object )
end

function Gizmo:setTransform( transform )
	inheritTransform( self._prop, transform )
end

function Gizmo:updateCanvas()
	self.parent:updateCanvas()
end

function Gizmo:onDestroy()
end

--------------------------------------------------------------------
CLASS: GizmoManager ( SceneEventListener )
	:MODEL{}

function GizmoManager:__init()
	self.normalGizmoMap   = {}
	self.selectedGizmoMap = {}
end

function GizmoManager:onLoad()
	self:scanScene()
end

function GizmoManager:_attachChildEntity( child )
	linkVisible( self:getProp(), child:getProp() )
end

function GizmoManager:onSelectionChanged( selection )
	--clear selection gizmos
	for ent, giz in pairs( self.selectedGizmoMap ) do
		giz:destroyWithChildrenNow()
	end
	self.selectedGizmoMap = {}
	local entities = {}
	for i, e in ipairs( selection ) do
		if isInstance( e, mock.Entity ) then
			self:buildForEntity( e, true )
		end
	end
end

function GizmoManager:onEntityEvent( ev, entity, com )
	if ev == 'clear' then
		self:clear()
		return
	end

	if entity.FLAG_EDITOR_OBJECT then return end

	if ev == 'add' then
		self:buildForObject( entity )
	elseif ev == 'remove' then
		self:removeForObject( entity )
	elseif ev == 'attach' then
		self:buildForObject( com )
	elseif ev == 'detach' then
		self:removeForObject( com )
	end

end

function GizmoManager:scanScene()
	for e in pairs( self.scene.entities ) do
		self:buildForEntity( e, false )
	end
end

function GizmoManager:buildForEntity( ent, selected )
	if ent.components then
		if not ( ent.FLAG_INTERNAL or ent.FLAG_EDITOR_OBJECT ) then
			self:buildForObject( ent, selected )
			for c in pairs( ent.components ) do
				if not ( c.FLAG_EDITOR_OBJECT ) then
					self:buildForObject( c, selected )
				end
			end
		end
	end
end

function GizmoManager:buildForObject( obj, selected )
	local onBuildGizmo
	if selected then 
		onBuildGizmo = obj.onBuildSelectedGizmo
	else
		onBuildGizmo = obj.onBuildGizmo
	end
	if onBuildGizmo then
		local giz = onBuildGizmo( obj )
		if giz then
			if selected then
				self.selectedGizmoMap[ obj ] = giz
			else
				self.normalGizmoMap[ obj ] = giz
			end
			self:addChild( giz )
			if obj:isInstance( mock.Entity ) then
				inheritVisible( giz:getProp(), obj:getProp() )
			elseif obj._entity then
				inheritVisible( giz:getProp(), obj._entity:getProp() )
			end
			giz:setTarget( obj )
		end
	end
end

function GizmoManager:removeForObject( obj )
	local giz = self.normalGizmoMap[ obj ]
	if giz then
		giz:destroyWithChildrenNow()
		self.normalGizmoMap[ e ] = nil
	end
end

function GizmoManager:clear()
	self:clearChildrenNow()
	self.normalGizmoMap   = {}
	self.selectedGizmoMap = {}
end


function GizmoManager:pickPoint( x,y )
	--TODO
end

function GizmoManager:pickRect( x,y, x1, y1  )
	--TODO
end