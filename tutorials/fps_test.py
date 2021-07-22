import math
import random

from pyrogen.src.pyrogen.ecs3.components.component import Component
from pyrogen.src.pyrogen.ecs3.components.gfx import GfxSprite, GfxBox
from pyrogen.src.pyrogen.ecs3.main.entity import Entity
from pyrogen.src.pyrogen.ecs3.main.pyrogen_app import PyrogenApp
from pyrogen.src.pyrogen.ecs3.main.scene import Scene

DEBUG_NB_SPRITES     = 100


def main():

    # -----------------------------------------------------------
    # INSTANCIATE APPLICATION
    # -----------------------------------------------------------
    app    = PyrogenApp(width=1920, height=1080, vsync=False, fsGpuMemSize=1*1024*1024*4)

    # -----------------------------------------------------------
    # ADD IMAGE RESOURCES
    # -----------------------------------------------------------
    # Add football image
    app.addImage("ball", "resources/images/fps_test/ball.png")
    # Add misc. sprites
    mini = 1
    maxi = 22
    for i in range(mini, maxi + 1):
        num = ("00" + str(i))[-3:]
        name = f"image{num}"
        app.addImage(name, f"resources/images/fps_test/{name}.png", (1, 5, 32, 32))
    # Add misc. sprites
    mini = 23
    maxi = 28
    for i in range(mini, maxi + 1):
        num = ("00" + str(i))[-3:]
        name = f"image{num}"
        app.addImage(name, f"resources/images/fps_test/{name}.png", (3, 4, 32, 32), )
    # Characters
    app.addImage("characters", f"resources/images/fps_test/characters001.png", (12, 8, 32, 48))

    # -----------------------------------------------------------
    # ADD FONT RESOURCES
    # -----------------------------------------------------------
    app.addFont("mandala", "resources/fonts/Mandala.ttf", 64)
    app.addFont("subway" , "resources/fonts/Subway.ttf" , 64)

    # -----------------------------------------------------------
    # FINALIZE RESOURCES
    # -----------------------------------------------------------
    app.finalizeResources()

    # -----------------------------------------------------------
    # ADD SCENES
    # -----------------------------------------------------------
    app.addScene( "MAIN", FpsTest() )

    # -----------------------------------------------------------
    # RUN APPLICATION
    # -----------------------------------------------------------
    app.run()




class FpsTest(Scene):

    def __init__(self):
        super().__init__()

        # Prepare sprites
        self._spriteMgr = SpriteMgr()
        sprList = self._spriteMgr.createRandomSprites(DEBUG_NB_SPRITES)


        # Create Entity
        entity = Entity()
        last = None
        for i in range(50):
            index = random.randint(0,10)
            entity.addComponent( sprList[index] )
            last = sprList[index]
            sprList.remove(sprList[index])
        self.addEntity(entity)

        last.setZIndex(1)


#        vd = array("l", self._spriteMgr.genVertex())
#        self._openGlData.set("vertexData", vd)
#        # write into GPU for the first time
#        self._openGlData.get("vertexBuffer").write(vd)

  #      entity.destroy()

  #      print( self.getNbEntities() )
  #      print( entity.getComponentsByType(Component.TYPE_GFX))




class SpriteMgr():

    __slots__ = ["_sprites",
                 "_dbgTime",
                 "_N",
                 ]

    def __init__(self):
        self._sprites = []

    def createRandomSprites(self, N):
        squareSize = int(round(math.sqrt(DEBUG_NB_SPRITES),0))

        names = ["characters_"+str(i) for i in range(96)]

        for i in range(N):
            # Name
            name = random.choice(names)
            # Position
            x = (i  % squareSize) * 32
            y = (i // squareSize) * 32
            z = i
            # Size
            width   = random.randint(22,42)
            height  = random.randint(22,42)
            # Anchor
            anchorX = random.randint(-width,width)
            anchorY = random.randint(-height,height)
            # rotation
            angle   = random.randint(0,360)
            autoRot = random.randint(0,270) - 135
            # visibility PWM
            total   = random.random()*9.0 + 1.0
            on      = random.random()*total
            # filter
            clr = (random.randint(128,255),random.randint(128,255),random.randint(128,255),random.randint(128,255))
            # Add Sprite or basic shape
            if random.random()<=10.5:
                scale = width/32
                #Sprite creation
                sprite  = GfxSprite(name,
                                    x=x, y=y, z=z,
#                                    width=width, height=width,  # for sprites, W=H
                                    angle=angle,
                                    visOn=on, visTot=total,
                                    autoRotate=autoRot,
                                    anchorX=anchorX,
                                    anchorY=anchorY,
                                    filterColor=clr)
                self._sprites.append(sprite)
            else:
                inClr  = (random.randint(0,255),random.randint(64,192),random.randint(128,255),random.randint(128,255))
                sprite = GfxBox(inClr=inClr,
                                x=x, y=y, z=z,
                                width=width, height=height,
                                angle=angle,
                                visOn=on, visTot=total,
                                autoRotate=autoRot,
                                anchorX=anchorX,
                                anchorY=anchorY  )
                self._sprites.append(sprite)

        self._dbgTime = 0
        self._N = 0
        return self._sprites

    def updateMovingSprites(self, currentTime, winSize):
        # prepare local vars
        i = 0
        L = len(self._sprites) / 4
        hw = winSize[0] / 8
        hh = winSize[1] / 8
        cw = winSize[0] / 2
        ch = winSize[1] / 2
        clr = [0,0,0]
        # update all sprites
        for spr in self._sprites:
            # sprite specific values
            randI = i/L
            t = currentTime * randI
            # Position (write data into the array.array)
            x = (math.cos(t) * randI * hw) + cw
            y = (math.sin(t) * randI * hh) + ch
            # scale (write data into the array.array)
            scl = randI * 0.4 + 0.25
            # Rotation (write data into the array.array)
            ang =  math.sin(currentTime + i) * 180
            # Set properties
            spr.setTransform(x, y, ang)
            spr.setScale(scl)
            # update sprite
            # (copy the whole sprite array.array into the GPU texture)
            spr.update(1/60)
            # increase i for next iteration
            i += 1

    def updateFixedSprites(self, currentTime, winSize):
        # update all sprites
        for spr in self._sprites:
            spr.update(1/60)

    def genVertex(self):
        for i in range(len(self._sprites)):
            spr = self._sprites[i]
            yield spr.getBlockID()





if __name__ == '__main__':
    main()

