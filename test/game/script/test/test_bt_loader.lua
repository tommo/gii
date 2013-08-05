
NO_WINDOW = true

CLASS: ActAlert ( mock.BTAction )
function ActAlert:step( owner, dt )

end

function OnTestStart()
	print('-----------')

	local tree = mock.BehaviorTree()
	tree:load( assert( BTDATA['creature'] ) )

	local context = mock.BTContext()
	context:setTree( tree )
		
	context['combat.mode.melee'] = true
	local i =1
	
	local actMove = {
		step = function( context )
			print('moving ..', i)
			i = i + 1
			if i >= 10 then return 'ok' end
			return 'running'
		end
	}
	context:registerAction( 'actMove', actMove )
	context:registerAction( 'actAlert', {step=function() print('ALERT!!!!') end} )

	context:update()
	context:update()
	context['enemy.spotted'] = true
	context:update()
	context:update()
	context['scared'] = true
	context:update()


end