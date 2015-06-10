--------------------------------------------------------------------
scn = mock_edit.createEditorCanvasScene()
--------------------------------------------------------------------

mock_edit.addColor( 'tilemap_grid', hexcolor( '#00ffea', 0.5 ) )


--------------------------------------------------------------------
CLASS: NamedTilesetLayout ( mock_edit.EditorEntity )
	:MODEL{}

function NamedTilesetLayout:onLoad()
	self.tileProps = {}
	self.target = false
	self.selectedTile = false
	self.selectedTileId = false

end

function NamedTilesetLayout:setTarget( tileset )
	self.target = tileset
	local count = tileset:getTileCount()
	local deck = tileset:getMoaiDeck()
	local bx0 = 1000000
	local by0 = 1000000
	local bx1 = -1000000
	local by1 = -1000000
	for id = 1, count do
		local name = tileset.idToName[ id ]
		local data = tileset.nameToTile[ name ]
		local x0,y0,x1,y1 = unpack( data['raw_rect'])
		local ox,oy = unpack( data['deck_offset'])
		local index = data['raw_index']
		local prop = MOAIProp.new()
		self:_attachProp( prop )
		local prop2 = MOAIProp.new()
		self:_attachProp( prop2 )
		
		local x, y = x0 - ox, -y1 - oy
		bx0 = math.min( x, bx0 )
		bx1 = math.max( x, bx1 )
		by0 = math.min( y, by0 )
		by1 = math.max( y, by1 )
		prop:setLoc( x, y, index*0.01 )
		prop:setColor( 1,1,1, 1 )
		prop:setDeck( deck )
		prop:setIndex( id )
		prop2:setLoc( x, y, index*0.01 + 0.1 )
		prop2:setColor( 0.5,0.5,1, 1 )
		-- prop2:setDeck( deck )
		local xx0,yy0,zz0, xx1,yy1,zz1 = prop:getBounds()
		local boundDeck = MOAIScriptDeck.new()
		boundDeck:setDrawCallback(function()
			MOAIGfxDevice.setPenColor( 0.5,0.5,1, 0.2 )
			MOAIDraw.fillRect( xx0,yy0, xx1,yy1  )
			MOAIGfxDevice.setPenColor( 0.5,0.5,1, 1 )
			MOAIDraw.drawRect( xx0,yy0, xx1,yy1  )
		end)
		prop2:setDeck( boundDeck )
		prop2:setBounds( prop:getBounds() )
		prop2.deck = boundDeck
		prop2:setIndex( id )
		prop2:setVisible( false )
		setPropBlend( prop2, 'alpha' )
		prop.selectionProp = prop2

		self.tileProps[ id ] = prop
	end
	self:setLoc( -(bx0+bx1)/2, -(by0+by1)/2 )
end

function NamedTilesetLayout:selectTile( name )
	if self.selectedTileId then
		local prevProp = self.tileProps[ self.selectedTileId ]
		-- prevProp:setColor( 1,1,1, 1 )
		prevProp.selectionProp:setVisible( false )
	end

	if name then
		local id = self.target.nameToId[ name ]
		local prop = self.tileProps[ id ]
		self.selectedTile = name
		self.selectedTileId = id
		-- prop:setColor( 1, .7, .7, 1 )
		prop.selectionProp:setVisible( true )
	else
		self.selectedTile = false
		self.selectedTileId = false
	end

end

function NamedTilesetLayout:pickTile( x, y )
	if not self.target then return nil end
	local found = false
	for i, prop in pairs( self.tileProps ) do
		local _,_,z1 = prop:getWorldLoc()
		if prop:inside( x, y, z1 ) then
			found = i
			break
		end
	end
	return self.target.idToName[ found ], found
end

function NamedTilesetLayout:onDestroy()
	for i, p in ipairs( self.tileProps ) do
		self:_detachProp( p.selectionProp )
		self:_detachProp( p )
	end
end

--------------------------------------------------------------------
CLASS: TilesetViewer ( mock_edit.EditorEntity )
	:MODEL{}

function TilesetViewer:__init()
	self.targetTilesetPath = false
	self.targetTileset = false
	self.currentLayout = false
	self.selectedTile = false
end

function TilesetViewer:onLoad()
	self.navigate = self:addChild( mock_edit.CanvasNavigate() )
	local inputDevice = self:getScene().inputDevice
	self:attach( mock.InputScript{ 
			device = inputDevice
		} )
end

function TilesetViewer:onMouseDown( btn, x,y )
	if btn ~= 'left' then return end
	if not self.currentLayout then return end
	local wx, wy = self:wndToWorld( x, y )
	local name = self.currentLayout:pickTile( wx, wy )
	if name then
		self.currentLayout:selectTile( name )
	end
	if mock_edit.getCurrentSceneView():getActiveToolId() ~= 'tilemap.fill' then
		self.parentEditor:changeEditTool( 'pen' )
	end
	self.parentEditor:selectTileBrush( name )
	self.navigate:updateCanvas()
