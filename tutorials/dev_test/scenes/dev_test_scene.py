from ....ecs3.components.gfx import GfxSprite, GfxBox
from ....ecs3.main.entity import Entity
from ....ecs3.main.scene import Scene


import random


class FpsTest(Scene):

    def __init__(self):
        super().__init__()

        # Create Entity
        entity = Entity()

        # Prepare number of Gfx components
        NX = 59
        NY = 22
        N = NX * NY

        # Create Sprites and plain rectangles
        for i in range(N):
            clr = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if i%2 == 0:
                index = random.randint(0,95)
                mySprite = GfxSprite(f"characters_{index}")
                mySprite.setColor(clr)
            else:
                w = random.randint(27,37)
                h = random.randint(43,53)
                mySprite = GfxBox(inClr=clr, width=w, height=h)
            # Position
            mySprite.setX((i % NX) * 32)
            mySprite.setY((i // NX) * 48)
#            mySprite.setAnchor(-16,-24)
            mySprite.setAutoRotate( random.randint(0,360) )
#            mySprite.setAngle( random.randint(0,360) )
#            mySprite.setFlipY(True)
            tALL = random.random() * 2 + 1.0
            tON  = random.random() * (tALL-0.1) + 0.1
            mySprite.setVisibility( tON, tALL )
            mySprite.setScale(1.5)

            # Add Sprite into entity
            entity.addComponent(mySprite)


        # Add entity to the Scene
        self.addEntity(entity)
