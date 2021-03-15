# FEATURE : Merge gfx classes
# put a single Sprite in a 1-size-spriteList
# to be more generic ? We would only have GfxSpriteList
# that would be easier to handle in GfxSystem class. let's see
# Also merge emitters if possible (position management, etc...)

# FEATURE : add a GfxFont component
# > use the olf script that generates png file from a .ttf file
# this script generates the JAVA file with all the font map
# just adapt this script to generate map for Python ;-)
# > then creates the component that will generate one sprite
# from both map file and png file
# add some fields like H/V alignment (left, center, ...)
# position must be related to this anchor point
# add some methods to get width heigth, etc...
# This component will be more efficient with static messages
# in order not to regenerate the Sprite List and lose some time
# to be continued ...



## ============================================================
## IMPORTS
## ============================================================
from ..arcadeRGR.spriteRGR import AnimatedSprite
from .component import Component


## ============================================================
## GFX UPPER CLASS
## ============================================================
class Gfx(Component):

    # constructor
    def __init__(self, compName=None):
        if compName==None:
            compName = "GFX"
        super().__init__(compName)
        self._zIndex    = 0
        self._arcadeGfx = None
        self._gfxType   = None
        self._visible   = True

    # Remove the reference to the arcade gfx element
    def kill(self):
        raise ValueError("[ERR] gfx : kill method has not been implemented yet !")

    def getGfx(self):
        return self._arcadeGfx

    # type method
    def getType(self):
        if self._gfxType == None:
            raise ValueError("[ERR] gfx : gfxType reference has not been set yet !")
        return self._gfxType

    # Z-Index
    def setZIndex(self, newZ):
        self._zIndex = newZ
        ent = self.getEntity()
        if ent != None:
            scn = ent.getScene()
            if scn != None:
                scn.notifyUpdateZIndex(self)

    def getZIndex(self):
        return self._zIndex
    # Visible (set the component field + notify Gfx Manager in order to update the draw list

    def show(self):
        self._visible = True
        ent = self.getEntity()
        if ent != None:
            scn = ent.getScene()
            if scn != None:
                scn.notifyUpdateVisible(self)

    def hide(self):
        self._visible = False
        ent = self.getEntity()
        if ent != None:
            scn = ent.getScene()
            if scn != None:
                scn.notifyUpdateVisible(self)

    def isVisible(self):
        return self._visible



## ============================================================
## GFX COMPONENTS
## ============================================================



#-----------------------------------
class GfxOneSPrite(Gfx):

    # Constructor
    def __init__(self, compName=None):
        if compName == None:
            compName = "1SPRITE"
        # call to parent constructor
        super().__init__(compName)

    # Position
    def move(self, dx, dy):
        self._arcadeGfx.center_x += dx
        self._arcadeGfx.center_y += dy
    def setPosition(self, newPos):
        self._arcadeGfx.center_x = newPos[0]
        self._arcadeGfx.center_y = newPos[1]
    def getPosition(self):
        return (self._arcadeGfx.center_x, self._arcadeGfx.center_y)

    # Orientation
    # QUESTION : is there a problem not to be in a specific range like [0-360] or [-180-180] ?
    # FEATURE  : improve methods to handle pivot points
    def rotate(self, offset, multiplier=1.0, pivotPos=None):
        self._arcadeGfx.angle *= multiplier
        self._arcadeGfx.angle += offset
    def setAngle(self, newAngle, pivotPos=None):
        self._arcadeGfx.angle = newAngle
    def getAngle(self):
        return self._arcadeGfx.angle

    # Dimensions
    def getWidth(self):
        return self._arcadeGfx.width
    def getHeight(self):
        return self._arcadeGfx.height

    # Scale
    def setScale(self, newScale):
        self._arcadeGfx.scale = newScale
    def getScale(self):
        return self._arcadeGfx.scale

    # Kill method
    def kill(self):
        self._arcadeGfx.kill()
        self._arcadeGfx = None


