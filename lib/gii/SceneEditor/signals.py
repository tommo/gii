from gii.core.signals import register 

register( 'scene.pre_open' )
register( 'scene.update' )
register( 'scene.clear' )
register( 'scene.open' )
register( 'scene.close' )
register( 'scene.change' ) #Scene is changed during preview


register( 'scene.modified' )

register( 'entity.added' )
register( 'entity.removed' )
register( 'entity.modified' )
register( 'entity.renamed' )

register( 'component.added' )
register( 'component.removed' )