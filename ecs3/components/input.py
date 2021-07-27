from .component import Component

# ============================================================
# Storage of any action status
# ============================================================
class LogicStatus():

    def __init__(self):
        self._state       = False
        self._risingEdge  = False
        self._fallingEdge = False
        self._modifiers   = None
        self._lastX       = 0
        self._lastY       = 0

    def updateStatus(self, v, modifiers=None, x=0, y=0):
        # If there is a change
        if v != self._state:
            if v:
                self._risingEdge = True
            else:
                self._fallingEdge = True
            self._state = v
            self._modifiers = modifiers
            self._lastX = x
            self._lastY = y

    def isPressed(self):
        return self._state
    def isReleased(self):
        return not self._state
    def hasBeenPressed(self):
        res = self._risingEdge
        self._risingEdge = False
        return res
    def hasBeenReleased(self):
        res = self._fallingEdge
        self._fallingEdge = False
        return res
    def getModifiers(self):
        return self._modifiers
    def getLastX(self):
        return self._lastX
    def getLastY(self):
        return self._lastY


# ============================================================
# Management of a logic input
# ============================================================
class LogicButton(Component):

    def __init__(self, type, name="LogicButton"):
        super().__init__(type, name)
        # Contains the action names for each key id
        self._buttons    = {}
        # Contains the status for each action
        self._actions = {}

    def addAction(self, ID, actionName):
        # Create action if not already present
        if actionName not in self._actions:
            self._actions[actionName] = LogicStatus()
        # Add key
        if ID not in self._buttons:
            self._buttons[ID] = []
        # Add key-action if needed
        if actionName not in self._buttons[ID]:
            self._buttons[ID].append(actionName)

    def removeAction(self, ID, actionName):
        # TODO
        pass

    # ID : "K" + keyID for keyboard
    #      "G" + gamepadID + buttonID for gamepads
    #      "M" + buttonID for mouse
    def notifyEvent(self, ID, isPressed, modifiers, x=0, y=0):
        if ID in self._buttons:
            names = self._buttons[ID]
            for name in names:
                self._actions[name].updateStatus(isPressed, modifiers, x, y)

    def isPressed(self, actionName):
        res = False
        if actionName in self._actions:
            res = self._actions[actionName].isPressed()
        return res

    def isReleased(self, actionName):
        res = False
        if actionName in self._actions:
            res = self._actions[actionName].isReleased()
        return res

    def hasBeenPressed(self, actionName):
        res = False
        if actionName in self._actions:
            res = self._actions[actionName].hasBeenPressed()
        return res

    def hasBeenReleased(self, actionName):
        res = False
        if actionName in self._actions:
            res = self._actions[actionName].hasBeenReleased()
        return res


# ============================================================
# KEYS
# ============================================================
class Keyboard(LogicButton):

    def __init__(self, name="Keyboard"):
        super().__init__(Component.TYPE_KEY, name)

    def addKey(self, keyID, actionName):
        ID = f"K-{keyID}"
        super().addAction(ID, actionName)

    def removeKey(self, keyID, actionName):
        # TODO
        pass


# ============================================================
# GAMEPAD BUTTONS
# ============================================================
class GamepadButton(LogicButton):

    def __init__(self, name="GamepadButton"):
        super().__init__(Component.TYPE_PAD_BUTTON, name)

    def addButton(self, gamepadID, buttonID, actionName):
        ID = f"G-{gamepadID}-{buttonID}"
        super().addAction(ID, actionName)

    def removeButton(self, gamepadID, buttonID, actionName):
        # TODO
        pass


# ============================================================
# MOUSE BUTTONS
# ============================================================
class MouseButton(LogicButton):

    def __init__(self, name="GamepadButton"):
        super().__init__(Component.TYPE_PAD_BUTTON, name)

    def addButton(self, buttonID, actionName):
        ID = f"M-{buttonID}"
        super().addAction(ID, actionName)

    def removeButton(self, buttonID, actionName):
        # TODO
        pass

