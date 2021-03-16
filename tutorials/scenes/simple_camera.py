# Import Paul Craven's arcade package
import arcade
# Import Romuald Grignon's pyrogen package
# (may be loaded from the "development branch" or the standard package build
try:
    import pyrogen.src.pyrogen as pyrogen
except ImportError:
    import pyrogen
# Import pyrogen components (needed in the current scene)
from ..components.moveCharacter import KeyboardMoveGfx



# pyrogen Scene class
class SimpleCamera(pyrogen.Scene):

    def __init__(self, sceneMgr, sceneName):
        # Init parent class
        super().__init__(sceneMgr, 960, 540, sceneName)
        # Set debug mode
        self.setDebugMode(False, False, False)

    def init(self, params):

        # ----------------------------------------------
        # CHARACTER
        # ----------------------------------------------
        # Create Entity
        character = pyrogen.Entity("Char")

        # Create animated gfx
        params = {
            "filePath": f"resources/images/character01.png",
            "animName" : "walk",
            "facingDirection" : 0,
            "size": (128, 128),
            "position": (480, 270),
            "textureName": f"character01",
            "spriteBox": (3, 4, 32, 32),
            "startIndex": 0,
            "endIndex": 2,
            "frameDuration": 1 / 5,
            "counter": 0,
            "backAndForth": True,
        }
        gfx = pyrogen.GfxAnimatedSprite(1, params)
        # Keyboard components (arrows)
        keyL = pyrogen.Keyboard("moveLeft", arcade.key.LEFT )
        keyR = pyrogen.Keyboard("moveLeft", arcade.key.RIGHT)
        keyU = pyrogen.Keyboard("moveLeft", arcade.key.UP   )
        keyD = pyrogen.Keyboard("moveLeft", arcade.key.DOWN )
        # Move script
        moveChar = KeyboardMoveGfx(gfx, keyL, keyR, keyU, keyD, 10)
        # Add components to entities
        character.addComponent(gfx)
        character.addComponent(keyL)
        character.addComponent(keyR)
        character.addComponent(keyU)
        character.addComponent(keyD)
        character.addComponent(moveChar)
        # Add entity to the current scene
        self.addEntity(character)

        # ----------------------------------------------
        # CAMERA
        # ----------------------------------------------
        # Create Entity
        camera = pyrogen.Entity("Cam")
        # Create camera
        cam = pyrogen.Camera( (480,270), (960,540) )
        # Add components to entities
        camera.addComponent(cam)
        # Add entity to the current scene
        self.addEntity(camera)
