from ..components.component  import Component
from ..systems.gfx_system    import GfxSystem
from ..systems.script_system import ScriptSystem
from ..systems.input_system import KeyboardSystem, GamepadSystem, MouseSystem


class World():

    # Constructor
    def __init__(self):
        # GFX
        self._gfxSys   = GfxSystem()
        # SCRIPT
        self._scrSys   = ScriptSystem()
        # INPUT
        self._keySys   = KeyboardSystem()
        self._padSys   = GamepadSystem()
        self._mouseSys = MouseSystem()


    # Application process
    def updateSystems(self, deltaTime, systemTime):
        self._gfxSys.update(deltaTime, systemTime)
        self._scrSys.updateScripts(deltaTime, systemTime)

    def renderSystems(self):
        self._gfxSys.render()


    # Component registering
    def registerComponent(self, ref):
        ###print(f"Registering a component : {ref}")
        # Check component type
        type = ref.getType()
        if type == Component.TYPE_GFX:
            self._gfxSys.addComponent(ref)
        elif type == Component.TYPE_SCRIPT:
            self._scrSys.addComponent(ref)
        elif type== Component.TYPE_KEY:
            self._keySys.addComponent(ref)
        elif type == Component.TYPE_PAD_BUTTON:
            self._padSys.addComponent(ref)
        else:
            raise RuntimeError("[ERROR] Cannot add the component in any system !")

    def unregisterComponent(self, ref):
        print(f"Unregistering a component : {ref} is not IMPLEMENTED YET !!!")
        pass


    # Specific events
    def notifyChangeZ(self, ref):
        self._gfxSys.notifyChangeZ(ref)

    def notifyChangeScriptPriority(self, ref):
        self._scrSys.notifyChangeScriptPriority(ref)


    # Input Events
    def keyboardEvent(self, keyID, isPressed, modifiers):
        self._keySys.keyboardEvent(keyID, isPressed, modifiers)

    def mouseButtonEvent(self, x, y, buttonID, isPressed, modifiers):
        self._mouseSys.mouseButtonEvent(x, y, buttonID, isPressed, modifiers)

    def mouseMotionEvent(self, x, y, dx, dy):
        # TODO
        pass

    def mouseDragEvent(self, x, y, dx, dy, buttonID, modifiers):
        # TODO
        pass

    def mouseScrollEvent(self, x, y, dx, dy):
        # TODO
        pass

    def gamepadButtonEvent(self, gamepadID, buttonID, isPressed):
        self._padSys.gamepadButtonEvent(gamepadID, buttonID, isPressed)

    def gamepadAxisEvent(self, gamepadID, axisID, analogValue):
        # TODO
        pass

