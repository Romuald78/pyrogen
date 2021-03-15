# FEATURE : improve the data structure to handle inputs
# For the moment, one instance handles one event.
# Use lists/dicts in order to make one component
# handle multiple events ?
# that should solve the fact that actioName parameter
# in callbacks is not used (so does the gamepadID)

# FEATURE improve mouse management
# add fields for simple, double and triple clicks
# In order to do that, the component needs to have a list
# of events with : positions, timestamp, status
# we also need fields for duration ranges (for the pressed and released states)

# FEATURE improve mouse management
# Add a field for long press without release
# to do that, an update method must be added and must be called
# from the world. FOr this feature, the list detailed above
# would be useful to : check how long the current click
# is being pressed

# FEATURE handle "any button" feature for mouse or gamepad, or "any key" for keayboard

# FEATURE : use modifiers for key and mouse buttons (modifers would be given by Launcher)



## ============================================================
## IMPORTS
## ============================================================
from .component import Component



## ============================================================
## INPUT UPPER CLASS
## ============================================================
class Input(Component):
    # Constants
    ALL_GAMEPADS_ID = -1
    # the upper class contains the action name of the input
    def __init__(self,actionName, compName=None):
        if compName == None:
            compName = "INPUT"
        #parent constructor
        super().__init__(compName)
        self.name = actionName
    def getType(self):
        raise ValueError("[ERR] Input getType() method not implemented yet !")
    def getActionName(self):
        return self.name


## ============================================================
## LOWER CLASSES
## ============================================================

# ----------------------------------------------------------
# KEYBOARD
# ----------------------------------------------------------
class Keyboard(Input):

    # Constructor
    def __init__(self, actionName, key, compName=None):
        if compName == None:
            compName = "KEYBOARD"
        # parent constructor
        super().__init__(actionName, compName)
        # store fields
        self._keyValue    = key
        self._risingEdge  = False    # from 'released' to 'pressed'
        self._fallingEdge = False    # from 'pressed' to 'released'
        self._value       = False    # current state

    # Event information
    def isPressed(self):
        return self._value
    def hasBeenPressed(self):
        res = self._risingEdge
        self._risingEdge = False
        return res
    def hasBeenReleased(self):
        res = self._fallingEdge
        self._fallingEdge = False
        return res

    # Field getters
    def getKey(self):
        return self._keyValue

    # Override parent method
    def getType(self):
        return Component.TYPE_KEYBOARD

    # Callback
    def keyboardEvent(self, action, isPressed):
        # Store current state
        self._value = isPressed
        # Store either rising or falling edge
        if isPressed:
            self._risingEdge  = True
        else:
            self._fallingEdge = True


# ----------------------------------------------------------
# GAMEPAD BUTTON
# ----------------------------------------------------------
class GamepadButton(Input):

    # Constructor
    def __init__(self, actionName, gamepadID, buttonName, compName=None):
        if compName == None:
            compName = "G_BUTTON"
        # parent constructor
        super().__init__(actionName, compName)
        # store fields
        self._ctrlID      = gamepadID
        self._button      = buttonName
        self._risingEdge  = False    # from 'released' to 'pressed'
        self._fallingEdge = False    # from 'pressed' to 'released'
        self._value       = False    # current state
        self._lastCtrlID  = gamepadID

    # Event information
    def isPressed(self):
        return self._value
    def hasBeenPressed(self):
        res = self._risingEdge
        self._risingEdge = False
        return res
    def hasBeenReleased(self):
        res = self._fallingEdge
        self._fallingEdge = False
        return res

    # Field getters
    def getGamepadID(self):
        return self._ctrlID
    def getLastGamepadID(self):
        return self._lastCtrlID
    def getButton(self):
        return self._button

    # Override parent method
    def getType(self):
        return Component.TYPE_GAMEPAD_BUTTON

    # Callback
    def gamepadButtonEvent(self, action, gamepadId, isPressed):
        # Store current state and last gamepadID
        self._value = isPressed
        self._lastCtrlID = gamepadId
        # Store either rising or falling edge
        if isPressed:
            self._risingEdge  = True
        else:
            self._fallingEdge = True


