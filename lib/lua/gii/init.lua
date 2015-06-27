module( 'gii', package.seeall )
--------------------------------------------------------------------
--EDITOR MODULES
--------------------------------------------------------------------

require 'gii.bridge'
require 'gii.clidebugger'
require 'gii.debugger'

----------------------------
require 'gii.RenderContext'
require 'gii.EditCanvasContext'

--------------------------------------------------------------------
MOAIGfxResourceMgr.setResourceLoadingPolicy( MOAIGfxResourceMgr.LOADING_POLICY_CPU_ASASP_GPU_BIND )
-- MOAIGfxResourceMgr.setResourceLoadingPolicy( MOAIGfxResourceMgr.LOADING_POLICY_CPU_GPU_ASAP )
-- MOAIGfxResourceMgr.setResourceLoadingPolicy( MOAIGfxResourceMgr.LOADING_POLICY_CPU_GPU_BIND )
