--------------------------------------------------------------------
scn = mock_edit.createEditorCanvasScene()
--------------------------------------------------------------------

mock_edit.addColor( 'tilemap_grid', hexcolor( '#ff0000', 0.5 ) )
--------------------------------------------------------------------
CLASS: TilesetViewer ( mock_edit.EditorEntity )
	:MODEL{}

function TilesetViewer:__init()
	self.targetTilesetPath = false
	self.targetTileset = false
	self.viewProp = MOAIProp.new()
	self.viewGrid = false
end

function TilesetViewer:onLoad()
	self:_attachProp( self.viewProp )
	self:addChild( mock_edit.CanvasNavigate() )
end

function TilesetViewer:setTargetTileset( tilesetPath )
	self.targetTilesetPath = tilesetPath
	self.targetTileset = tilesetPath and mock.loadAsset( tilesetPath )
	if not self.targetTileset then return self:hide() end
	self:show()
	local tileset = self.targetTileset
	self.viewProp:setDeck( tileset:getMoaiDeck() )
	self.viewGrid = tileset:buildPreviewGrid()	
	self.viewProp:setGrid( self.viewGrid )
end

-- function TilesetViewer:

function TilesetViewer:fitViewport( w, h )
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
	self.currentTileBrush = false
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
	self.currentTileBrush    = 'FloorDirt.c'
	self.currentTileBrush    = 'WallBrick.s'
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

function TileMapEditor:setTileBrush( id )
	self.currentTileBrush = id
end

function TileMapEditor:getTileBrush()
	return self.currentTileBrush
end

function TileMapEditor:setTerrainBrush( id )
	self.currentTerrainBrush = id
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
	elseif id == 'eraser' then
		mock_edit.getCurrentSceneView():changeEditTool( 'tilemap.eraser' )
	end
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
	x, y = self:wndToWorld( x, y )
	local map = editor:getTargetTileMap()
	local layer = editor:getTargetTileMapLayer()
	local lx, ly = map._entity:worldToModel( x, y )
	local tx, ty = layer:locToCoord( lx, ly ) 
	if layer:isValidCoord( tx, ty ) then
		self:onAction( layer, tx, ty )
		mock_edit.getCurrentSceneView():updateCanvas()
	end
end

mock_edit.registerCanvasTool( 'tilemap.pen', TileMapToolPen )



--------------------------------------------------------------------
CLASS: TileMapToolEraser ( TileMapToolPen )

function TileMapToolEraser:onAction( layer, x, y )
	print( 'erase', x, y )
	layer:setTile( x, y, false )
end

mock_edit.registerCanvasTool( 'tilemap.eraser', TileMapToolEraser )


--------------------------------------------------------------------
CLASS: TileMapToolTerrain ( TileMapToolPen )

function TileMapToolTerrain:onAction( layer, x, y )
	layer:setTile( x,y, 0 )
end

mock_edit.registerCanvasTool( 'tilemap.terrain', TileMapToolTerrain )
--------------------------------------------------------------------


editor = scn:addEntity( TileMapEditor() )

