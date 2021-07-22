

class SceneSystem():

    # Constructor
    def __init__(self):
        # Create the scene dictionary (name => ref)
        self._scenes       = {}
        # Create the special scene references
        self._currentScene = None
        self._nextScene    = None

    def run(self):
        pass

    # Scene management
    def registerScene(self, name, ref):
        # Check if this scene already exists
        if name in self._scenes:
            raise RuntimeError(f"[ERROR] The scene {name} is already registered !")
        # Add scene
        self._scenes[name] = ref
        # Make a link to the scene manager
        self._scenes[name].setManager(self)
        # Select this scene if this is the first to be added
        if len(self._scenes) == 1:
            self._currentScene = ref

    def unregisterScene(self, name):
        # Check if this scenes does not exist
        if name not in self._scenes:
            raise RuntimeError(f"[ERROR] Impossible to unregister the scene {name}. It does not exist !")
        # If this scene is the current selected one, raise an error
        if self._currentScene == self._scenes[name]:
            raise RuntimeError(f"[ERROR] Impossible to unregister the scene {name}. It is currently selected !")
        # Remove the link to the scene manager
        self._scenes[name].setManager(None)
        # Forget scene
        del self._scenes[name]

    def getNbScenes(self):
        return len(self._scenes)

    # Main application process
    def updateScene(self, deltaTime):
        if self._currentScene != None:
            # TODO | in case of transitions, do not update anymore ?
            # TODO | or update both scenes ?
            self._currentScene.updateWorld(deltaTime)

    def renderScene(self):
        if self._currentScene != None:
            # TODO | handle the transitions, rendering both scenes with shader, or plain rectangle
            self._currentScene.renderWorld()

    # Scene selection
    def selectScene(self, name):
        # Check if this scenes does not exist
        if name not in self._scenes:
            raise RuntimeError(f"[ERROR] Impossible to select the scene {name}. It does not exist !")
        # If the requested name is the selected one, do nothing
        if self._scenes[name] == self._currentScene:
            return
        # Now set the parameters to perform the transition
        self._nextScene = self._scenes[name]

    # Events
    def keyboardEvent(self, keyID, isPressed, modifiers):
        self._currentScene.keyboardEvent(keyID, isPressed, modifiers)
    def mouseButtonEvent(self, x, y, buttonID, isPressed, modifiers):
        self._currentScene.mouseButtonEvent(x, y, buttonID, isPressed, modifiers)
    def mouseMotionEvent(self, x, y, dx, dy):
        self._currentScene.mouseMotionEvent(x, y, dx, dy)
    def mouseDragEvent(self, x, y, dx, dy, buttonID, modifiers):
        self._currentScene.mouseDragEvent(x, y, dx, dy, buttonID, modifiers)
    def mouseScrollEvent(self, x, y, dx, dy):
        self._currentScene.mouseScrollEvent(x, y, dx, dy)
    def gamepadButtonEvent(self, gamepadID, buttonID, isPressed):
        self._currentScene.gamepadButtonEvent(gamepadID, buttonID, isPressed)
    def gamepadAxisEvent(self, gamepadID, axisID, analogValue):
        self._currentScene.gamepadAxisEvent(gamepadID, axisID, analogValue)







