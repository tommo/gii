import freejoy
import time

count= freejoy.getJoystickCount()
print 'joysticks:', count 


j1 = freejoy.Joystick( 1 )
print( j1.getName() )
print( j1.getButtonCaps() )

while True:
	axis = j1.getAxis( 9 )
	print '%.2f, %.2f, %.2f, %.2f || %.2f, %.2f, %.2f' % ( axis[0], axis[1], axis[2], axis[3], axis[6], axis[7], axis[8] )
	time.sleep( .2 )

