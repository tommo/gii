module 'mock_edit'

--------------------------------------------------------------------
--Transform Proxy
--------------------------------------------------------------------
CLASS: TransformProxy( EditorEntity )

function TransformProxy:__init()
	self.updateNode = MOAIScriptNode.new()
	self.updateNode:setCallback( function() self:onUpdate() end )
	self.updateNode:setNodeLink( self._prop )
	self.syncing = false
end

function TransformProxy:setTargets( targets )
	self.targets = targets
	local proxies = {}
	self.proxies = proxies

	local count = 0
	local prop  = self._prop
	for e in pairs( targets ) do		
		local proxy = MOAITransform.new()
		proxies[e] = proxy
		inheritTransform( proxy, prop )
		count = count + 1
	end
	self.targetCount = count
	self:updatePivot()
	self:syncFromTarget()
end

function TransformProxy:refresh()
	self:syncFromTarget()
end

function TransformProxy:updatePivot()
	local totalX, totalY = 0, 0
	for e in pairs( self.targets ) do
		e:forceUpdate()		
		local x1,y1 = e:modelToWorld( e:getPiv() )
		totalX = totalX + x1
		totalY = totalY + y1		
	end
	local count = self.targetCount
	self:setLoc( totalX/count, totalY/count, 0 )	

	if count == 1 then
		self.rot0 = next( self.targets ):getRotZ()
	else
		self.rot0 = 0
	end
	self:setRotZ( self.rot0 )
end

function TransformProxy:syncFromTarget()
	self.syncing = true
	self:forceUpdate()
	for e, proxy in pairs( self.proxies ) do
		e:forceUpdate()
		proxy:forceUpdate()
		syncWorldTransform( proxy, e )
		proxy:forceUpdate()
	end
	self.syncing = false
end

function TransformProxy:onUpdate()
	if self.syncing then return end
	self.syncing = true
	self:forceUpdate()
	for e, proxy in pairs( self.proxies ) do
		e:forceUpdate()
		proxy:forceUpdate()
		syncWorldTransform( e, proxy )
		e:forceUpdate()
		gii.emitPythonSignal( 'entity.modified', e )
	end
	self.syncing = false
end

-- function TransformProxy:setTargets( targets )
-- 	self.targets = targets
-- 	local proxies = {}
-- 	self.proxies = proxies
-- 	local count = 0

-- 	local trans = self._prop

-- 	local totalX, totalY = 0, 0
-- 	for e in pairs( targets ) do
-- 		e:forceUpdate()
-- 		local x1,y1 = e:modelToWorld( e:getPiv() )
-- 		totalX = totalX + x1
-- 		totalY = totalY + y1
-- 		count = count + 1
-- 		local proxy = MOAITransform.new()
-- 		proxies[e] = proxy
-- 		inheritTransform( proxy, trans )
-- 	end

		
-- 	self.targetCount = count
-- 	trans:forceUpdate()
-- 	self:syncFromTarget()
-- end

-- function TransformProxy:syncFromTarget()
-- 	for e, proxy in pairs( self.proxies ) do
-- 		e:forceUpdate()
-- 		local px, py, pz = e:getPiv()
-- 		local x, y, z = self:worldToModel( e:modelToWorld( px,py,pz ) )
-- 		local rx,ry,rz = e:getRot()
-- 		proxy:setLoc( x, y, z )
-- 		proxy:setRot( rx, ry, rz )
-- 		proxy.rz0 = rz
-- 		proxy:setScl( e:getScl() )
-- 	end

-- 	if self.targetCount == 1 then
-- 		self.rot0 = next( self.targets ):getRotZ()
-- 		self:setRotZ( self.rot0 )
-- 	else
-- 		self.rot0 = 0
-- 	end

-- 	self:forceUpdate()
-- end

-- local function syncWorldLoc( e, proxy )
-- 	local x,y,z = proxy:modelToWorld( 0,0,0 )
-- 	local p = e.parent
-- 	local x0,y0,z0 = e:getLoc()
-- 	if p then
-- 		x, y, z = p:worldToModel( x, y, z )
-- 		e:setLoc( x, y, z0 )
-- 	else
-- 		e:setLoc( x, y, z0 )
-- 	end
-- end

-- local function getWorldRot( e )

-- end

-- local function setWorldRot( e )

-- end

-- function TransformProxy:onUpdate()
-- 	local sx,sy,sz = self:getScl()
-- 	local rx,ry,rz = self:getRot()
-- 	for e, proxy in pairs( self.proxies ) do
-- 		proxy:forceUpdate()
-- 		syncWorldLoc( e, proxy )
-- 		local sx1,sy1,sz1 = proxy:getScl()
-- 		local rx1,ry1,rz1 = proxy:getRot()
-- 		e:setScl( sx*sx1, sy*sy1, sz1 )
-- 		e:setRot( rx+rx1, ry+ry1, rz + rz1 - self.rot0 )
-- 		gii.emitPythonSignal( 'entity.modified', e )
-- 	end
-- end