# ----------------------------------------------------------
# MOUSE BUTTON
# ----------------------------------------------------------
class MouseButton(Input):

    # Constructor
    def __init__(self, actionName, buttonName, compName=None):
        if compName == None:
            compName = "M_BUTTON"
        # parent constructor
        super().__init__(actionName, compName)
        # store fields
        self._button         = buttonName
        self._risingEdge     = False  # from 'released' to 'pressed'
        self._fallingEdge    = False  # from 'pressed' to 'released'
        self._value          = False  # current state
        self._lastPosition   = (-1, -1)
        self._lastRisingPos  = (-1, -1)
        self._lastFallingPos = (-1, -1)

    # Event information
    def isPressed(self):
        return self._value
    def hasBeenPressed(self):
        res = self._risingEdge
        self._risingEdge = False
        return res
    def hasBeenReleased(self):
        res = self._fallingEdge
        self._fallingEdge = False
        return res

    def getLastPosition(self):
        return self._lastPosition
    def getPressedPosition(self):
        return self._lastRisingPos
    def getReleasedPosition(self):
        return self._lastFallingPos

    # Field getters
    def getButton(self):
        return self._button

    # Override parent method
    def getType(self):
        return Component.TYPE_MOUSE_BUTTON

    # Callback
    def mouseButtonEvent(self, action, x, y, isPressed):
        # Store current state
        self._value        = isPressed
        self._lastPosition = (x, y)
        # Store either rising or falling edge
        if isPressed:
            self._risingEdge    = True
            self._lastRisingPos = (x, y)
        else:
            self._fallingEdge    = True
            self._lastFallingPos = (x, y)


# ----------------------------------------------------------
# MOUSE MOTION
# ----------------------------------------------------------
class MouseMotion(Input):

    # Constructor
    def __init__(self, actionName, compName=None):
        if compName == None:
            compName = "M_MOTION"
        # parent constructor
        super().__init__(actionName, compName)
        # store fields
        self._lastPosition = (-1, -1)
        self._lastVector   = (0, 0)

    # Event information
    def getLastPosition(self):
        return self._lastPosition
    def getLastVector(self):
        # Reset vector after reading
        res = self._lastVector
        self._lastVector = (0, 0)
        return res

    # Override parent method
    def getType(self):
        return Component.TYPE_MOUSE_MOTION

    # Callback
    def mouseMotionEvent(self, action, x, y, dx, dy):
        self._lastPosition = (x, y)
        self._lastVector   = (dx, dy)


# ----------------------------------------------------------
# GAMEPAD AXIS
# ----------------------------------------------------------
class GamepadAxis(Input):

    # Constructor
    def __init__(self, actionName, gamepadID, axisName, deadZone=0.2, compName=None):
        if compName == None:
            compName = "AXIS"
        # parent constructor
        super().__init__(actionName, compName)
        # store fields
        self._ctrlID    = gamepadID
        self._axis      = axisName
        self._dead      = deadZone
        self._value     = 0
        self._minValue  = -0.5        # used to normalize the output
        self._maxValue  =  0.5        # used to normalize the output
        self._lastValue = 1.0

    # Event information
    def getValue(self):
        return self._value

    # Field getters
    def getGamepadID(self):
        return self._ctrlID
    def getAxis(self):
        return self._axis
    def getLastValue(self):
        return self._lastValue

    # Override parent method
    def getType(self):
        return Component.TYPE_GAMEPAD_AXIS

    # Callback
    def gamepadAxisEvent(self, action, gamepadId, analogValue):
        # Trap code in order to debug some issues in the Input System
        if self._ctrlID != Input.ALL_GAMEPADS_ID:
            if self._ctrlID != gamepadId:
                raise ValueError(f"[ERR] Input gamepad axis avent issue ctrlID={self._ctrlID}/event ID={gamepadId}")

        # Normalize value in order to take care of gamepads
        # that do not provide a full [-1.0,+1.0] output range
        # First, update min and max values
        if analogValue < self._minValue:
            self._minValue = analogValue
        if analogValue > self._maxValue:
            self._maxValue = analogValue
        # Then, check dead zone
        if abs(analogValue) < self._dead:
            analogValue = 0
        # Then, normalize
        if analogValue >= 0:
            analogValue /=  self._maxValue
        else:
            analogValue /= -self._minValue
        # Finally, store value
        if analogValue != 0:
            self._lastValue = analogValue
        self._value = analogValue

