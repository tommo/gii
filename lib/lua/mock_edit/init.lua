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
require 'mock_edit.common.DeployTarget'
require 'mock_edit.common.bridge'


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
require 'mock_edit.AssetHelper.FMODReloader'
