function OnTestStart()
  layer=sceneGlobal:getLayer('main')
  local mouseDown=false

  path = {}

  path_mt = { __index = path }

  function path.new()
    local new_inst = { 
      points = {}
    }

    setmetatable(new_inst, path_mt)
    return new_inst
  end

  function path:MOAISetup()
    path.vertexFormat = MOAIVertexFormat.new()
    path.vertexFormat:declareCoord ( 1, MOAIVertexFormat.GL_FLOAT, 2 )
    path.vertexFormat:declareUV ( 2, MOAIVertexFormat.GL_FLOAT, 2 )
    path.vertexFormat:declareColor ( 3, MOAIVertexFormat.GL_UNSIGNED_BYTE )

    self.mesh = MOAIMesh.new ()
    self.mesh:setTexture ( "moai.png" )
    self.mesh:setPrimType ( MOAIMesh.GL_LINE_STRIP)
    self.mesh:setPenWidth(3)

    self.prop = MOAIProp2D.new ()
    self.prop:setDeck ( self.mesh )
    self.prop:setVisible(false)

    self.vbo = MOAIVertexBuffer.new ()
    self.mesh:setVertexBuffer ( self.vbo )

    self.vbo:setFormat ( path.vertexFormat )
    self.vbo:reserveVerts ( 2 )
    
    -- if you comment the below lines out, and don't write data into 
    -- the vbo immediately but rather wait until the first call to
    -- render(), below, then nothing ever gets shown on screen.
    self.vbo:reset()

    self.vbo:writeFloat ( 0,0 )
    self.vbo:writeFloat ( 0.5, 0.5 )
    self.vbo:writeColor32 ( 0,0,0)

    self.vbo:writeFloat ( 0,0 )
    self.vbo:writeFloat ( 0.5, 0.5 )
    self.vbo:writeColor32 ( 0,0,0)
    self.vbo:bless()
    -- end bizarre hack

    self.target = { x = 0, y = 0 }
    self.from = { x = 0, y = 0 }
    self.shown = false
  end

  function path:render()
    if self.vbo ~= nil then self.vbo:reset() else
      print("err: vbo is nil")
    end

    self.vbo:writeFloat ( self.from.x,self.from.y )
    self.vbo:writeFloat ( 0.5, 0.5 )
    self.vbo:writeColor32 ( 1,1,1)

    self.vbo:writeFloat ( self.target.x, self.target.y )
    self.vbo:writeFloat ( 0.5, 0.5 )
    self.vbo:writeColor32 ( 1,1,1)

    self.vbo:bless()
  end

  function path:show()
    self.prop:setVisible(true)
  end

  function path:hide()
    self.prop:setVisible(false)
  end

  function path:length()
    local v = self.target - self.from
    return v:len()
  end

  function path:set_up_input()
    pointer_callback = 
    function(x,y)
      target_x, target_y = layer:wndToWorld(x,y)
      if mouseDown then
        p.target = { x = target_x, y = target_y }
        print('render')
        p:render()
        p:show()
      end
    end

    pick_callback = 
    function(down)
      if down then
        print("down")
        mouseDown = true
        picked = true
      else
        mouseDown = false
        picked = nil
      end
    end

    if MOAIInputMgr.device.pointer then
      MOAIInputMgr.device.pointer:setCallback(pointer_callback)
      MOAIInputMgr.device.mouseLeft:setCallback(pick_callback)
    else
      MOAIInputMgr.device.touch:setCallback (
        function(eventType,idx,x,y,tapCount)
          pointer_callback(x,y)
          if eventType == MOAITouchSensor.TOUCH_DOWN then
            pick_callback(true)
          elseif eventType == MOAITouchSensor.TOUCH_UP then
            pick_callback(false)
          end
        end
       )
    end
  end

  -- MOAISim.openWindow ( "vbo test", 320, 480 )

  -- viewport = MOAIViewport.new ()
  -- viewport:setSize ( 320, 480 )
  -- viewport:setScale ( 320, 480 )
   
  -- partition = MOAIPartition.new()
  -- layer = MOAILayer2D.new ()
  -- layer:setPartition(partition)
  -- layer:setViewport(viewport)

  -- MOAISim.pushRenderPass(layer)

  p = path.new()
  p:MOAISetup()
  p:set_up_input()
  layer:insertProp ( p.prop )

  function bloop()
    while true do
      p.from = { x = math.random(1,320) - 160, y = math.random(1,320)-160 }
      coroutine.yield()
    end
  end

  x = MOAICoroutine.new()
  x:run(bloop)
end