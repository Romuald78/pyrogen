### ====================================================================================================
### IMPORTS
### ====================================================================================================
import arcade
import time
from .ecs.systems.sceneSystem import SceneSystem



### ====================================================================================================
### GAME CLASS
### ====================================================================================================


class Launcher(arcade.Window):

    # FEATURE : use key and mouse modifiers (Ctrl, Alt, Shift, ...)

    # FEATURE : how to create and add a scene outside the Main class ???

    # FEATURE : try to remove all arcade dependencies in the Main class (keep arcade in launcher)

    # FEATURE : REVIEW the design in order to remove as much as possible user scene calls to
    # ECS system. May be the Main file could be a upper class for the real user main ... to be continued

    BUTTON_NAMES = ["A",
                    "B",
                    "X",
                    "Y",
                    "LB",
                    "RB",
                    "VIEW",
                    "MENU",
                    "LSTICK",
                    "RSTICK",
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    ]

    AXIS_NAMES =["X",
                 "Y",
                 "RX",
                 "RY",
                 "Z",
                ]


    # ----------------------------------
    # PRIVATE METHODS FOR INPUT MANAGEMENT
    # ----------------------------------
    def __onButtonPressed(self, _gamepad, button):
        idx = self.gamepads[_gamepad]
        if Launcher.BUTTON_NAMES[button] != None:
            self.onButtonPressed(idx, Launcher.BUTTON_NAMES[button])
    def __onButtonReleased(self, _gamepad, button):
        idx = self.gamepads[_gamepad]
        if Launcher.BUTTON_NAMES[button] != None:
            self.onButtonReleased(idx, Launcher.BUTTON_NAMES[button])
    def __onCrossMove(self, _gamepad, x, y):
        idx = self.gamepads[_gamepad]
        self.onCrossMove(idx, x, -y)
    def __onAxisMove(self, _gamepad, axis, value):
        idx = self.gamepads[_gamepad]
        self.onAxisMove(idx, axis, value)


    # ----------------------------------
    # CONSTRUCTOR
    # ----------------------------------
    def __init__(self, width, height, title="Pyrogen", fullScreen=False):
        # Init application window
        super().__init__(width, height, title, fullScreen)

        # Create Scene system
        self._sceneMgr = SceneSystem(self)

        # Set application window background color
        arcade.set_background_color(arcade.color.BLACK)
        # Store gamepad list
        self.gamepads = arcade.get_game_controllers()
        # Check every connected gamepad
        if self.gamepads:
            for g in self.gamepads:
                # Link all gamepad callbacks to the current class methods
                g.open()
                g.on_joybutton_press   = self.__onButtonPressed
                g.on_joybutton_release = self.__onButtonReleased
                g.on_joyhat_motion     = self.__onCrossMove
                g.on_joyaxis_motion    = self.__onAxisMove
            # Transform list into a dictionary to get its index faster
            self.gamepads = { self.gamepads[idx]:idx for idx in range(len(self.gamepads)) }
        else:
            print("There are no Gamepad connected !")
            self.gamepads = None
        # FPS counter
        self.updateTime  = []
        self.drawTime    = []
        self.frameTime   = []




    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                SETUP your game here
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def setup(self):
        pass
    def addScene(self, newScene, sceneName):
        self._sceneMgr.addScene(newScene(self._sceneMgr, sceneName))
    def start(self):
        self.center_window()
        self.set_vsync(True)
        self.setup()
        arcade.run()


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                               DRAW your game elements here
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def on_draw(self):
        measure = time.time()
        arcade.start_render()
        self._sceneMgr.drawCurrentScene()
        measure = time.time() - measure
        self.drawTime.append(measure)
        self.drawTime = self.drawTime[-60:]
        arcade.draw_text("FPS   : "+str(int(60 / sum(self.frameTime))), 12, 12, (255, 255, 255))
        arcade.draw_text("Draw  : "+str(round(sum(self.updateTime)*50/3,3))+"ms"      , 12, 24, (255, 255, 255))
        arcade.draw_text("Update: "+str(round(sum(self.drawTime  )*50/3,3))+"ms"      , 12, 36, (255, 255, 255))


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                  UPDATE your game model here
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def update(self, delta_time):
        measure = time.time()
        self._sceneMgr.updateCurrentScene(delta_time)
        measure = time.time() - measure
        self.updateTime.append(measure)
        self.updateTime = self.updateTime[-60:]
        self.frameTime.append(delta_time)
        self.frameTime = self.frameTime[-60:]


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # KEY PRESSED events
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def on_key_press(self, key, modifiers):
        # Close application if ESCAPE key is hit
        if key == arcade.key.ESCAPE:
            self.close()
        # switch between full screen and window mode
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
        # Dispatch all key events
        self._sceneMgr.dispatchKeyEvent(key, True)


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # KEY RELEASED events
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def on_key_release(self, key, modifiers):
        self._sceneMgr.dispatchKeyEvent(key, False)


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # GAMEPAD BUTTON PRESSED events
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def onButtonPressed(self, gamepadNum, buttonName):
        self._sceneMgr.dispatchGamepadButtonEvent(gamepadNum,buttonName,True)


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # GAMEPAD BUTTON RELEASED events
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def onButtonReleased(self, gamepadNum, buttonName):
        self._sceneMgr.dispatchGamepadButtonEvent(gamepadNum,buttonName,False)


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # GAMEPAD CROSSPAD events
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def onCrossMove(self, gamepadNum, xValue, yValue):
        self._sceneMgr.dispatchGamepadAxisEvent(gamepadNum, "X", xValue)
        self._sceneMgr.dispatchGamepadAxisEvent(gamepadNum, "Y", yValue)


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # GAMEPAD AXIS events
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def onAxisMove(self, gamepadNum, axisName, analogValue):
        if axisName == "z":
            analogValue = -analogValue
        self._sceneMgr.dispatchGamepadAxisEvent(gamepadNum,axisName.upper(),analogValue)


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # MOUSE MOTION events
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def on_mouse_motion(self, x, y, dx, dy):
        self._sceneMgr.dispatchMouseMotionEvent(x,y,dx,dy)


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # MOUSE BUTTON PRESSED events
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def on_mouse_press(self, x, y, button, modifiers):
        buttonName = "M" + str(button)
        self._sceneMgr.dispatchMouseButtonEvent(buttonName,x,y,True)


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # MOUSE BUTTON RELEASED events
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def on_mouse_release(self, x, y, button, modifiers):
        buttonName = "M" + str(button)
        self._sceneMgr.dispatchMouseButtonEvent(buttonName,x,y,False)

