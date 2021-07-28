from .base_system import BaseSystem

class KeyboardSystem(BaseSystem):

    def __init__(self):
        super().__init__()

    def keyboardEvent(self, keyID, isPressed, modifiers):
        # Update all the Script
        for c in self._compByRef:
            ID = f"K-{keyID}"
            c.notifyEvent(ID, isPressed, modifiers)
        #print(f"\n\n\nnotified {len(self._compByRef)} input components\n\n\n")

class GamepadSystem(BaseSystem):

    def __init__(self):
        super().__init__()

    def gamepadButtonEvent(self, gamepadID, buttonID, isPressed):
        print(f"Pad:{gamepadID} - button:{buttonID} - isPressed:{isPressed}")
        # Update all the Script components
        for c in self._compByRef:
            ID = f"G-{gamepadID}-{buttonID}"
            c.notifyEvent(ID, isPressed)

class MouseSystem(BaseSystem):

    def __init__(self):
        super().__init__()

    def mouseButtonEvent(self, x, y, buttonID, isPressed, modifiers):
        # Update all the Script components
        for c in self._compByRef:
            ID = f"G-{buttonID}"
            c.notifyEvent(ID, isPressed, modifiers, x, y)

