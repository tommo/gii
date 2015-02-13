local insert,remove=table.insert,table.remove
local next=next
CLASS: UserAction ()

function UserAction:__init()
	self.state='wait'
end

function UserAction:isWaiting()
	return self.state~='wait'
end

function UserAction:isDone()
	return self.state=='done'
end

function UserAction:isBusy()
	return self.state=='busy'
end

function UserAction:update(dt)
	local state=self.state	
	
	if state=='busy' then
		if self:onUpdate(dt) then 
			self.state='done'
			return self:onFinish()
		end
	end
	if state=='wait' then
		self:onStart()
		self.state='busy'
		return self:update(dt)
	end

end

function UserAction:onStart()
end

function UserAction:onFinish()
end

function UserAction:onUpdate(dt)
end

function UserAction:addNext(a)
	assert(self.state~='done', 'action already done')

	local nextActions=self.nextActions
	if not nextActions then
		nextActions={}
		self.nextActions=nextActions
	end
	insert(nextActions,a)
	return a
end


CLASS: UserActionMgr ()

function UserActionMgr:__init()
	self.actions={}
end

function UserActionMgr:isEmpty()
	return not self.actions[1]
end

function UserActionMgr:addAction(a,addFirst)
	local actions=self.actions
	if addFirst then 
		insert(actions,1,a)
	else
		insert(actions,a)
	end
	return a
end

function UserActionMgr:chainLast(a)
	local last=self.actions[1]
	if not last then return self:addAction(a) end
	return last:addNext(a)
end

function UserActionMgr:update(dt)
	local d=0
	local i=nil

	local actions=self.actions
	while true do
		i,a = next(actions,i)
		if not i then return end

		a:update(dt)
		if a.state=='done' then
			local nextActions=a.nextActions
			if nextActions then
				for n, na in ipairs(nextActions) do
					self:addAction(na)
				end
			end
			remove(actions,i)
			i=i-1
			if i<1 then i=nil end
		end

	end

end
