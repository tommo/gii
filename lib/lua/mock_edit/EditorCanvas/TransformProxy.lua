module 'mock_edit'

--------------------------------------------------------------------
--Transform Proxy
--------------------------------------------------------------------
CLASS: TransformProxy( EditorEntity )

function TransformProxy:__init()
	self.updateNode = MOAIScriptNode.new()	
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
	self.updateNode:setCallback( function() self:onUpdate() end )
	self.updateNode:setNodeLink( self._prop )
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
