module 'mock'

MOAIUntzSystem.initialize ()

-- CLASS: MusicPlayer ( Component )

-- function MusicPlayer
-- local checkFileExists=MOAIFileSystem.checkFileExists
-- function Game:registerSound(table,preloadAll)
-- 	local st={}
-- 	self.soundTable=st
-- 	self.soundCache={}
-- 	--check file existence
-- 	local missingFiles={}
-- 	for k,s in pairs(table) do
-- 		st[s.name or s.file]=s
-- 		if type(s.file)=='table' then
-- 			for k,f in pairs(s.file) do
-- 				if not checkFileExists(f) then
-- 					missingFiles[f]=true
-- 				end
-- 			end
-- 		else
-- 			if not checkFileExists(s.file) then
-- 				missingFiles[s.file]=true
-- 			end
-- 		end		
-- 	end

-- 	if next(missingFiles) then
-- 		for f in pairs(missingFiles) do
-- 			print(f)
-- 		end
-- 		error('Missing Above Sound File(s):')
-- 	end

-- 	if preloadAll then self:preloadSounds() end
	
-- end

-- function Game:initSound()
-- 	self.soundPool={}
-- 	self.playingSound={}
	
-- 	-- for i=1,10 do
-- 	-- 	self:allocSoundChannel() --fill sound pool
-- 	-- end

-- 		--extend sound to support extra volume setting
-- 	local tmpSound=self:allocSoundChannel()
-- 	local mt=getmetatable(tmpSound)
-- 	local mt2=getmetatable(mt)
-- 	local index=mt2.__index
	
-- 	local _setVolume,_seekVolume,_moveVolume
-- 		=
-- 		tmpSound.setVolume,tmpSound.seekVolume,tmpSound.moveVolume

-- 	index.setVolume=function(self,v)
-- 		local sv=self.subVolume or 1
-- 		return _setVolume(self, sv *v)
-- 	end

-- 	index.seekVolume=function(self,v,l,m)
-- 		local sv=self.subVolume or 1
-- 		return _seekVolume(self,sv *v,l,m)
-- 	end

-- 	index.moveVolume=function(self,v,l,m)
-- 		local sv=self.subVolume or 1
-- 		return _moveVolume(self, sv *v,l,m)
-- 	end	

-- end


-- function Game:preloadSounds()
-- 	if not self.soundTable then return end
-- 	for k,s in pairs(self.soundTable) do
-- 		if not s.noBuffer or s.preload then
-- 			if type(s.file)=='table' then
-- 				for k,f in pairs(s.file) do
-- 					-- print('Loading Sound:',f)
-- 					self:getSoundBuffer(f)
-- 				end
-- 			else
-- 				-- print('Loading Sound:',s.file)
-- 				self:getSoundBuffer(s.file)	
-- 			end		
-- 		end
-- 	end
-- end

-- function Game:setVolume(v)
-- 	MOAIUntzSystem.setVolume(v)
-- end

-- function Game:seekVolume(v,time)
-- 	local v0=MOAIUntzSystem.getVolume()
	
-- 	local th=timedAction(
-- 		function(k)			
-- 			MOAIUntzSystem.setVolume(lerp(v0,v,k))
-- 		end, time
-- 	)
-- 	return th
-- end

-- function Game:seekMusicVolume(v,t)
-- 	if self.playingMusic then
-- 		if self.musicSeekAction then 
-- 			self.musicSeekAction:stop()
-- 			self.musicSeekAction=nil
-- 		end
-- 		self.musicSeekAction=self.playingMusic:seekSubVolume(v,t)
-- 		return self.musicSeekAction
-- 	end
-- 	return nil
-- end


-- function Game:getSoundBuffer(file)
-- 	local cache=self.soundCache
-- 	local buf=cache[file]
-- 	if not buf then
-- 		buf=MOAIUntzSampleBuffer.new()
-- 		if not MOAIFileSystem.checkFileExists(file) then
-- 			print('WARN: sound file not found:'..file)
-- 			-- return
-- 		else
-- 			buf:load(file)
-- 		end
-- 		cache[file]=buf
-- 	end
-- 	return buf
-- end

