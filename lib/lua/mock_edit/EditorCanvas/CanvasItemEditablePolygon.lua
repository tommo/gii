module 'mock_edit'

--------------------------------------------------------------------
CLASS: CanvasItemEditablePolygon ( mock_edit.EditorEntity )
	:MODEL{}
function CanvasItemEditablePolygon:__init()
	self.vertexList = {}
	self.triangles  = false
	self.closed = false
	self:attach( mock.DrawScript{ priority = 500 } )
end

function CanvasItemEditablePolygon:onLoad()
end

function CanvasItemEditablePolygon:addVertex( x, y, index )
	local v = self:addChild( VertexHandle() )
	v:setLoc( x, y )
	if index then
		table.insert( self.vertexList, index, v )
	else
		table.insert( self.vertexList, v )
	end
	v:forceUpdate()
	self:triangulate()
	updateCanvas()
	return v
end

function CanvasItemEditablePolygon:closePolygon()
	if #self.vertexList < 3 then return false end
	self.closed = true
	self:triangulate()
	return true
end

function CanvasItemEditablePolygon:triangulate()
	if not self.closed then return end
	local coords = self:getVertexCoords()
	local verts = triangulateCanvasItemEditablePolygon( gii.tableToList( coords ) )
	verts = gii.listToTable( verts )
	local triangles = {}
	for i = 1, #verts, 6 do
		local tri = {}
		for j = i, i + 6 do
			table.insert( tri, verts[ j ] )
		end
		table.insert( triangles, tri )
	end
	self.triangles = triangles
end

function CanvasItemEditablePolygon:findVertex( x, y )
	for i, v in ipairs( self.vertexList ) do
		if v:inside( x, y ) then
			return v
		end
	end
end

function CanvasItemEditablePolygon:removeVertex( v1 )
	for i, v in ipairs( self.vertexList ) do
		if v == v1 then 
			v:destroy()
			table.remove( self.vertexList, i )
			if #self.vertexList < 3 then 
				self.closed = false
				self.triangles = false
			else
				self:triangulate()
			end
			updateCanvas()
			return
		end
	end
end

function CanvasItemEditablePolygon:tryInsertVertex( x, y )
	local count = #self.vertexList
	for i, v1 in ipairs( self.vertexList ) do
		local v2 = self.vertexList[ i == 1 and count or i - 1 ]
		local x1,y1 =v1:getLoc()
		local x2,y2 =v2:getLoc()
		local px,py = projectPointToLine( x1,y1, x2,y2, x,y )
		local dst = distance( px,py, x,y )
		if dst < 10 then
			local newVertex = self:addVertex( px, py, i == 1 and count + 1 or i )
			return newVertex
		end
	end
end

function CanvasItemEditablePolygon:getVertexCoords( loop )
	local verts = {}
	for i, v in ipairs( self.vertexList ) do
		local x, y = v:getLoc()
		table.insert( verts, x )
		table.insert( verts, y )
	end
	if loop and self.closed then
		table.insert( verts, verts[1] )
		table.insert( verts, verts[2] )
	end
	return verts
end


function CanvasItemEditablePolygon:onDraw()
	local triangles = self.triangles
	if triangles then
		MOAIGfxDevice.setPenWidth( 1 )
		MOAIGfxDevice.setPenColor( 0,0,1,0.4 )
		for i,tri in ipairs( self.triangles ) do
			MOAIDraw.fillFan( unpack( tri ) )
		end
		-- MOAIGfxDevice.setPenColor( 0,0,1,0.2 )
		-- for i,tri in ipairs( self.triangles ) do
		-- 	MOAIDraw.drawLine( tri )
		-- end
	end
	MOAIGfxDevice.setPenColor( 1,0,1,1 )
	MOAIGfxDevice.setPenWidth( 2 )
	local verts = self:getVertexCoords( true )
	MOAIDraw.drawLine( verts )

	MOAIGfxDevice.setPenWidth( 1 )
end

--------------------------------------------------------------------
CLASS: CanvasItemEditablePolygonEditor( mock_edit.EditorEntity )
function CanvasItemEditablePolygonEditor:onLoad()
	self.polygons = {}
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self.previewDeck    = false
	self.currentPolygon = false
	self.currentVertex  = false
	self.dragging       = false
	self.bounds         = {0,0,100,100}
end

function CanvasItemEditablePolygonEditor:addCanvasItemEditablePolygon()
	local p = self:addChild( CanvasItemEditablePolygon() )
	return p
end

function CanvasItemEditablePolygonEditor:pickCanvasItemEditablePolygon( x, y )
end

