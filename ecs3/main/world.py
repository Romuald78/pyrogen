from ..components.component import Component
from ..systems.gfx_system import GfxSystem


class World():

    # Constructor
    def __init__(self):
        # store the system references
        self._gfxSys = GfxSystem()
        pass

    # Application process
    def updateSystems(self, deltaTime):
        self._gfxSys.update(deltaTime)

    def renderSystems(self):
        self._gfxSys.render()

    # Component registering
    def registerComponent(self, ref):
        ###print(f"Registering a component : {ref}")
        # Check component type
        type = ref.getType()
        if type == Component.TYPE_GFX:
            self._gfxSys.addComponent(ref)
        else:
            raise RuntimeError("[ERROR] Cannot add the component in any system !")

    def unregisterComponent(self, ref):
        print(f"Unregistering a component : {ref}")

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

