
from ..components.component import Component
from ..systems.cameraSystem import CameraSystem
from ..systems.gfxSystem    import GfxSystem
from ..systems.idleSystem   import IdleSystem
from ..systems.inputSystem  import InputSystem
from ..systems.lightSystem  import LightSystem
from ..systems.physicSystem import PhysicSystem
from ..systems.scriptSystem import ScriptSystem
from ..systems.musicSystem  import MusicSystem




class World():

    ## -------------------------------------
    ## CONSTRUCTOR
    ## -------------------------------------
    def __init__(self, scn, W, H):
        # attach scene to this world
        self._scene = scn
        # Create systems
        self._inputMgr  = InputSystem()
        self._gfxMgr    = GfxSystem()
        self._scriptMgr = ScriptSystem()
        self._idleMgr   = IdleSystem()
        self._phyMgr    = PhysicSystem()
        self._lightMgr  = LightSystem(W,H)
        self._sfxMgr    = MusicSystem()
        self._cameraMgr = CameraSystem(scn)


    ## -------------------------------------
    ## COMPONENT REGISTRATION
    ## -------------------------------------
    def _registerComponent(self, compRef):
        # Retrieve component type and check before registering to systems
        compType = compRef.getType()
        # SCRIPT component
        if compType == Component.TYPE_SCRIPT:
            self._scriptMgr.add(compRef)
        # INPUT KEYBOARD component
        elif compType == Component.TYPE_KEYBOARD:
            key    = compRef.getKey()
            action = compRef.getActionName()
            self._inputMgr.registerKey(key, action, compRef)
        # INPUT GAMEPAD BUTTON component
        elif compType == Component.TYPE_GAMEPAD_BUTTON:
            ctrlID = compRef.getGamepadID()
            button = compRef.getButton()
            action = compRef.getActionName()
            self._inputMgr.registerButton(ctrlID, button, action, compRef)
        # INPUT MOUSE BUTTON component
        elif compType == Component.TYPE_MOUSE_BUTTON:
            button = compRef.getButton()
            action = compRef.getActionName()
            self._inputMgr.registerClick(button, action, compRef)
        # INPUT MOUSE MOTION component
        elif compType == Component.TYPE_MOUSE_MOTION:
            action = compRef.getActionName()
            self._inputMgr.registerMouse(action, compRef)
        # INPUT GAMEPAD AXIS component
        elif compType == Component.TYPE_GAMEPAD_AXIS:
            ctrlID = compRef.getGamepadID()
            axis = compRef.getAxis()
            action = compRef.getActionName()
            self._inputMgr.registerAxis(ctrlID, axis, action, compRef)
        # GFX components
        elif (compType & Component.TYPE_GFX_MASK) == Component.TYPE_GFX_MASK:
            self._gfxMgr.registerGfx(compRef)
        # USER components
        elif compType == Component.TYPE_IDLE:
            self._idleMgr.add(compRef)
        # PHYSIC
        elif (compType & Component.TYPE_PHYSIC_MASK) == Component.TYPE_PHYSIC_MASK:
            self._phyMgr.add(compRef)
        # LIGHT
        elif (compType & Component.TYPE_LIGHT_MASK) == Component.TYPE_LIGHT_MASK:
            self._lightMgr.add(compRef)
        # MUSIC
        elif (compType & Component.TYPE_MUSIC) == Component.TYPE_MUSIC:
            self._sfxMgr.add(compRef)
        # CAMERA
        elif (compType & Component.TYPE_CAMERA) == Component.TYPE_CAMERA:
            self._cameraMgr.add(compRef)

        # TRANSFORM
        elif (compType & Component.TYPE_TRANSFORM) == Component.TYPE_TRANSFORM:
            pass

        # /!\ UNKNOWN COMPONENT TYPES /!\
        else:
            raise ValueError(f"[ERR] addEntity : unknow component type {compType} !")



    def _unregisterComponent(self,cmpRef):
        typ = cmpRef.getType()
        # Remove GFX component from the system
        if (typ & Component.TYPE_GFX_MASK) == Component.TYPE_GFX_MASK:
            self._gfxMgr.removeGfx(cmpRef)
        # Remove Scripts
        elif (typ & Component.TYPE_SCRIPT_MASK) == Component.TYPE_SCRIPT_MASK:
            self._scriptMgr.removeScript(cmpRef)
        # Remove Physic
        elif (typ & Component.TYPE_PHYSIC_MASK) == Component.TYPE_PHYSIC_MASK:
            self._phyMgr.remove(cmpRef)
        # Remove Light
        elif (typ & Component.TYPE_LIGHT_MASK) == Component.TYPE_LIGHT_MASK:
            self._lightMgr.remove(cmpRef)
        # SFX
        elif (typ & Component.TYPE_SFX_MASK) == Component.TYPE_SFX_MASK:
            self._sfxMgr.removeMusic(cmpRef)

        # /!\ UNKNOWN COMPONENT TYPES /!\
        else:
            raise ValueError(f"[ERR] _unregisterComponent : unknow component type {typ} !")



    ## -------------------------------------
    ## COMPONENT NOTIFICATIONS
    ## -------------------------------------
    def notifyAddComponent(self, cmpRef):
        self._registerComponent(cmpRef)

    def notifyRemoveComponent(self, cmpRef):
        self._unregisterComponent(cmpRef)

    def notifyUpdateVisible(self, gfxComp):
        self._gfxMgr.notifyUpdateVisible(gfxComp)

    def notifyUpdateZIndex(self, gfxComp):
        self._gfxMgr.notifyUpdateZIndex(gfxComp)


    ## -------------------------------------
    ## LIGTH MANAGEMENT
    ## -------------------------------------
    def setAmbientColor(self, newColor):
        self._lightMgr.setAmbient(newColor)


    ## -------------------------------------
    ## CAMERA MANAGEMENT
    ## -------------------------------------
    def setActiveCamera(self, newCam):
        return self._cameraMgr.setActiveCamera(newCam)


    ## -------------------------------------
    ## PHYSIC WORLD
    ## -------------------------------------
    def addCollisionHandler(self, colTyp1, colTyp2, callbacks, data):
        return self._phyMgr.addCollisionHandler(colTyp1, colTyp2, callbacks, data)


    ## -------------------------------------
    ## MAIN METHODS
    ## -------------------------------------
    def update(self, deltaTime):
        isOnPause = self._scene.isPaused()
        self._cameraMgr.update(deltaTime)
        self._phyMgr.updatePhysicEngine(deltaTime, isOnPause)
        self._scriptMgr.updateAllScripts(deltaTime, isOnPause)
        self._gfxMgr.updateAllGfx(deltaTime, isOnPause)
        self._sfxMgr.updateAllMusics(deltaTime, isOnPause)

    def draw(self):
        with self._lightMgr.getLayer():    # code line 1
            self._gfxMgr.drawAllGfx()
            if self._scene.isDrawDebug():
                self._phyMgr.drawDebug()
        self._lightMgr.draw()              # code line 2


    ## -------------------------------------
    ## INPUT NOTIFICATIONS
    ## -------------------------------------
    def onKeyEvent(self,key, isPressed):
        isOnPause = self._scene.isPaused()
        self._inputMgr.notifyKeyEvent(key, isPressed, isOnPause)

    def onMouseButtonEvent(self, buttonName, x, y, isPressed):
        isOnPause = self._scene.isPaused()
        self._inputMgr.notifyMouseButtonEvent(buttonName, x, y, isPressed,isOnPause)
    def onMouseMotionEvent(self, x, y, dx, dy):
        isOnPause = self._scene.isPaused()
        self._inputMgr.notifyMouseMotionEvent(x, y, dx, dy,isOnPause)
    def onGamepadButtonEvent(self, gamepadId, buttonName, isPressed):
        isOnPause = self._scene.isPaused()
        self._inputMgr.notifyGamepadButtonEvent(gamepadId, buttonName, isPressed,isOnPause)
    def onGamepadAxisEvent(self, gamepadId, axisName, analogValue):
        isOnPause = self._scene.isPaused()
        self._inputMgr.notifyGamepadAxisEvent(gamepadId, axisName, analogValue,isOnPause)

