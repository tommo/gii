require 'mock.env'

--------------------------------------------------------------------
-- mock.setLogLevel( 'status' )

module( 'mock_edit', package.seeall )

--------------------------------------------------------------------
--CORE
--------------------------------------------------------------------
require 'mock_edit.common.signals'
require 'mock_edit.common.ModelHelper'
require 'mock_edit.common.ClassManager'
require 'mock_edit.common.EditorCommand'
require 'mock_edit.common.SceneTool'
require 'mock_edit.common.DeployTarget'
require 'mock_edit.common.bridge'
require 'mock_edit.common.utils'


--------------------------------------------------------------------
--EDITOR UI HELPER
--------------------------------------------------------------------
require 'mock_edit.UIHelper'


--------------------------------------------------------------------
--Editor related
--------------------------------------------------------------------
require 'mock_edit.EditorCanvas'


--------------------------------------------------------------------
--DEPLOY TARGETs
--------------------------------------------------------------------
require 'mock_edit.deploy.DeployTargetIOS'


--------------------------------------------------------------------
--Editor Related Res
--------------------------------------------------------------------
require 'mock_edit.common.resloader'


--------------------------------------------------------------------
require 'mock_edit.AssetHelper.DeckReloader'
require 'mock_edit.AssetHelper.ShaderReloader'
require 'mock_edit.AssetHelper.FMODReloader'

--------------------------------------------------------------------
--COMMANDS
--------------------------------------------------------------------
require 'mock_edit.commands'
require 'mock_edit.gizmos'
require 'mock_edit.tools'

require 'mock_edit.defaults'

require 'mock_edit.drag'


mock._allowAssetCacheWeakMode( false )
MOAISim.getInputMgr().configuration = 'GII'
