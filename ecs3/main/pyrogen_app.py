import platform
import pyglet

# ---------------------------------------------------------------
# On OS X we need to disable the shadow context
# because the 2.1 shadow context cannot be upgrade to a 3.3+ core
if platform.system() == "Darwin":
    pyglet.options["shadow_window"] = False
# ---------------------------------------------------------------

import cProfile

from ..loader.loader import ResourceLoader
from ..gpu.opengl_data import OpenGLData
from ..systems.scene_system import SceneSystem


# ========================================================
# 21/06/2021 :
# - dynamic sprites = 3k
# - static  sprites = 100k
# both calling the sprite.update() method to check if the
# array.array must be copied into the GPU texture
# ========================================================


# ========================================================
# DEBUG PARAMS
# ========================================================
DEBUG_DISPLAY_PERFS  = False


class Pyrogen():

    def __init__(self,
                 atlasDir=".",
                 fsGpuMemSize= 8*1024*1024*4,
                 *args, **kwargs):

        # Create GL config
        cfg = pyglet.gl.Config(
            major_version=3,
            minor_version=3,
            forward_compatible=True,
            depth_size=24,
            double_buffer=True,
            sample_buffers=1,
            samples=4,
        )

        # Instanciate Window
        self._pyrogenWin = PyrogenWindow(atlasDir=atlasDir,
                                     fsGpuMemSize=fsGpuMemSize,
                                     config=cfg,
                                     *args, **kwargs)

    def addImage(self, name, path, spriteInfo=None):
        self._pyrogenWin.addImage(name, path, spriteInfo)

    def addFont(self, name, path, size=128, border=1):
        self._pyrogenWin.addFont(name, path, size, border)

    def finalizeResources(self):
        self._pyrogenWin.finalizeResources()

    def addScene(self, name, ref):
        self._pyrogenWin.addScene(name, ref)

    def run(self):
        self._pyrogenWin.run()




