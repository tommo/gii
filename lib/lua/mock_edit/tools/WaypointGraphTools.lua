module 'mock_edit'

--------------------------------------------------------------------
CLASS: WapypointGraphToolCommon ( mock_edit.CanvasTool )

function WapypointGraphToolCommon:onLoad()
	WapypointGraphToolCommon.__super.onLoad( self )
	self.currentGraph = false
	self:updateSelection()
end

function WapypointGraphToolCommon:onSelectionChanged( selection )
	self:updateSelection()
end

function WapypointGraphToolCommon:updateSelection()
	self.currentGraph = false
	local selection = self:getSelection()
	for i, e in ipairs( selection ) do
		if isInstance( e, mock.Entity ) then 
			local g = e:getComponent( mock.WaypointGraph )
			if g then
				self.currentGraph = g
				return
			end
		end
	end

end

function WapypointGraphToolCommon:wndToGraph( x, y )
	x, y = self:wndToWorld( x, y )
	x, y = self.currentGraph:getEntity():worldToModel( x, y )
	return x, y 
end


--------------------------------------------------------------------
CLASS: WapypointGraphToolMain ( WapypointGraphToolCommon )

function WapypointGraphToolMain:onMouseDown( btn, x, y )
	if not self.currentGraph then return end

	if btn == 'left' then
		x, y = self:wndToGraph( x, y )
		if self:getInputDevice():isCtrlDown() then
			--add
			local p = self.currentGraph:addWaypoint()
			p:setLoc( x, y )
			self.currentWaypoint = p
			self.currentWaypoint.selected = true
			self.currentWaypointDragOffset = { 0, 0 }

		else
			--find waypoint
			local p = self.currentGraph:findWaypointByLoc( x, y, 20 )		
			if not p then return end

			if self:getInputDevice():isAltDown() then
				self.currentGraph:removeWaypoint( p )
			else
				self.currentWaypoint = p
				self.currentWaypoint.selected =true
				local px, py = p:getLoc()
				local dx, dy = px - x, py - y
				self.currentWaypointDragOffset = { dx, dy }
			end
			self:updateCanvas()	
		end

	end

end

function WapypointGraphToolMain:onMouseMove( x, y )
	if self.currentWaypoint then
		x, y = self:wndToGraph( x, y )
		local ox, oy = unpack( self.currentWaypointDragOffset )
		self.currentWaypoint:setLoc( x + ox, y + oy )
		self:updateCanvas()	
	end
end

function WapypointGraphToolMain:onMouseUp( btn, x, y )
	
	if btn == 'left' then
		if self.currentWaypoint then
			self.currentWaypoint.selected = false
			self.currentWaypoint = false
			self:updateCanvas()	
		end
	end

end


--------------------------------------------------------------------
CLASS: WapypointGraphToolLink ( WapypointGraphToolCommon )

function WapypointGraphToolLink:__init()
	self.tmpWaypoint = mock.Waypoint()
	self.connectionType = 'forcelink'
	self.action = 'add'
end

function WapypointGraphToolLink:onMouseDown( btn, x, y )
	if not self.currentGraph then return end

	if btn == 'left' then
		if self:getInputDevice():isAltDown() then
			self.action = 'delete'
		else
			self.action = 'add'
		end
		x, y = self:wndToGraph( x, y )
		local p = self.currentGraph:findWaypointByLoc( x, y, 20 )
		if not p then return end
		self.tmpWaypoint:setLoc( x, y )
		self.startWaypoint = p
		self.currentGraph:_addTmpConnection( self.tmpWaypoint, p, self.connectionType )
		self:updateCanvas()
	end

end

function WapypointGraphToolLink:onMouseMove( x, y )
	if self.startWaypoint then
		self.tmpWaypoint:setLoc( self:wndToGraph( x, y ) )
		self:updateCanvas()
	end
end

function WapypointGraphToolLink:onMouseUp( btn, x, y )
	if self.startWaypoint then
		x, y = self:wndToGraph( x, y )
		local p = self.currentGraph:findWaypointByLoc( x, y, 20 )
		if p then
			if self.action == 'delete' then
				self.startWaypoint:removeNeighbour( p )
			else
				self.startWaypoint:addNeighbour( p, self.connectionType )
			end
		end
		self.currentGraph:_clearTmpConnections()
		self:updateCanvas()
	end
end

--------------------------------------------------------------------
CLASS: WapypointGraphToolForceLink ( WapypointGraphToolLink )

function WapypointGraphToolForceLink:__init()
	self.connectionType = 'forcelink'
end


--------------------------------------------------------------------
CLASS: WapypointGraphToolNoLink ( WapypointGraphToolLink )

function WapypointGraphToolNoLink:__init()
	self.connectionType = 'nolink'
end


--------------------------------------------------------------------
registerCanvasTool( 'waypoint_tool',      WapypointGraphToolMain )
registerCanvasTool( 'waypoint_forcelink', WapypointGraphToolForceLink )
registerCanvasTool( 'waypoint_nolink',    WapypointGraphToolNoLink )