function CanvasItemEditablePolygonEditor:onMouseDown( btn, x, y )
	if not self.enabled then return end
	if btn == 'left' then
		x, y = self:wndToWorld( x, y )
		
		if not self.currentPolygon then
			self.currentPolygon = self:addCanvasItemEditablePolygon()			
		end	
		
		if self.currentVertex then
			if self.currentVertex == self.currentPolygon.vertexList[1] then 
				self.currentPolygon:closePolygon()
				self:updateDeck()
				updateCanvas()
			end
		else
			x, y = self.currentPolygon:worldToModel( x, y )

			if not self.currentPolygon.closed then
				if not self:inside( x, y ) then return end
				local v = self.currentPolygon:addVertex( x, y )
				self:setCurrentVertex( v )
				self:updateDeck()
			else --try insert
				local v = self.currentPolygon:tryInsertVertex( x, y )
				if v then self:setCurrentVertex( v ) end
				self:updateDeck()
			end
		end
		self.dragging = self.currentVertex ~= false
	end
end

function CanvasItemEditablePolygonEditor:onKeyDown( key )
	if self.dragging then return end
	if key == 'delete' and self.currentVertex then
		self.currentPolygon:removeVertex( self.currentVertex )
		self:setCurrentVertex( false )
		self:updateDeck()
	end
end


function CanvasItemEditablePolygonEditor:setCurrentVertex( v )
	v = v or false
	if self.currentVertex == v then return end
	if self.currentVertex then self.currentVertex.selected = false end
	self.currentVertex = v
	if v then v.selected = true end
	updateCanvas()
end

function CanvasItemEditablePolygonEditor:limitPos( x, y )
	local bounds = self.bounds
	x = clamp( x, bounds[1], bounds[3] )
	y = clamp( y, bounds[2], bounds[4] )
	return x, y
end

function CanvasItemEditablePolygonEditor:inside( x, y )
	local bounds = self.bounds
	return 
		between( x, bounds[1], bounds[3] ) and 
		between( y, bounds[2], bounds[4] )
end


function CanvasItemEditablePolygonEditor:onMouseMove( x, y )
	x, y = self:wndToWorld( x, y )
	if not self.dragging then 		
		local v = self:findVertex( x, y )
		self:setCurrentVertex( v )
	else
		x, y = self:limitPos( x, y )
		x, y = self.currentPolygon:worldToModel( x, y )
		self.currentVertex:setLoc( x, y )
		self.currentPolygon:triangulate()
		updateCanvas()
		self:updateDeck()
	end
end

function CanvasItemEditablePolygonEditor:onMouseUp( btn, x, y )
	if btn == 'left' then
		x, y = self:wndToWorld( x, y )
		self.dragging = false
		self:setCurrentVertex( self:findVertex( x, y ) )
	end
end

function CanvasItemEditablePolygonEditor:findVertex( x, y )
	return self.currentPolygon and self.currentPolygon:findVertex( x, y )
end

function CanvasItemEditablePolygonEditor:wndToWorld( x, y )
	return scn.cameraCom:wndToWorld( x, y )
end

function CanvasItemEditablePolygonEditor:setEnabled( e )
	self.enabled = e
	self:setVisible( e )
end

function CanvasItemEditablePolygonEditor:setDeck( deck )
	self.currentDeck = deck
	if deck then
		local previewDeck = mock.Quad2D()
		local tex = self.currentDeck:getTexture()
		previewDeck:setTexture( tex )
		self.previewDeck = previewDeck
		local bounds = { previewDeck:getRect() }	
		self.bounds = bounds
		--load triangles
		if self.currentPolygon then self.currentPolygon:destroy() end

		local poly = self:addCanvasItemEditablePolygon()
		self.currentPolygon = poly

		local polyline = deck.polyline
		if not polyline then
			local x,y,x1,y1 = unpack( bounds )
			polyline = {
				x, y,
				x1, y,
				x1, y1,
				x, y1,
			}
		end
		for i = 1, #polyline, 2 do
			local x, y = polyline[i], polyline[i+1]
			poly:addVertex( x, y )
		end
		poly:closePolygon()
	end

end

local insert = table.insert
function CanvasItemEditablePolygonEditor:updateDeck()
	local poly = self.currentPolygon

	self.currentDeck.polyline = poly:getVertexCoords()

	local triangles = poly.triangles
	if not triangles then return end

	local w, h = self.previewDeck:getSize()
	local verts = {}
	for i, tri in ipairs( triangles ) do
		for j = 1, 6, 2 do
			local x,y = tri[j], tri[j+1]
			insert( verts, x )
			insert( verts, y )
			local u,v = ( x + w/2 ) / w, ( y + h/2 ) / h
			insert( verts, u )
			insert( verts, v )
		end
	end
	self.currentDeck.vertexList = verts
	self.currentDeck:update()
end

function CanvasItemEditablePolygonEditor:getPreviewDeck()
	return self.previewDeck:getMoaiDeck()	
end

