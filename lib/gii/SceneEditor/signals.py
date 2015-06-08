from gii.core.signals import register 

register( 'scene.pre_open' )
register( 'scene.update' )
register( 'scene.clear' )
register( 'scene.save' )
register( 'scene.saved' )
register( 'scene.open' )
register( 'scene.close' )
register( 'scene.change' ) #Scene is changed during preview

register( 'scene.modified' )

register( 'entity.added' )
register( 'entity.removed' )
register( 'entity.modified' )
register( 'entity.renamed' )

register( 'prefab.unlink' )
register( 'prefab.relink' )
register( 'prefab.push' )
register( 'prefab.pull' )

register( 'proto.unlink' )
register( 'proto.relink' )

register( 'component.added' )
register( 'component.removed' )

register( 'animator.start' )
register( 'animator.stop' )

register( 'tool.change' )
register( 'tool_category.update' )
