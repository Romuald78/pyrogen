from ..components.component  import Component
from ..systems.gfx_system    import GfxSystem
from ..systems.script_system import ScriptSystem


class World():

    # Constructor
    def __init__(self):
        # store the system references
        self._gfxSys = GfxSystem()
        self._scrSys = ScriptSystem()
        pass

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
        else:
            raise RuntimeError("[ERROR] Cannot add the component in any system !")

    def unregisterComponent(self, ref):
        print(f"Unregistering a component : {ref} is not IMPLEMENTED YET !!!")
        pass

    def notifyChangeZ(self, ref):
        self._gfxSys.notifyChangeZ(ref)


    # Events
    def keyboardEvent(self, keyID, isPressed, modifiers):
        # TODO
        pass
    def mouseButtonEvent(self, x, y, buttonID, isPressed, modifiers):
        # TODO
        pass
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
        # TODO
        pass
    def gamepadAxisEvent(self, gamepadID, axisID, analogValue):
        # TODO
        pass

