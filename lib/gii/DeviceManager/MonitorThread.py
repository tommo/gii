import threading
import time
import logging

from MobileDevice.MobileDevice import *
import MobileDevice

from IOSDevice import IOSDeviceItem

##----------------------------------------------------------------##
class DeviceMonitorThread( threading.Thread ):
	def __init__( self, callback, *args ):
		super( DeviceMonitorThread, self ).__init__( *args )
		self.devices = {}
		self.callback = callback
		self.active   = False
		self.deamon   = True

	def run( self ):		
		self.active   = True
		devices = self.devices
		def cbFunc(info, cookie):
			info = info.contents
			if info.message == ADNCI_MSG_CONNECTED:
				dev = IOSDeviceItem( MobileDevice.AMDevice(info.device), True )
				devices[info.device] = dev
				self.callback( 'connected', dev )

			elif info.message == ADNCI_MSG_DISCONNECTED:
				dev = devices[info.device]
				self.callback( 'disconnected', dev )
				dev.disconnect()
				del devices[info.device]

		notify = AMDeviceNotificationRef()
		notifyFunc = AMDeviceNotificationCallback(cbFunc)
		err = AMDeviceNotificationSubscribe(notifyFunc, 0, 0, 0, byref(notify))
		if err != MDERR_OK:
			raise RuntimeError(u'Unable to subscribe for notifications')

		# loop so we can exit easily
		while self.active:
			CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.01, False)
			time.sleep( 0.1 )

		AMDeviceNotificationUnsubscribe(notify)

	def getDevices( self ):
		return self.devices

	def stop( self ):
		self.active = False

##----------------------------------------------------------------##
_monitorThread = None
def startDeviceMonitorThread( callback, *args ):
	global _monitorThread
	_monitorThread = DeviceMonitorThread( callback, *args )
	_monitorThread.start()

def stopDeviceMonitorThread():
	global _monitorThread
	_monitorThread.stop()
	_monitorThread = None