#-----------------------------------
class GfxText(GfxOneSPrite):

    # Constructor
    def __init__(self, params, zIdx=0, compName=None):
        if compName == None:
            compName = "textGfx"
        # call to parent constructor
        super().__init__(compName)
        # set type
        self._gfxType   = Component.TYPE_TEXT
        # create Gfx element
        self._params = params
        self._zIndex    = zIdx
        self._arcadeGfx = drawText(params)


    def setMessage(self, newStr):
        self._params["message"] = newStr
        self._arcadeGfx = drawText(self._params)

    # Kill method
    def kill(self):
        self._arcadeGfx.kill()
        self._arcadeGfx = None


#-----------------------------------
class GfxSimpleSprite(GfxOneSPrite):

    # Constructor
    def __init__(self, params, zIdx=0, compName=None):
        if compName == None:
            compName = "FixedSPrite"
        # call to parent constructor
        super().__init__(compName)
        # set type
        self._gfxType   = Component.TYPE_SIMPLE_SPRITE
        # create Gfx element
        self._arcadeGfx = createSimpleSprite(params)
        self._zIndex    = zIdx



#-----------------------------------
class GfxAnimatedSprite(GfxOneSPrite):

    # Constructor
    def __init__(self, nbStates=1, params=None, zIdx=0, compName=None):
        if compName == None:
            compName = "AnimSPrite"
        # call to parent constructor
        super().__init__(compName)
        # set type
        self._gfxType  = Component.TYPE_ANIM_SPRITE
        # create Gfx element
        self._arcadeGfx = AnimatedSprite(nbStates)
        # Add first animation if given
        if params != None:
            self.addAnimation(params, True, True)
        # Set ZIndex
        self._zIndex    = zIdx

    def addAnimation(self, params, changePosition=False, changeScale=False):
        # retrieve parameters
        filePath       = params["filePath"]
        animName       = "defaultName" if "animName" not in params else params["animName"]
        size           = None if "size" not in params else params["size"]
        filterColor    = (255, 255, 255, 255) if "filterColor" not in params else params["filterColor"]
        isMaxRatio     = False if "isMaxRatio" not in params else params["isMaxRatio"]
        position       = (0, 0) if "position" not in params else params["position"]
        spriteBox      = params["spriteBox"]
        startIndex     = params["startIndex"]
        endIndex       = params["endIndex"]
        frameduration  = 1 / 60 if "frameDuration" not in params else params["frameDuration"]
        flipH          = False if "flipH" not in params else params["flipH"]
        flipV          = False if "flipv" not in params else params["flipV"]
        counter        = 0 if "counter" not in params else params["counter"]
        backAndForth   = False if "backAndForth" not in params else params["backAndForth"]
        facingDirection= 0 if "facingDirection" not in params else params["facingDirection"]
        # Add first animation
        self._arcadeGfx.add_animation(animName, filePath,
                                      spriteBox[0], spriteBox[1],
                                      spriteBox[2],spriteBox[3],
                                      startIndex, endIndex,
                                      frameduration,
                                      flipH, flipV,
                                      counter, backAndForth,
                                      filterColor,
                                      facingDirection
                                      )
        # Set scale
        if changeScale:
            if size != None:
                if isMaxRatio:
                    ratio = max(size[0] / self._arcadeGfx.width, size[1] / self._arcadeGfx.height)
                else:
                    ratio = min(size[0] / self._arcadeGfx.width, size[1] / self._arcadeGfx.height)
                self._arcadeGfx.scale = ratio
        # Set position
        if changePosition:
            self._arcadeGfx.center_x = position[0]
            self._arcadeGfx.center_y = position[1]

    def selectFrame(self,index):
        self._arcadeGfx.select_frame(index)

    def selectAnimation(self, animName, rewind=False, resume=True):
        self._arcadeGfx.select_animation(animName, rewind, resume)

    def selectState(self, state, rewind=False, resume=True):
        self._arcadeGfx.select_state(state, rewind, resume)


    def getCurrentAnimation(self):
        return self._arcadeGfx.get_current_animation()

    def isFinished(self):
        return self._arcadeGfx.is_finished()

    def pause(self):
        self._arcadeGfx.pause_animation()


#-----------------------------------
class GfxMultiSprite(GfxAnimatedSprite):

    # Constructor
    def __init__(self, params, zIdx=0, compName=None):
        if compName == None:
            compName = "AnimSPrite"
        # call to parent constructor
        super().__init__(params, zIdx, compName)

    def setTexture(self, index):
        self._arcadeGfx.select_frame(index)



