function OnTestStart()
	CLASS: ActionTest ( UserAction )
	function ActionTest:__init(name)
		self.name=name or '???'
	end

	function ActionTest:onUpdate(dt)
		if self.ready then
			print('fire!',self.name)
			return true
		else
			print('ready',self.name)
			self.ready=true
		end
	end

	function ActionTest:onStart()
		print('start',self.name)
	end
	function ActionTest:onFinish()
		print('done',self.name)
	end


	local mgr=UserActionMgr()

	print('add action:1')
	mgr:addAction(ActionTest('1'))
	print('chain action:3->1')
	mgr:chainLast(ActionTest('3'))
	print('add action:2')
	mgr:addAction(ActionTest('2'))

	print(' \ncycle: 1')
	mgr:update(1)

	print(' \ncycle: 2')
	mgr:update(1)

	print(' \ncycle: 3')
	mgr:update(1)

	assert(mgr:isEmpty())
end