class PyrogenWindow(pyglet.window.Window):

    # ========================================================
    #  EVENTS
    # ========================================================
    def _keyboardEvent(self, keyID, isPressed, modifiers):
        print(f"<KEY> id={keyID} isPressed={isPressed} modifiers={modifiers}")
        self._scnMgr.keyboardEvent(keyID, isPressed, modifiers)
    def _mouseButtonEvent(self, x, y, buttonID, isPressed, modifiers):
        y = self.height-y
        print(f"<MOUSE-BUTTON> position=({x},{y}) buttonID={buttonID} isPressed={isPressed} modifiers={modifiers}")
        self._scnMgr.mouseButtonEvent(x, y, buttonID, isPressed, modifiers)
    def _mouseMotionEvent(self, x, y, dx, dy):
        dy = -dy
        print(f"<MOUSE-MOVE> position=({x},{y}) direction=({dx},{dy})")
        self._scnMgr.mouseMotionEvent(x, y, dx, dy)
    def _mouseDragEvent(self, x, y, dx, dy, buttonID, modifiers):
        dy = -dy
        print(f"<MOUSE-DRAG> position=({x},{y}) direction=({dx},{dy}) buttonID={buttonID} modifiers={modifiers}")
        self._scnMgr.mouseDragEvent(x, y, dx, dy, buttonID, modifiers)
    def _mouseScrollEvent(self, x, y, dx, dy):
        print(f"<MOUSE-SCROLL> position=({x},{y}) direction=({dx},{dy})")
        self._scnMgr.mouseScrollEvent(x, y, dx, dy)
    def _gamepadButtonEvent(self, gamepadID, buttonID, isPressed):
        print(f"<GAMEPAD-BUTTON> gamePadID=({gamepadID}) buttonID=({buttonID}) isPressed={isPressed}")
        self._scnMgr.gamepadButtonEvent(gamepadID, buttonID, isPressed)
    def _gamepadAxisEvent(self, gamepadID, axisID, analogValue):
        if axisID == "z":
            analogValue *= -1
        print(f"<GAMEPAD-AXIS> gamePadID=({gamepadID}) axisID=({axisID}) value={analogValue}")
        self._scnMgr.gamepadAxisEvent(gamepadID, axisID, analogValue)

    # ========================================================
    #  PYGLET CALLBACKS
    # ========================================================
    def on_key_press(self, symbol, modifiers):
        self._keyboardEvent(symbol, True, modifiers)
        if symbol == pyglet.window.key.ESCAPE:
            self._openGlData.displayFS()
            self.close()
    def on_key_release(self, symbol, modifiers):
        self._keyboardEvent(symbol, False, modifiers)
    def on_mouse_press(self, x, y, button, modifiers):
        self._mouseButtonEvent(x, y, button, True, modifiers)
    def on_mouse_release(self, x, y, button, modifiers):
        self._mouseButtonEvent(x, y, button, False, modifiers)
    def on_mouse_motion(self, x, y, dx, dy):
        self._mouseMotionEvent(x, y, dx, dy)
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._mouseDragEvent(x, y, dx, dy, buttons, modifiers)
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self._mouseScrollEvent(x, y, scroll_x, scroll_y)
    def on_joystick_press(self, joystick, button):
        joyID = self.gamepads[joystick]
        self._gamepadButtonEvent(joyID, button, True)
    def on_joystick_release(self, joystick, button):
        joyID = self.gamepads[joystick]
        self._gamepadButtonEvent(joyID, button, False)
    def on_joystick_motion(self, joystick, axis, value):
        joyID = self.gamepads[joystick]
        self._gamepadAxisEvent(joyID, axis, value)
    def on_joystick_hat(self, joystick, x, y):
        joyID = self.gamepads[joystick]
        self._gamepadAxisEvent(joyID, "x",  x)
        self._gamepadAxisEvent(joyID, "y", -y)

    # ========================================================
    #  GAMEPADS
    # ========================================================
    def _loadGamepads(self):
        # Gamepad callbacks
        joysticks = pyglet.input.get_joysticks()
        N = len(joysticks)
        s1 = "is" if N <= 1 else "are"
        s2 = "" if N <= 1 else "s"
        if N == 0:
            N = "no"
        print(f"\nThere {s1} {N} connected gamepad{s2}")
        self.gamepads = {}
        if len(joysticks) > 0:
            i = 0
            for g in joysticks:
                g.open()
                if g not in self.gamepads:
                    self.gamepads[g] = i
                    i += 1
                g.on_joybutton_press   = self.on_joystick_press
                g.on_joybutton_release = self.on_joystick_release
                g.on_joyaxis_motion    = self.on_joystick_motion
                g.on_joyhat_motion     = self.on_joystick_hat
                print(f"    ID : #{i-1} - NAME : {g.device.name}")

    # ========================================================
    #  PERFORMANCE DISPLAY (DEBUG)
    # ========================================================
    def _displayPerfs(self, cpr):
        # List methods under supervision
        watchMethods = [
            #                    "render",
            #                    "update",
            "updateMovingSprites",
            #                    "write",
            #                    "_write",
            #                    "_verifCHK",
            #                    "_computeCHK",
            #                    "_explodeID",
            #                    "genVertex",
            #                    "writeBlock",
            #                    "getData",
            #                    "on_draw"
        ]
        watchFiles = [
            #            "gfx_components",
        ]
        # Get stats of execution : parse them
        st = cpr.getstats()
        out = []
        for row in st:
            # Prepare data
            code = str(row[0])
            code = code.replace("code object ", "")
            code = code.replace("built-in ", "")
            code = code.replace("method ", "")
            code = code.replace(" objects", "")
            code = code.replace("<", "")
            code = code.replace(">", "")
            code = code.split(",")
            method = code[0].split(" ")[0]
            file = code[1] if len(code) > 1 else ""
            file = file.replace("file", "")
            file = file.replace("\"", "")
            #            file   = os.path.basename(file).split(".")[0]
            line = code[2] if len(code) > 2 else ""
            line = line.lower().replace("line ", "")
            # store data
            toBeStored = False
            for w in method.split(" "):
                if w in watchMethods:
                    toBeStored = True
                    break
            for w in watchFiles:
                if w in file:
                    toBeStored = True
            #            toBeStored = True
            if toBeStored:
                out.append({"method": method,
                            "file": file,
                            "line": line,
                            "ncalls": str(row[1]).replace(".", ","),
                            "tottime": str(1000 * row[4]).replace(".", ","),
                            "totpercall": str(1000 * row[4] / row[1]).replace(".", ","),
                            "cumtime": str(1000 * row[3]).replace(".", ","),
                            "cumpercall": str(1000 * row[3] / row[1]).replace(".", ","),
                            })
        out = sorted(out, key=lambda x: (x["file"], x["method"]))
        for o in out:
            me = o["method"]
            fi = o["file"]
            li = o["line"]
            nc = o["ncalls"]
            tt = o["tottime"]
            tp = o["totpercall"]
            ct = o["cumtime"]
            cp = o["cumpercall"]
            print(f"{fi}/{me} ({li})\t{nc}\t{tt}\t{tp}\t{ct}\t{cp}")

    # ========================================================
    #  CONSTRUCTOR
    # ========================================================
    def __init__(self,
                 atlasDir=".",
                 fsGpuMemSize= 8*1024*1024*4,
                 *args, **kwargs, ):
        # Parent constructor
        super().__init__(*args, **kwargs)
        # Gamepads
        self._loadGamepads()
        # initiate the resource loader
        self._loader = ResourceLoader(atlasDir)
        # GL Stuff
        self._openGlData = OpenGLData(self._loader, fsGpuMemSize)
        # Profiling
        self._FPS = []
        # Create scene manager
        self._scnMgr = SceneSystem()

    # ========================================================================
    #  RESOURCES
    # ========================================================================
    def addImage(self, name, path, spriteInfo=None):
        self._loader.addImage(name, path, spriteInfo)
    def addFont(self, name, path, size=128, border=1):
        self._loader.addFont(name, path, size=size, border=border)
    def finalizeResources(self):
        self._openGlData.createAtlas()
    def addScene(self, name, ref):
        self._scnMgr.registerScene(name, ref)

    # ========================================================
    #  UPDATE METHOD
    # ========================================================
    def update(self, deltaTime):
        # Process FPS
        self._FPS.append(deltaTime)
        if len(self._FPS)==60:
            print(f">>>>>>>>>>>>> FPS = {round(60/sum(self._FPS),2)} <<<<<<<<<<<<<<<<<<<<<<<")
            self._FPS = []

        # Update the current scene
        # this will update the world and all the systems inside
        self._scnMgr.updateScene(deltaTime)

    # ========================================================
    #  RENDER METHOD
    # ========================================================
    def on_draw(self):
        # Render the current scene
        self._scnMgr.renderScene()

    # ========================================================
    #  RESIZE APPLICATION WINDOW
    # ========================================================
    def on_resize(self, width, height):
        pass
#        self.ctx.screen.viewport = 0, 0, *self.get_framebuffer_size()
#  check window.get_pixel_ratio() to be sure of the physical screen size


    # ========================================================
    #  MAIN LOOP
    # ========================================================
    def run(self):
        # Do not run the app if no scene has been created
        if self._scnMgr.getNbScenes() <= 0:
            raise RuntimeError("[ERROR] Impossible to launch the application because there is no Scene registered !")

        # update loop interval
        pyglet.clock.schedule_interval(self.update, 1/65)

        # Start pyglet app and profile it if needed
        cpr = None
        if DEBUG_DISPLAY_PERFS:
            cpr = cProfile.Profile()
            cpr.enable()
        pyglet.app.run()
        if DEBUG_DISPLAY_PERFS:
            cpr.disable()
            self._displayPerfs(cpr)

