
# FEATURE add unregister method with only Input ref as a parameter


## ============================================================
## IMPORTS
## ============================================================

from ..components.input import Input



## ============================================================
## INPUT MANAGER
## ============================================================

class InputSystem():

    ## -------------------------------------
    ## Constructor
    ## -------------------------------------
    def __init__(self):
        self.inputs = {}


    ## -------------------------------------
    ## Private methods
    ## -------------------------------------
    def __checkType(self, ref):
        if not isinstance(ref, Input):
            raise ValueError(f"[ERR] check input: bad object type. It should be Input !\n{ref}")

    def __getKeyIndex(self, key):
        return "K" + str(key)

    def __getMouseButtonIndex(self, buttonName):
        return "M" + buttonName

    def __getGamepadButtonIndex(self, gamepadId, buttonName):
        return "G" + str(gamepadId) + "B" + buttonName

    def __getMouseMotionIndex(self):
        return "Mmotion"

    def __getGamepadAxisIndex(self,gamepadId, axisName):
        return "G" + str(gamepadId) + "A" + axisName

    def __fillData(self, idx, actionName, inputRef):
        # Check type
        self.__checkType(inputRef)
        # create index in the dictionnary
        if idx not in self.inputs:
            self.inputs[idx] = {}
        # create action name in the sub dictionnary
        if actionName not in self.inputs[idx]:
            self.inputs[idx][actionName] = []
        # fill the input reference list
        if inputRef not in self.inputs[idx][actionName]:
            self.inputs[idx][actionName].append(inputRef)
        else:
            raise ValueError(f"[ERR] register input : ref is already in the list for action '{actionName}' and index '{idx}'")

    def __isExecutionAllowed(self, inRef, isOnPause):
        return inRef.isEnabled() and (not isOnPause or inRef.isEnabledOnPause())


    ## -------------------------------------
    ## Registering methods
    ## -------------------------------------
    def registerKey(self, key, actionName, inputRef):
        idx = self.__getKeyIndex(key)
        self.__fillData(idx, actionName, inputRef)

    def registerClick(self, buttonName, actionName, inputRef):
        idx = self.__getMouseButtonIndex(buttonName)
        self.__fillData(idx, actionName, inputRef)

    def registerButton(self, gamepadId, buttonName, actionName, inputRef):
        idx = self.__getGamepadButtonIndex(gamepadId, buttonName)
        self.__fillData(idx, actionName, inputRef)

    def registerMouse(self, actionName, inputRef):
        idx = self.__getMouseMotionIndex()
        self.__fillData(idx, actionName, inputRef)

    def registerAxis(self, gamepadId, axisName, actionName, inputRef):
        idx = self.__getGamepadAxisIndex(gamepadId, axisName)
        self.__fillData(idx, actionName, inputRef)


    ## -------------------------------------
    ## Notification methods
    ## -------------------------------------
    def notifyKeyEvent(self, key, isPressed, isOnPause):
        idx = self.__getKeyIndex(key)
        if idx in self.inputs:
            for action in self.inputs[idx]:
                for inRef in self.inputs[idx][action]:
                    if self.__isExecutionAllowed(inRef, isOnPause) :
                        inRef.keyboardEvent(action, isPressed)

    def notifyMouseButtonEvent(self, buttonName, x, y, isPressed, isOnPause):
        idx = self.__getMouseButtonIndex(buttonName)
        if idx in self.inputs:
            for action in self.inputs[idx]:
                for inRef in self.inputs[idx][action]:
                    if self.__isExecutionAllowed(inRef, isOnPause) :
                        inRef.mouseButtonEvent(action, x, y, isPressed)

    def notifyGamepadButtonEvent(self, gamepadId, buttonName, isPressed, isOnPause):
        indexes = [ self.__getGamepadButtonIndex(gamepadId, buttonName),
                    self.__getGamepadButtonIndex(Input.ALL_GAMEPADS_ID, buttonName)
                  ]
        for idx in indexes:
            if idx in self.inputs:
                for action in self.inputs[idx]:
                    for inRef in self.inputs[idx][action]:
                        if self.__isExecutionAllowed(inRef, isOnPause):
                            inRef.gamepadButtonEvent(action, gamepadId, isPressed)

    def notifyMouseMotionEvent(self, x, y, dx, dy, isOnPause):
        idx = self.__getMouseMotionIndex()
        if idx in self.inputs:
            for action in self.inputs[idx]:
                for inRef in self.inputs[idx][action]:
                    if self.__isExecutionAllowed(inRef, isOnPause) :
                        inRef.mouseMotionEvent(action, x, y, dx, dy)

    def notifyGamepadAxisEvent(self, gamepadId, axisName, analogValue, isOnPause):
        indexes = [self.__getGamepadAxisIndex(gamepadId, axisName),
                   self.__getGamepadAxisIndex(Input.ALL_GAMEPADS_ID, axisName)
                  ]

        # print(f"{action} {gamepadId} {analogValue}")
        #print(f"-----{gamepadId}-{axisName}-{analogValue}-----")
        for idx in indexes:
            if idx in self.inputs:
                for action in self.inputs[idx]:
                    for inRef in self.inputs[idx][action]:
                        if self.__isExecutionAllowed(inRef, isOnPause):
                            #print(f"{action} {inRef}")
                            inRef.gamepadAxisEvent(action, gamepadId, analogValue)

