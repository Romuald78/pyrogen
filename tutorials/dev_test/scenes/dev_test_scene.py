from ....ecs3.components.gfx import GfxSprite, GfxBox
from ....ecs3.main.entity import Entity
from ....ecs3.main.scene import Scene
from ..components.scripts import MoveCircle, MoveSquare

import random


class FpsTest(Scene):

    def __init__(self):
        super().__init__()


        # Prepare number of Gfx components
        NX = 79
        NY = 38
        N = NX * NY

        for i in range(N):

            # -------------------------------------
            # Create Entity
            entity = Entity()

            # -------------------------------------
            # Create Sprite or plain color rectangle
            clr = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if i%2 == 0:
                index = random.randint(0,95)
                mySprite = GfxSprite(f"characters_{index}")
                mySprite.setColor(clr)
            else:
                w = random.randint(30,34)
                h = random.randint(46,50)
                mySprite = GfxBox(inClr=clr, width=w, height=h)
            # Position
            x = (i % NX) * (1920//NX)
            y = (i // NX) * (1080//NY)
            mySprite.setX(x)
            mySprite.setY(y)
#            mySprite.setAnchor(-16,-24)
            mySprite.setAutoRotate( random.randint(0,360) )
#            mySprite.setAngle( random.randint(0,360) )
#            mySprite.setFlipY(True)
            tALL = random.random() * 2 + 1.0
            tON  = random.random() * (tALL-0.1) + 0.1
            mySprite.setVisibility( tON, tALL )
#            mySprite.setScale(1.5)

            # -------------------------------------
            # Create script to move sprite
            radius = random.randint(30,300)
            speed  = random.randint(-360,360)
            if random.random()<0.5:
                scrMove = MoveCircle(mySprite, (x,y), radius, speed)
            else:
                scrMove = MoveSquare(mySprite, (x, y), radius, speed)

            # -------------------------------------
            # Add both components into entity
            entity.addComponent(mySprite)
            entity.addComponent(scrMove)

            # -------------------------------------
            # Add entity to the Scene (containing both components)
            self.addEntity(entity)