end

function TilesetViewer:setTargetTileset( tilesetPath )
	if self.targetTilesetPath == tilesetPath then return end
	self.targetTilesetPath = tilesetPath
	self.targetTileset = tilesetPath and mock.loadAsset( tilesetPath )

	self.parentEditor:selectTileBrush( false )
	if self.currentLayout then
		self.currentLayout:destroyAllNow()
		self.currentLayout = false
	end
	if not self.targetTileset then return self:hide() end
	self:show()

	--build tile layout
	if self.targetTileset:isInstance( mock.NamedTileset ) then
		self.currentLayout = self:addChild( NamedTilesetLayout() )
		self.currentLayout:setTarget( self.targetTileset )
	else
		--TODO
	end
end

function TilesetViewer:fitViewport( w, h )
end

function TilesetViewer:clearSelection()
	if self.currentLayout then self.currentLayout:selectTile( false ) end
	self.parentEditor:selectTileBrush( false )
	self.navigate:updateCanvas()
end

--------------------------------------------------------------------
CLASS: TileMapGridLines ( mock_edit.EditorEntity )
	:MODEL{}

function TileMapGridLines:__init()
	self.targetLayer = false
end

function TileMapGridLines:onLoad()
	self:attach( mock.DrawScript() ):setBlend( 'alpha' )
end

function TileMapGridLines:onDraw()
	if not self.targetLayer then return end
	mock_edit.applyColor( 'tilemap_grid' )
	self.targetLayer:onDrawGridLine()
end

function TileMapGridLines:setTarget( targetLayer )
	self.targetLayer = targetLayer
end

--------------------------------------------------------------------
CLASS: TileMapEditor( mock_edit.EditorEntity )

function TileMapEditor:__init()
	self.currentTerrainBrush = false
	self.currentTileBrush    = false
	self.randomEnabled       = false
end

function TileMapEditor:onLoad()
	self.tilesetViewer = self:addSibling( TilesetViewer() )
	self.tilesetViewer.parentEditor = self
	self.gridLine = false
end

function TileMapEditor:findTargetTileMap()
	local selection = gii.getSelection( 'scene' )
	--find a parent animator
	if #selection ~= 1 then --only single selection allowed( for now )
		return nil
	end

	local ent = selection[1]
	if not isInstance( ent, mock.Entity ) then
		return nil
	end

	while ent do
		local map = ent:getComponent( mock.TileMap )
		if map then return map end
		ent = ent.parent
	end

	return nil
end

function TileMapEditor:setTargetTileMap( m )
	self.targetTileMap = m
end

function TileMapEditor:setTargetTileMapLayer( l )
	if self.gridLine then
		self.gridLine:destroyAllNow()
		self.gridLine = false
	end

	self.targetTileMapLayer  = l
	self.currentTileBrush    = false
	-- self.currentTileBrush    = 'WallBrick.s'
	self.currentTerrainBrush = false
	if self.targetTileMapLayer then
		self.tilesetViewer:setTargetTileset( self.targetTileMapLayer:getTilesetPath() )
		self.gridLine = self.targetTileMap._entity:addChild( TileMapGridLines() )
		self.gridLine:setTarget( self.targetTileMapLayer )
	else
		self.tilesetViewer:setTargetTileset( false )
	end
end

function TileMapEditor:getTargetTileMapLayer()
	return self.targetTileMapLayer
end

function TileMapEditor:getTargetTileMap()
	return self.targetTileMap
end

function TileMapEditor:wndToCoord( x, y )
	local sceneView = mock_edit.getCurrentSceneView()
	x, y = sceneView:wndToWorld( x, y )
	layer = self.targetTileMapLayer
	local lx, ly = layer:worldToModel( x, y )
	local tx, ty = layer:locToCoord( lx, ly ) 
	return tx, ty
end

function TileMapEditor:requestAvailTileMapLayerTypes()
	if not self.targetTileMap then return {} end
	return self.targetTileMap:getAvailTileMapLayerTypes()
end

function TileMapEditor:createTileMapLayer( tileset )
	local layer = self.targetTileMap:_createLayer( tileset )
	if not layer then
		mock_edit.alertMessage( 'message', 'unsupported Tileset type', 'info' )
		return false
	end
	return layer
end

function TileMapEditor:removeTileMapLayer()
	if not self.targetTileMapLayer then return end
	self.targetTileMap:removeLayer( self.targetTileMapLayer )
	self.targetTileMapLayer = false
end

function TileMapEditor:moveTileMapLayerUp( layer )
	--TODO
end

