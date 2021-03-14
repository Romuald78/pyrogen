
## ============================================================
## COMPONENT INTERFACE
## ============================================================

class Component():

    #---------------------------------------------
    # TYPE VALUES
    #---------------------------------------------
    # Use of numeric values instead of calling isinstance()
    # TASK : use some patterns like visitor instead of multiple "if" ??

    # FEATURE : create a Type class and put everything about type in it 

    # Scripts
    TYPE_SCRIPT_MASK    = 0x1000
    TYPE_SCRIPT         = TYPE_SCRIPT_MASK | 0x01
    # Inputs
    TYPE_INPUT_MASK     = 0x2000
    TYPE_KEYBOARD       = TYPE_INPUT_MASK | 0x01
    TYPE_GAMEPAD_BUTTON = TYPE_INPUT_MASK | 0x02
    TYPE_MOUSE_BUTTON   = TYPE_INPUT_MASK | 0x04
    TYPE_MOUSE_MOTION   = TYPE_INPUT_MASK | 0x08
    TYPE_GAMEPAD_AXIS   = TYPE_INPUT_MASK | 0x10

    # Gfx
    SIMPLE    = 0x01
    ANIMATED  = 0x02
    UNLIMITED = 0x04
    LIMITED   = 0x08
    SINGLE    = 0x10
    LIST      = 0x20
    PARTICLES = 0x40
    TEXT      = 0x80
    MULTI     = 0x100
    TYPE_GFX_MASK       = 0x4000
    TYPE_SIMPLE_SPRITE  = TYPE_GFX_MASK | SIMPLE    | SINGLE
    TYPE_MULTI_SPRITE   = TYPE_GFX_MASK | SIMPLE    | MULTI
    TYPE_ANIM_SPRITE    = TYPE_GFX_MASK | ANIMATED  | SINGLE
    TYPE_SIMPLE_LIST    = TYPE_GFX_MASK | SIMPLE    | LIST
    TYPE_ANIM_LIST      = TYPE_GFX_MASK | ANIMATED  | LIST
    TYPE_EMITTER        = TYPE_GFX_MASK | UNLIMITED | PARTICLES
    TYPE_BURST          = TYPE_GFX_MASK | LIMITED   | PARTICLES
    TYPE_TEXT           = TYPE_GFX_MASK | TEXT
    # User defined
    TYPE_IDLE_MASK      = 0x8000
    TYPE_IDLE           = TYPE_IDLE_MASK | 0x01
    # Physic
    TYPE_PHYSIC_MASK    = 0x10000
    TYPE_PHY_COLLIDE    = TYPE_PHYSIC_MASK | 0x01
    TYPE_PHYSIC_BOX     = TYPE_PHYSIC_MASK | 0x02
    TYPE_PHYSIC_DISC    = TYPE_PHYSIC_MASK | 0x03
    # Light
    TYPE_LIGHT_MASK     = 0x20000
    TYPE_LIGHT          = TYPE_LIGHT_MASK | 0x01
    # SOUNDS
    TYPE_SFX_MASK       = 0x40000
    TYPE_SOUND          = TYPE_SFX_MASK | 0x01
    TYPE_MUSIC          = TYPE_SFX_MASK | 0x02

    # TRANSFORM
    TYPE_TRANSFORM_MASK = 0x80000
    TYPE_TRANSFORM      = TYPE_TRANSFORM_MASK | 0x01
    # CAMERA
    TYPE_CAMERA_MASK    = 0x100000
    TYPE_CAMERA         = TYPE_CAMERA_MASK | 0x01



    # User Strings
    TYPE_INFO = {
        TYPE_SCRIPT         : {"name" : "Script",
                               "color": (255,64,64)},
        TYPE_MOUSE_BUTTON   : {"name": "MouseButton",
                               "color": (80,80,255)},
        TYPE_MOUSE_MOTION   : {"name": "MouseMotion",
                               "color": (80,80,255)},
        TYPE_KEYBOARD       : {"name": "Key",
                               "color": (128,128,255)},
        TYPE_GAMEPAD_BUTTON : {"name": "GamepadButton",
                               "color": (160,160,255)},
        TYPE_GAMEPAD_AXIS   : {"name": "GamepadAxis",
                               "color": (160,160,255)},
        TYPE_SIMPLE_SPRITE  : {"name": "FixedSprite",
                               "color": (255,255,0)},
        TYPE_ANIM_SPRITE    : {"name": "AnimSprite",
                               "color": (255,255,0)},
        TYPE_SIMPLE_LIST    : {"name": "FixedSpriteList",
                               "color": (192,192,0)},
        TYPE_ANIM_LIST      : {"name": "AnimSpriteList",
                               "color": (192,192,0)},
        TYPE_EMITTER        : {"name": "Emitter",
                               "color": (255,255,64)},
        TYPE_BURST          : {"name": "Burst",
                               "color": (255,255,64)},
        TYPE_IDLE           : {"name": "User",
                               "color": (192,192,192)},
        TYPE_PHY_COLLIDE    : {"name": "PhyCollide",
                               "color": (192, 64, 192)},
        TYPE_PHYSIC_BOX     : {"name": "PhysicBox",
                               "color": (192, 64, 192)},
        TYPE_PHYSIC_DISC    : {"name": "PhysicDisc",
                               "color": (192, 64, 192)},
        TYPE_TEXT           : {"name": "GfxText",
                               "color": (255, 255, 255)},
        TYPE_LIGHT          : {"name": "Light",
                               "color": (255, 255, 0)},
        TYPE_SOUND          : {"name": "Music",
                               "color": (0, 255, 255)},
        TYPE_MUSIC          : {"name": "Music",
                               "color": (0, 255, 255)},
        TYPE_TRANSFORM      : {"name": "Transform",
                               "color": (255, 255, 255)},
        TYPE_CAMERA         : {"name": "Camera",
                               "color": (255, 255, 255)},
    }


    #---------------------------------------------
    # COMPONENT ID
    #---------------------------------------------
    # Static field
    _maxCompID = 0
    @staticmethod
    def getNewID():
        Component._maxCompID += 1
        return Component._maxCompID


    #---------------------------------------------
    # CONSTRUCTOR
    #---------------------------------------------
    def __init__(self, compName):
        self._ID = Component.getNewID()
        if compName == None:
            compName = "COMP"
        self._name      = compName
        self._debugName = f"c_{compName}_{self._ID}"
        # By default this component is disabled when the
        # scene is on pause; That means NO UPDATE (scripts or animated sprites)
        self.execOnPause = False
        # By default this script is enabled
        self.isActive = True
        # owner entity
        self._entity = None


    #---------------------------------------------
    # ENTITY LINK
    #---------------------------------------------
    def linkToEntity(self, entRef):
        self._entity = entRef
    def getEntity(self):
        return self._entity
    def destroy(self):
        # notify entity that this component must be removed
        if self._entity == None:
            raise ValueError("[ERR] component destroy request : no entity linked !")
        self._entity.removeComponent(self)


    #---------------------------------------------
    # COMPONENT INFORMATION
    #---------------------------------------------
    # Name
    def getName(self):
        return self._name
    def getDebugName(self):
        return self._debugName
    # Unique ID
    def getID(self):
        return self._ID
    # Type (getType must be overridden by sub classes)
    def getType(self):
        raise ValueError("[ERR] Component getType() method has not been implemented yet !")
    def getTypeName(self):
        t = self.getType()
        s = Component.TYPE_INFO[t]["name"]
        return s
    def getTypeColor(self):
        t = self.getType()
        c = Component.TYPE_INFO[t]["color"]
        return c


    #---------------------------------------------
    # PAUSE BEHAVIOR
    #---------------------------------------------
    # On Pause behavior
    def enableOnPause(self):
        self.execOnPause = True
    def disableOnPause(self):
        self.execOnPause = False
    def isEnabledOnPause(self):
        return self.execOnPause
    def isDisabledOnPause(self):
        return not self.execOnPause


    #---------------------------------------------
    # EXECUTION BEHAVIOR
    #---------------------------------------------
    def enable(self):
        self.isActive = True
    def disable(self):
        self.isActive = False
    def isEnabled(self):
        return self.isActive
    def isDisabled(self):
        return not self.isActive


