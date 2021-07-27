from .world import World


class Scene():

    # ========================================================
    # Constructor
    # ========================================================
    def __init__(self):
        # Create a world entity
        self._world = World()
        # Init scene manager ref
        self._scnMgr = None
        # Entity list
        self._entitiesByName = {}
        self._entitiesByRef  = []
        # System time for this scene
        self._systemTime = 0

    # ========================================================
    # Application process
    # ========================================================
    def setManager(self, ref):
        self._scnMgr = ref

    def updateWorld(self, deltaTime):
        self._systemTime += deltaTime
        self._world.updateSystems(deltaTime, self._systemTime)

    def renderWorld(self):
        self._world.renderSystems()

    # ========================================================
    # Scene management
    # ========================================================
    def registerScene(self, name, ref):
        self._scnMgr.registerScene(name, ref)

    def unregisterScene(self, name):
        self._scnMgr.unregisterScene(name)

    def selectScene(self, name):
        self._scnMgr.selectScene(name)

    # ========================================================
    # Entity management
    # ========================================================
    def addEntity(self, ref):
        # Check if we can add the entity
        if ref in self._entitiesByRef:
            raise RuntimeError(f"[ERROR] Cannot add entity {ref} into the scene {self} !")
        # Add the entity
        self._entitiesByRef.append(ref)
        self._entitiesByName[ref.getName()] = ref
        # Create the link between scene and entity
        ref.setScene(self)

    def removeEntity(self, ref):
        # Check if we can add the entity
        if ref not in self._entitiesByRef:
            raise RuntimeError(f"[ERROR] Cannot remove entity {ref} from the scene {self} !")
        # Remove the link between the entoty and the current scene
        ref.resetScene(self)
        # Remove the entity
        self._entitiesByRef.remove(ref)
        del self._entitiesByName[ref.getName()]

    def getNbEntities(self):
        return len(self._entitiesByRef)

    # ========================================================
    # Component management
    # ========================================================
    def registerComponent(self, ref):
        self._world.registerComponent(ref)

    def unregisterComponent(self, ref):
        self._world.unregisterComponent(ref)


    # ========================================================
    # Specific events
    # ========================================================
    def notifyChangeZ(self, ref):
        self._world.notifyChangeZ(ref)

    def notifyChangeScriptPriority(self, ref):
        self._world.notifyChangeScriptPriority(ref)


    # ========================================================
    # Events
    # ========================================================
    def keyboardEvent(self, keyID, isPressed, modifiers):
        self._world.keyboardEvent(keyID, isPressed, modifiers)

    def mouseButtonEvent(self, x, y, buttonID, isPressed, modifiers):
        self._world.mouseButtonEvent(x, y, buttonID, isPressed, modifiers)

    def mouseMotionEvent(self, x, y, dx, dy):
        self._world.mouseMotionEvent(x, y, dx, dy)

    def mouseDragEvent(self, x, y, dx, dy, buttonID, modifiers):
        self._world.mouseDragEvent(x, y, dx, dy, buttonID, modifiers)

    def mouseScrollEvent(self, x, y, dx, dy):
        self._world.mouseScrollEvent(x, y, dx, dy)

    def gamepadButtonEvent(self, gamepadID, buttonID, isPressed):
        self._world.gamepadButtonEvent(gamepadID, buttonID, isPressed)

    def gamepadAxisEvent(self, gamepadID, axisID, analogValue):
        self._world.gamepadAxisEvent(gamepadID, axisID, analogValue)
