## ============================================================
## IMPORTS
## ============================================================
import arcade


## ============================================================
## SCENE MANAGER (driven by the main class)
## ============================================================
class SceneSystem():

    ## -------------------------------------
    ## Constructor
    ## -------------------------------------
    def __init__(self, application):
        # Scene names used in the main process
        self._currentSceneName = None
        self._nextSceneName    = None
        self._nextSceneParams  = None
        # Pause mode
        self._onPause          = False
        # Dict of shmup
        self._scenes           = {}
        # Time and color used in the transition process
        self._currentTime      = 1
        self._maxTime          = 1
        self._color            = (0, 0, 0)
        # Keep application reference
        self._application = application


    ## -------------------------------------
    ## Scene list management
    ## -------------------------------------
    def addScene(self, sceneRef, params=None):
        sceneName = sceneRef.getName()
        if sceneName not in self._scenes:
            self._scenes[sceneName] = sceneRef
            # select this scene if this is the first to be added
            if len(self._scenes) == 1:
                self._currentSceneName = sceneName
                self._currentTime      = 0
                self._maxTime          = sceneRef.getTransitionTimeIN()
                self._color            = sceneRef.getTransitionColorIN()
                # Call the init method as it is the first time
                sceneRef.init(params)
        else:
            raise ValueError(f"[ERR] cannot add scene '{sceneName}' : already in the list !")

    def removeScene(self, sceneName):
        if sceneName in self._scenes:
            # delete scene if not selected
            if self._currentSceneName != sceneName:
                del self._scenes[sceneName]
            else:
                raise ValueError(f"[ERR] cannot remove scene '{sceneName}' : currently selected !")
        else:
            raise ValueError(f"[ERR] cannot remove scene '{sceneName}' : not in the list !")


    ## -------------------------------------
    ## Scene control
    ## -------------------------------------
    def selectNewScene(self,sceneName, params=None):
        # Set the next scene if not currently in transition
        if self._nextSceneName == None:
            self._nextSceneName   = sceneName
            self._nextSceneParams = params
            self._maxTime         = self._scenes[self._currentSceneName].getTransitionTimeOUT()
            self._currentTime     = 0
            self._color           = self._scenes[self._currentSceneName].getTransitionColorOUT()
        else:
            pass
            #print(f"[WRN] cannot select scene {sceneName} : transition in progress !")

    def getCurrentSceneName(self):
        return self._currentSceneName

    def getApplication(self):
        return self._application

    def pause(self):
        self._onPause = True

    def resume(self):
        self._onPause = False

    def isPaused(self):
        return self._onPause


    ## -------------------------------------
    ## Transitions methods
    ## -------------------------------------
    def __updateTransition(self, deltaTime):
        # increase timer
        self._currentTime = self._currentTime + deltaTime
        # OUT phase
        if self._nextSceneName != None:
            if self._currentTime >= self._maxTime:
                # First time we arrive here, we check for params
                if self._nextSceneParams != None:
                    self._scenes[self._nextSceneName].init(self._nextSceneParams)
                    self._nextSceneParams = None
                # switch to IN phase
                self._currentSceneName = self._nextSceneName
                self._currentTime     -= self._maxTime
                self._maxTime          = self._scenes[self._nextSceneName].getTransitionTimeIN()
                self._color            = self._scenes[self._nextSceneName].getTransitionColorIN()
                self._nextSceneName    = None
        # IN Phase
        else:
            # saturate the current time
            self._currentTime = min(self._maxTime, self._currentTime)

    def __getTransitionColor(self):
        # OUT phase
        if self._nextSceneName != None:
            alpha = self._currentTime / self._maxTime
        # IN phase
        else:
            alpha = 1.0 - (self._currentTime / self._maxTime)
            if alpha <= 0:
                # no use to display a full transparent screen
                # when the transition is over
                return None
        # concatenate RGB and ALPHA
        alpha = int(255*alpha)
        return self._color + (alpha,)


    ## -------------------------------------
    ## Scene process
    ## -------------------------------------
    def updateCurrentScene(self, deltaTime):
        # we need at least one scene
        if self._currentSceneName != None:
            # update transition information
            self.__updateTransition(deltaTime)
            # Get scene ref
            scn = self._scenes[self._currentSceneName]
            # Display debug info on console output
            scn.displayDebugInfo()
            # update
            scn.update(deltaTime)


    def drawCurrentScene(self):
        # we need at least one scene
        if self._currentSceneName != None:
            scn = self._scenes[self._currentSceneName]
            # draw current scene
            scn.draw()
            # draw color mask in case of transitions
            clr = self.__getTransitionColor()
            if clr != None:
                # TODO : Get viewport instead of scene dimensions (should be the same but ...)
                W, H = scn.getDimensions()
                arcade.draw_rectangle_filled(W//2, H//2, W, H, clr)
            # Draw debug info on screen
            scn.drawDebugInfo()


    ## -------------------------------------
    ## Input management
    ## -------------------------------------
    def dispatchKeyEvent(self, key, isPressed):
        if self._currentSceneName != None:
            self._scenes[self._currentSceneName].onKeyEvent(key, isPressed)

    def dispatchMouseButtonEvent(self, buttonName, x, y, isPressed):
        if self._currentSceneName != None:
            self._scenes[self._currentSceneName].onMouseButtonEvent(buttonName, x, y, isPressed)

    def dispatchMouseMotionEvent(self, x, y, dx, dy):
        if self._currentSceneName != None:
            self._scenes[self._currentSceneName].onMouseMotionEvent(x, y, dx, dy)

    def dispatchGamepadButtonEvent(self, gamepadNum, buttonName, isPressed):
        if self._currentSceneName != None:
            self._scenes[self._currentSceneName].onGamepadButtonEvent(gamepadNum, buttonName, isPressed)

    def dispatchGamepadAxisEvent(self, gamepadNum, axisName, analogValue):
        if self._currentSceneName != None:
            self._scenes[self._currentSceneName].onGamepadAxisEvent(gamepadNum, axisName, analogValue)

