import os
import sys
import logging

from watchdog.observers import Observer
from watchdog.events    import FileSystemEventHandler,PatternMatchingEventHandler
from gii.core           import EditorModule, app, signals

##----------------------------------------------------------------##
class ModuleFileWatcher( EditorModule ):
	def __init__(self):
		super(ModuleFileWatcher, self).__init__()
		self.watches={}

	def getName(self):
		return 'filewatcher'

	def getDependency(self):
		return []

	def onLoad(self):		
		self.observer=Observer()
		self.observer.start()

		self.assetWatcher=self.startWatch(
			self.getProject().getAssetPath(),
			ignorePatterns=['*/.git','*/.*','*/_gii']
		)

		signals.connect('file.moved', self.onFileMoved)
		signals.connect('file.added', self.onFileCreated)
		signals.connect('file.modified', self.onFileModified)
		signals.connect('file.removed', self.onFileDeleted)
		

	def startWatch(self, path, **options):
		path=os.path.realpath(path)
		if self.watches.get(path):
			logging.warning( 'already watching: %s' % path )
			return self.watches[path]
		logging.info ( 'start watching: %s' % path )
		handler=FileWatcherEventHandler(
				options.get('patterns',None),
				options.get('ignorePatterns',None),
				options.get('ignoreDirectories',False),
				options.get('caseSensitive',False)
			)
		watch=self.observer.schedule(handler, path, options.get('recursive',True))
		self.watches[path]=watch
		return watch

	def stopWatch(self, path):
		path  = os.path.realpath(path)
		watch = self.watches.get(path, None)
		if not watch: return
		self.observer.unschedule(watch)
		self.watches[path] = None

	def stopAllWatches(self):
		for path in self.watches:
			self.stopWatch(path)

	
	def onFileMoved(self, path, newpath):
		# print('asset moved:',path, newpath)
		app.getAssetLibrary().scanProjectPath()
		pass

	def onFileCreated(self, path):
		# print('asset created:',path)
		app.getAssetLibrary().scanProjectPath()
		pass

	def onFileModified(self, path):
		# print('asset modified:',path)
		app.getAssetLibrary().scanProjectPath()
		pass

	def onFileDeleted(self, path):
		# print('asset deleted:',path)
		app.getAssetLibrary().scanProjectPath()
		pass

##----------------------------------------------------------------##
class FileWatcherEventHandler(PatternMatchingEventHandler):
	def on_moved(self, event):
		super(FileWatcherEventHandler, self).on_moved(event)
		signals.emit('file.moved', event.src_path, event.dest_path)

		# what = 'directory' if event.is_directory else 'file'
		# logging.info("Moved %s: from %s to %s", what, event.src_path,
		# 						 event.dest_path)

	def on_created(self, event):
		super(FileWatcherEventHandler, self).on_created(event)
		signals.emit('file.added', event.src_path)

		# what = 'directory' if event.is_directory else 'file'
		# logging.info("Created %s: %s", what, event.src_path)

	def on_deleted(self, event):
		super(FileWatcherEventHandler, self).on_deleted(event)
		signals.emit('file.removed', event.src_path)

		# what = 'directory' if event.is_directory else 'file'
		# logging.info("Deleted %s: %s", what, event.src_path)

	def on_modified(self, event):
		super(FileWatcherEventHandler, self).on_modified(event)
		signals.emit('file.modified', event.src_path)

		# what = 'directory' if event.is_directory else 'file'
		# logging.info("Modified %s: %s", what, event.src_path)


ModuleFileWatcher().register()