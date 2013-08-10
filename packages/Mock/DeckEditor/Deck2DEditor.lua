--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------

--------------------------------------------------------------------
CLASS: Deck2DEditor( mock.Entity )

function Deck2DEditor:onLoad()
	self:addSibling( CanvasGrid() )
	self:addSibling( CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
end

function Deck2DEditor:openDeck( node )
end

--------------------------------------------------------------------
editor = scn:addEntity( Deck2DEditor() )