function TileMapEditor:moveTileMapLayerDown( layer )
	--TODO
end

function TileMapEditor:selectTileBrush( id, additive )
	self.currentTileBrush = id
end

function TileMapEditor:getTileBrush()
	return self.currentTileBrush
end

function TileMapEditor:setTerrainBrush( brush )
	self.currentTerrainBrush = brush
	self:changeEditTool( 'terrain' )
end

function TileMapEditor:getTerrainBrush()
	return self.currentTerrainBrush
end

function TileMapEditor:changeEditTool( id )
	if not self.targetTileMapLayer then
		mock_edit.alertMessage( 'message', 'no target tilemap layer selected', 'info' )
		return
	end
	if id == 'pen' then		
		mock_edit.getCurrentSceneView():changeEditTool( 'tilemap.pen' )
		_module.clearTerrainSelection()

	elseif id == 'eraser' then
		mock_edit.getCurrentSceneView():changeEditTool( 'tilemap.eraser' )
		self.tilesetViewer:clearSelection()
	elseif id == 'fill' then
		mock_edit.getCurrentSceneView():changeEditTool( 'tilemap.fill' )
	elseif id == 'terrain' then
		mock_edit.getCurrentSceneView():changeEditTool( 'tilemap.terrain' )
		self.tilesetViewer:clearSelection()
	elseif id == 'clear' then
		self:getTargetTileMapLayer():getMoaiGrid():fill(0)
		mock_edit.getCurrentSceneView():updateCanvas()
	end
end

function TileMapEditor:toggleToolRandom( enabled )
	self.randomEnabled = enabled
end


--------------------------------------------------------------------
CLASS: TileMapToolPen ( mock_edit.CanvasTool )
	:MODEL{}

function TileMapToolPen:__init()
	self.pressed = false
end

function TileMapToolPen:onMouseDown( btn, x, y )
	if btn == 'left' then 
		self.pressed = true
		self:_doAction( x, y )
	end
end

function TileMapToolPen:onAction( layer, x, y )
	local brush = editor:getTileBrush()
	if brush then
		layer:setTile( x,y, brush )
	end
end

function TileMapToolPen:onMouseUp( btn, x, y )
	self.pressed = false
	self.targetRoom = false
end

function TileMapToolPen:onMouseMove( x, y )
	if self.pressed then
		self:_doAction( x, y )
	end
end

function TileMapToolPen:_doAction( x, y )
	local tx, ty = editor:wndToCoord( x, y )
	local layer  = editor:getTargetTileMapLayer()
	if layer:isValidCoord( tx, ty ) then
		self:onAction( layer, tx, ty )
		mock_edit.getCurrentSceneView():updateCanvas()
	end
end

mock_edit.registerCanvasTool( 'tilemap.pen', TileMapToolPen )


--------------------------------------------------------------------
CLASS: TileMapToolEraser ( TileMapToolPen )

function TileMapToolEraser:onAction( layer, x, y )
	layer:setTile( x, y, false )
end

mock_edit.registerCanvasTool( 'tilemap.eraser', TileMapToolEraser )


--------------------------------------------------------------------
CLASS: TileMapToolFill ( TileMapToolPen )

local function _floodFill( grid, x, y, w, h, id0, id1 )
	if x < 1 then return end
	if y < 1 then return end
	if x > w then return end
	if y > h then return end
	local id = grid:getTile( x, y )
	if id ~= id0 then return end
	grid:setTile( x, y, id1 )
	_floodFill( grid, x+1, y, w, h, id0, id1 )
	_floodFill( grid, x-1, y, w, h, id0, id1 )
	_floodFill( grid, x, y+1, w, h, id0, id1 )
	_floodFill( grid, x, y-1, w, h, id0, id1 )
end

function TileMapToolFill:onAction( layer, x, y )
	local brush = editor:getTileBrush()
	--flood fill
	if not brush then return end
	local layer = editor:getTargetTileMapLayer()
	local grid = layer:getMoaiGrid()
	local brushId = layer:tileIdToGridId( brush )
	local id0 = grid:getTile( x, y )
	local w, h = grid:getSize()
	if id0 == brushId then return end
	_floodFill( grid, x,y, w,h, id0, brushId )
end


mock_edit.registerCanvasTool( 'tilemap.fill', TileMapToolFill )


--------------------------------------------------------------------
CLASS: TileMapToolTerrain ( TileMapToolPen )


function TileMapToolTerrain:onAction( layer, x, y )
	local brush = editor:getTerrainBrush()
	--flood fill
	if not brush then return end
	print( x,y, brush.name )
end


mock_edit.registerCanvasTool( 'tilemap.terrain', TileMapToolTerrain )


--------------------------------------------------------------------
editor = scn:addEntity( TileMapEditor() )


