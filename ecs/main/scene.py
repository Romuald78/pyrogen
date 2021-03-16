

## ============================================================
## IMPORTS
## ============================================================
import arcade

from .loader import ResourceLoader
from .world import World



## ============================================================
## SCENE class (extended by the user scenes)
## ============================================================
class Scene():

    # ---------------------------------------------
    # COMPONENT ID
    # ---------------------------------------------
    # Static field
    _maxSceneID = 0
    @staticmethod
    def _getNewID():
        Scene._maxSceneID += 1
        return Scene._maxSceneID


    ## -------------------------------------
    ## CONSTRUCTOR
    ## -------------------------------------
    def __init__(self, scnMgr, W, H, sceneName):
        self._sceneMgr     = scnMgr
        self._world        = World(self, W, H)
        self._consoleDebug = False
        self._drawDebug    = False
        self._drawMemory   = False
        self._dimensions   = (W,H)
        self._ID           = Scene._getNewID()
        self._name         = sceneName
        self._debugName    = f"s_{sceneName}_{self._ID}"
        # prepare entity dict
        self._entByName = {}
        self._entByRef  = {}

    def init(self, params):
        pass


    ## -------------------------------------
    ## SCENE INFORMATION
    ## -------------------------------------
    def getApplication(self):
        return self._sceneMgr.getApplication()
    def getName(self):
        return self._name
    def getDebugName(self):
        return self._debugName
    def getID(self):
        return self._ID


    ## -------------------------------------
    ## SCENE MANAGEMENT
    ## -------------------------------------
    def selectNewScene(self, name, params=None):
        self._sceneMgr.selectNewScene(name, params)
    def pause(self):
        self._sceneMgr.pause()
    def resume(self):
        self._sceneMgr.resume()
    def isPaused(self):
        return self._sceneMgr.isPaused()
    def setAmbientColor(self, newColor):
        self._world.setAmbientColor(newColor)


    ## -------------------------------------
    ## ENTITY MANAGEMENT
    ## -------------------------------------
    def addEntity(self,entRef):
        # link the entity to this scene
        entRef.linkToScene(self)
        # retrieve entity name
        entName = entRef.getName()
        # Store entity by Name
        if not entName in self._entByName:
            self._entByName[entName] = []
        if entRef in self._entByName[entName]:
            raise ValueError("[ERR] addEntity : reference is already in the name dict !")
        self._entByName[entName].append(entRef)
        # Store entity by ref
        if entRef in self._entByRef:
            raise ValueError("[ERR] addEntity : reference is already in the ref dict !")
        self._entByRef[entRef] = entName
        # Get all components from entity (dict by ref)
        comps = entRef.getComponentList()
        for compRef in comps:
            # Register this component to the world
            self._world.notifyAddComponent(compRef)

    def removeEntity(self, entRef):
        # Remove all components
        for compRef in entRef.getComponentList():
            compRef.destroy()
        # prepare empty names to remove
        emptyNames = []
        # remove from name dict
        for entName in self._entByName:
            if entRef in self._entByName[entName]:
                self._entByName[entName].remove(entRef)
                if len(self._entByName[entName]) == 0:
                    emptyNames.append(entName)
        # Clean empty names
        for nam in emptyNames:
            del self._entByName[nam]
        # remove from ref dict
        if entRef in self._entByRef:
            del self._entByRef[entRef]
        # Actually at this stage,  the entity is not in the world list
        # and all its components have bee removed from the different
        # systems too.
        # The whole package entity+components is not in the memory anymore

    def getNbEntities(self):
        return len(self._entByRef)

    def getEntitiesByName(self,entName):
        res = []
        if entName in self._entByName:
            res = self._entByName[entName]
        return res

    def hasEntity(self, entRef):
        return entRef in self._entByRef

    def getAllEntities(self):
        return list(self._entByRef.keys())


    ## -------------------------------------
    ## MAIN METHODS
    ## -------------------------------------
    def update(self, deltaTime):
        self._world.update(deltaTime)
    def draw(self):
        self._world.draw()


    ## -------------------------------------
    ## COMPONENT NOTIFICATIONS
    ## -------------------------------------
    def notifyAddComponent(self, newCmpRef):
        self._world.notifyAddComponent(newCmpRef)
    def notifyRemoveComponent(self, cmpRef):
        self._world.notifyRemoveComponent(cmpRef)


    ## -------------------------------------
    ## GFX DISPLAY NOTIFICATIONS
    ## -------------------------------------
    def notifyUpdateVisible(self, gfxComp):
        self._world.notifyUpdateVisible(gfxComp)
    def notifyUpdateZIndex(self, gfxComp):
        self._world.notifyUpdateZIndex(gfxComp)


    ## -------------------------------------
    ## PHYSIC WORLD
    ## -------------------------------------
    def addCollisionHandler(self, colType1, colType2, callbacks, data):
        self._world.addCollisionHandler(colType1, colType2, callbacks, data)


    ## -------------------------------------
    ## CAMERAS
    ## -------------------------------------
    def setActiveCamera(self, newCam):
        return self._world.setActiveCamera(newCam)


    ## -------------------------------------
    ## INPUT NOTIFICATIONS
    ## -------------------------------------
    def onKeyEvent(self,key, isPressed):
        self._world.onKeyEvent(key, isPressed)
    def onMouseButtonEvent(self, buttonName, x, y, isPressed):
        self._world.onMouseButtonEvent(buttonName, x, y, isPressed)
    def onMouseMotionEvent(self, x, y, dx, dy):
        self._world.onMouseMotionEvent(x, y, dx, dy)
    def onGamepadButtonEvent(self, gamepadId, buttonName, isPressed):
        self._world.onGamepadButtonEvent(gamepadId, buttonName, isPressed)
    def onGamepadAxisEvent(self, gamepadId, axisName, analogValue):
        self._world.onGamepadAxisEvent(gamepadId, axisName, analogValue)


    ## -------------------------------------
    ## DEBUG
    ## -------------------------------------
    def getDimensions(self):
        return self._dimensions
    def isConsoleDebug(self):
        return self._consoleDebug
    def isDrawDebug(self):
        return self._drawDebug
    def setDebugMode(self, consoleDebug, drawDebug, drawMem):
        self._consoleDebug = consoleDebug
        self._drawDebug    = drawDebug
        self._drawMemory   = drawMem
    def displayDebugInfo(self):
        if self._consoleDebug:
            msg = "[INFO] Your scene has no implementation of 'displayDebugInfo' method !"
            print(msg)
    def drawDebugInfo(self):
        if self._drawDebug:
            # arcade.draw_rectangle_filled(self._dimensions[0]//2, self._dimensions[1]//2, self._dimensions[0], self._dimensions[1],(128,128,128,128))
            refX = 15
            refY = self._dimensions[1] - 20
            # Scene information
            a = ["[_]", "[o]"][not self.isPaused()]
            msg = f"{a} {self.getDebugName()}"
            arcade.draw_text(msg, refX, refY, (255,255,255), 14)
            # Scene entities
            entities = self.getAllEntities()
            for ent in entities:
                refY -= 18
                arcade.draw_text(ent.getDebugName(), refX+15, refY, (64, 255, 64), 14)
                components = ent.getComponentList()
                for comp in components:
                    refY -= 18
                    n = comp.getDebugName()
                    s = comp.getTypeName()
                    c = comp.getTypeColor()
                    a = ["[_]", "[o]"][comp.isEnabled() and (not self.isPaused() or comp.isEnabledOnPause())]
                    msg = f"{a} {n} ({s})"
                    arcade.draw_text(msg, refX + 30, refY, c, 12)

        if self._drawMemory:
            # Memory consumption
            gfxMem = self._world._gfxMgr.getMemoryInfo()
            scrMem = self._world._scriptMgr.getMemoryInfo()
            ldrMem = ResourceLoader.getMemoryInfo()
            mems = [gfxMem, scrMem, ldrMem]
            refX = 20
            refY = 300
            for mem in mems:
                refY += 15*(len(mem)+1)
                dY = 15
                for entry in mem:
                    value = mem[entry]
                    arcade.draw_text(f"{entry}:{value}", refX, refY+dY, (255, 255, 255), 12)
                    dY -= 15


    ## -------------------------------------
    ## TRANSITION MANAGEMENT
    ## -------------------------------------
    def getTransitionTimeIN(self):
        return 1
    def getTransitionTimeOUT(self):
        return 1
    def getTransitionColorIN(self):
        return (0,255,0)
    def getTransitionColorOUT(self):
        return (255,0,0)