-- function Game:playSound(name,fadeTime, loadIntoMemory)
-- 	local s=self.soundTable[name]
-- 	-- print('sound:',name)
-- 	if s then
-- 		local sound=self:allocSoundChannel()
-- 		sound.data=s
-- 		local file=s.file

-- 		if type(file)=='table' then
-- 			local listmode=s.listmode

-- 			if listmode=='cycle' then
-- 				local file1=table.remove(file,1)
-- 				table.insert(file,file1)
-- 				file=file1

-- 			elseif listmode=='random-cycle' then
-- 				local file1=randextract(file)

-- 				if not file1 then 
-- 					file=s.lastPlay 
-- 				else
-- 					if s.lastPlay then
-- 						table.insert(file,s.lastPlay)
-- 					end
-- 					file=file1
-- 				end

-- 			else
-- 				file=randselect(file)
-- 			end

-- 			s.lastPlay=file
-- 		end
		
-- 		-- sound.file=file

-- 		if loadIntoMemory==false or s.noBuffer then
-- 			sound:load ( file ,false)
-- 		else
-- 			local buf=self:getSoundBuffer(file)
-- 			sound:load(buf)
-- 		end
-- 		local volume=s.volume
-- 		if volume then
-- 			if type(volume)=='table' then
-- 				volume=rand(volume[1],volume[2])
-- 			end
-- 		else
-- 			volume=1
-- 		end
		
-- 		sound.subVolume=volume

-- 		if fadeTime then
-- 			sound:setVolume(0)
-- 			sound:seekVolume(1, fadeTime)

-- 		else
-- 			sound:setVolume (1)
-- 		end

-- 		sound:setLooping ( s.loop or false )
-- 		sound:play()
-- 		self.playingSound[sound]=true
-- 		return sound
-- 	else
-- 		error('sound not found:'..name)
-- 	end
-- end

-- local soundCheckCounter=3
-- function Game:allocSoundChannel()
-- 	local pool=self.soundPool
-- 	local s=next(pool)

-- 	if not s then
-- 		soundCheckCounter=soundCheckCounter-1
-- 		if soundCheckCounter<=0 then 
-- 			soundCheckCounter=3
-- 			s=self:updateSoundPool()
-- 		end
-- 	end

-- 	if not s then
-- 		return MOAIUntzSound.new()
-- 	else
-- 		pool[s]=nil		
-- 		return s
-- 	end

-- end

-- function Game:updateSoundPool()
-- 	local playingSound=self.playingSound
-- 	local pool=self.soundPool
-- 	local lastSound
-- 	local playing=0
-- 	local ending=0
-- 	for s in pairs(playingSound) do
-- 		if not s:isPlaying() then
-- 			ending=ending+1
-- 			playingSound[s]=nil			
-- 			pool[s]=true
-- 			lastSound=s
-- 		else
-- 			playing=playing+1
-- 		end
-- 	end
-- 	return lastSound
-- end

-- function Game:musicThread()

-- end

-- function Game:playMusic(name,fadetime)
-- 	if self.playingMusic then
-- 		self:stopMusic(fadetime)
-- 	end
-- 	local mus=self:playSound(name,fadetime,false)
-- 	self.playingMusic=mus
-- end

-- function Game:pauseMusic()
-- 	if not  self.playingMusic then return end
-- 	self.playingMusic:pause()
-- end

-- function Game:resumeMusic()
-- 	if not  self.playingMusic then return end
-- 	self.playingMusic:play()
-- end

-- function Game:stopMusic(fadeTime)
-- 	if not  self.playingMusic then return end	

-- 	if fadeTime and fadeTime>0 then
-- 		local m=self.playingMusic
-- 		threadAction(
-- 			function()
-- 				MOAICoroutine.blockOnAction(
-- 					m:seekVolume(0,fadeTime)
-- 				)
-- 				m:stop()
-- 				-- print('stopped')				
-- 			end
-- 		)
-- 	else
-- 		self.playingMusic:stop()
-- 	end

-- 	self.playingMusic=nil
-- end


-- function Component:onAttach( owner )

-- end

-- function Component:onDetach( owner )
-- end

-- CLASS: SoundSource ( Component )
-- function SoundSource:setSample()
-- end

