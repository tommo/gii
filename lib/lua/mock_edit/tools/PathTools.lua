module 'mock_edit'


--------------------------------------------------------------------
CLASS: PathToolCommon ( mock_edit.CanvasTool )

function PathToolCommon:onLoad()
	PathToolCommon.__super.onLoad( self )
	self.currentGraph = false
	self:updateSelection()
end

function PathToolCommon:onSelectionChanged( selection )
	self:updateSelection()
end

function PathToolCommon:updateSelection()
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

function PathToolCommon:wndToGraph( x, y )
	x, y = self:wndToWorld( x, y )
	x, y = self.currentGraph:getEntity():worldToModel( x, y )
	return x, y 
end



--------------------------------------------------------------------
CLASS: PathToolMain ( PathToolCommon )



--------------------------------------------------------------------
registerCanvasTool( 'path_tool',    PathToolMain )