#-----------------------------------
class GfxAnimSpriteList(Gfx):

    # Constructor
    def __init__(self, zIdx=0, compName=None):
        if compName == None:
            compName = "SPRITELIST"
        # call to parent constructor
        super().__init__(compName)
        # set type
        self._gfxType = Component.TYPE_ANIM_LIST
        # Gfx Comps
        self._arcadeGfx = arcade.SpriteList()
        self._gfxs = []
        # Store zIndex
        self._zIndex = zIdx

    # Filling
    # TODO : when adding components, for the moment, it does not take care about Z-Index
    # Improvement would be to have a local list here with zIndex in order
    # to add components one by one without knowing their order
    # in fact if we change the zIndex of a comp in the list,
    # it won't change the z for the drawing part : take care !
    def addSprite(self, spriteComp):
        # the added component is so not visible as part of the sprite list
        # it is not visible from the Gfx System point of view
        # but the whole sprite list will be
        spriteComp.hide()
        # Add it to the list
        if spriteComp in self._gfxs:
            raise ValueError("[ERR] sprite Component already in the Sprite list !")
        self._gfxs.append(spriteComp)
        # Add the arcade sprite into the arcade sprite list
        arcSpr = spriteComp.getGfx()
        self._arcadeGfx.append(arcSpr)
        # TODO notify to the scene ?

    # Removing
    def removeSprite(self, spriteComp):
        # Remove from comp list
        if spriteComp not in  self._gfxs:
            raise ValueError("[ERR] sprite comp not the in sprite list !")
        self._gfxs.remove(spriteComp)
        # Remove from arcade sprite list
        arcSpr = spriteComp.getGfx()
        self._arcadeGfx.remove(arcSpr)

    # Position
    def move(self, dx, dy):
        for gfx in self._arcadeGfx:
            gfx.center_x += dx
            gfx.center_y += dy

    # Orientation
    def rotate(self, offset, mult=1, pivotPos=None):
        for gfx in self._arcadeGfx:
            gfx.angle *= mult
            gfx.angle += offset

    # List management
    def size(self):
        return len(self._arcadeGfx)
    def getSprite(self,index):
        return self._arcadeGfx[index]

    # Kill method
    def kill(self):
        self._arcadeGfx = None


#-----------------------------------
class GfxSimpleEmitter(Gfx):

    def __init__(self, params, zIdx=0, compName=None):
        if compName == None:
            compName = "Emitter"
        # call to parent constructor
        super().__init__(compName)
        # set type
        self._gfxType   = Component.TYPE_EMITTER
        # create Gfx element
        self._arcadeGfx = createParticleEmitter(params)
        self._zIndex    = zIdx

    # position
    def move(self, dx, dy):
        self._arcadeGfx.center_x += dx
        self._arcadeGfx.center_y += dy
    def setPosition(self, newPos):
        self._arcadeGfx.center_x = newPos[0]
        self._arcadeGfx.center_y = newPos[1]
    def getPosition(self):
        return (self._arcadeGfx.center_x, self._arcadeGfx.center_y)

    # Kill method
    def kill(self):
        self._arcadeGfx = None


#-----------------------------------
class GfxBurstEmitter(Gfx):

    def __init__(self, params, zIdx=0, compName=None):
        if compName == None:
            compName = "Burst"
        # call to parent constructor
        super().__init__(compName)
        # set type
        self._gfxType   = Component.TYPE_BURST
        # create Gfx element
        self._arcadeGfx = createParticleBurst(params)
        self._zIndex    = zIdx

    # position
    def move(self, dx, dy):
        self._arcadeGfx.center_x += dx
        self._arcadeGfx.center_y += dy
    def setPosition(self, newPos):
        self._arcadeGfx.center_x = newPos[0]
        self._arcadeGfx.center_y = newPos[1]
    def getPosition(self):
        if self._arcadeGfx != None:
            return (self._arcadeGfx.center_x, self._arcadeGfx.center_y)
        return (-10000,-10000)

    # process
    def isFinished(self):
        return self._arcadeGfx.can_reap()
    def isRunning(self):
        return not self.isFinished()

    # Kill method
    def kill(self):
        self._arcadeGfx = None
