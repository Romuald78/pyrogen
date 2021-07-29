from ....ecs3.main.scene       import Scene
from ....ecs3.main.entity      import Entity
from ....ecs3.main.common      import Buttons, Gamepads, Axis
from ....ecs3.components.gfx   import GfxSprite, GfxBox
from ....ecs3.components.input import Keyboard, GamepadButton, MouseButton, GamepadAxis

from ..components.scripts import MoveCircle, MoveSquare, ShowHide, MoveShip

import pyglet.window.key as keys
import random


class FpsTest(Scene):

    def __init__(self):
        super().__init__()

        # ----------------------------------------------
        # Ship entity
        # ----------------------------------------------
        ship = Entity()
        # Create components
        shipGfx = GfxSprite(f"ship001")
        shipGfx.setX(480)
        shipGfx.setY(540)
        shipGfx.setZIndex(20000)
        shipGfx.setScale(1.0)
        axis = GamepadAxis(0.1)
        axis.addAxis(Gamepads.ANY, Axis.LX, "moveX")
        axis.addAxis(Gamepads.ANY, Axis.LY, "moveY")
        axis.addAxis(Gamepads.ANY, Axis.RX, "moveX")
        axis.addAxis(Gamepads.ANY, Axis.RY, "moveY")
        moveShip = MoveShip(shipGfx, axis)
        # add components to entity
        ship.addComponent(shipGfx)
        ship.addComponent(axis)
        ship.addComponent(moveShip)
        # Add ship to scene
        self.addEntity(ship)

        # ----------------------------------------------
        # Main Sprite
        # ----------------------------------------------
        mainCharacter = Entity()
        # Create components
        mySprite = GfxSprite(f"characters_0")
        mySprite.setX(960)
        mySprite.setY(540)
        mySprite.setZIndex(10000)
        mySprite.setScale(4)
        padButtons = GamepadButton()
        padButtons.addButton(Gamepads.ANY, Buttons.A  , "Hide"   )
        padButtons.addButton(Gamepads.ANY, Buttons.B  , "Show"   )
        padButtons.addButton(Gamepads.ANY, Buttons.LB , "Enlarge")
        padButtons.addButton(Gamepads.ANY, Buttons.RB , "Reduce" )
        mouseButtons = MouseButton()
        mouseButtons.addButton(Buttons.MOUSE_LEFT , "RotateLeft" )
        mouseButtons.addButton(Buttons.MOUSE_RIGHT, "RotateRight")
        scrShowHide = ShowHide(mySprite, padButtons, mouseButtons)
        scrShowHide.setPriority(10)
        # add components to entity
        mainCharacter.addComponent(mySprite)
        mainCharacter.addComponent(padButtons)
        mainCharacter.addComponent(mouseButtons)
        mainCharacter.addComponent(scrShowHide)
        # add entity to scene
        self.addEntity(mainCharacter)

        # ----------------------------------------------
        # Other Gfx components
        # ----------------------------------------------
        NX = 70
        NY = 35
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
            x = (i %  NX) * (1920//NX)
            y = (i // NX) * (1080//NY)
            mySprite.setX(x)
            mySprite.setY(y)
            mySprite.setZIndex(i+100)
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

            # -------------------------------------
            # Add input components to move all the sprites
            keyboard = Keyboard()
            if i%2 == 1:
                keyboard.addKey(keys.UP, "moveUp")
                keyboard.addKey(keys.DOWN, "moveDown")
                scrMove = MoveCircle(mySprite, (x,y), radius, speed, keyboard)
            else:
                keyboard.addKey(keys.LEFT, "moveLeft")
                keyboard.addKey(keys.RIGHT, "moveRight")
                scrMove = MoveSquare(mySprite, (x, y), radius, speed, keyboard)

            # -------------------------------------
            # Add all components into entity
            entity.addComponent(mySprite)
            entity.addComponent(keyboard)
            entity.addComponent(scrMove)

            # -------------------------------------
            # Add entity to the Scene (containing both components)
            self.addEntity(entity)

