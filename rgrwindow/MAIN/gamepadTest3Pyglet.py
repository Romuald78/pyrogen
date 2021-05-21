import math
from pathlib import Path

import numpy as np
import moderngl
import moderngl_window
import pyglet
from PIL import Image

from pyrogen.src.pyrogen.ecs.shaders.simple_shader import SimpleShader
from pyrogen.src.pyrogen.rgrwindow.MAIN.loader import ResourceLoader
from pyrogen.src.pyrogen.rgrwindow.MAIN.opengl_data import OpenGLData


class PyrogenApp3(pyglet.window.Window):

    # ========================================================
    # PARAMETERS
    # ========================================================
    CHANNEL_ATLAS_INFO    = 0
    CHANNEL_ATLAS_TEXTURE = 1
    CHANNEL_LIGHTS        = 7


    # ========================================================
    # EVENTS
    # ========================================================
    def keyboardEvent(self, keyID, isPressed, modifiers):
        print(f"<KEY> id={keyID} isPressed={isPressed} modifiers={modifiers}")
    def mouseButtonEvent(self, x, y, buttonID, isPressed, modifiers):
        y = self.height-y
        print(f"<MOUSE-BUTTON> position=({x},{y}) buttonID={buttonID} isPressed={isPressed} modifiers={modifiers}")
    def mouseMotionEvent(self, x, y, dx, dy):
        dy = -dy
        print(f"<MOUSE-MOVE> position=({x},{y}) direction=({dx},{dy})")
    def mouseDragEvent(self, x, y, dx, dy, buttonID, modifiers):
        dy = -dy
        print(f"<MOUSE-DRAG> position=({x},{y}) direction=({dx},{dy}) buttonID={buttonID} modifiers={modifiers}")
    def mouseScrollEvent(self, x, y, dx, dy):
        print(f"<MOUSE-SCROLL> position=({x},{y}) direction=({dx},{dy})")
    def gamepadButtonEvent(self, gamepadID, buttonID, isPressed):
        print(f"<GAMEPAD-BUTTON> gamePadID=({gamepadID}) buttonID=({buttonID}) isPressed={isPressed}")
    def gamepadAxisEvent(self, gamepadID, axisID, analogValue):
        if axisID == "z":
            analogValue *= -1
        print(f"<GAMEPAD-AXIS> gamePadID=({gamepadID}) axisID=({axisID}) value={analogValue}")


    # ========================================================
    # CALLBACKS
    # ========================================================
    def on_key_press(self, symbol, modifiers):
        self.keyboardEvent(symbol, True, modifiers)
        if symbol == pyglet.window.key.ESCAPE:
            self.close()
    def on_key_release(self, symbol, modifiers):
        self.keyboardEvent(symbol, False, modifiers)
    def on_mouse_press(self, x, y, button, modifiers):
        self.mouseButtonEvent(x, y, button, True, modifiers)
    def on_mouse_release(self, x, y, button, modifiers):
        self.mouseButtonEvent(x, y, button, False, modifiers)
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouseMotionEvent(x, y, dx, dy)
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouseDragEvent(x, y, dx, dy, buttons, modifiers)
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.mouseScrollEvent(x, y, scroll_x, scroll_y)
    def on_joystick_press(self, joystick, button):
        joyID = self.gamepads[joystick]
        self.gamepadButtonEvent(joyID, button, True)
    def on_joystick_release(self, joystick, button):
        joyID = self.gamepads[joystick]
        self.gamepadButtonEvent(joyID, button, False)
    def on_joystick_motion(self, joystick, axis, value):
        joyID = self.gamepads[joystick]
        self.gamepadAxisEvent(joyID, axis, value)
    def on_joystick_hat(self, joystick, x, y):
        joyID = self.gamepads[joystick]
        self.gamepadAxisEvent(joyID, "x", x)
        self.gamepadAxisEvent(joyID, "y", -y)


    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # GL config
        self.cfg = pyglet.gl.Config(
            major_version=3,
            minor_version=3,
            forward_compatible=True,
            depth_size=24,
            double_buffer=True,
            sample_buffers=1,
            samples=4,
        )
        # GL context
        self.ctx  = moderngl.create_context(require=330)
        moderngl_window.activate_context(ctx=self.ctx)
        for field in self.ctx.info:
            print(f"{field} : {self.ctx.info[field]}")

        # Gamepad callbacks
        joysticks = pyglet.input.get_joysticks()
        self.gamepads = {}
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

        # initiate the resource loader
        self._loader = ResourceLoader()

        # Store a list of different programs
        # Only one can be selected at a time
        #the selected program will be used in the prepareData method
        self._program            = None
        self._programs           = {}

        # structure to store all rendering information
        self._openGlData = OpenGLData()

        # init app time
        self.time = 0


    # ========================================================================
    # RESOURCES
    # ========================================================================
    def addImage(self, name, path, spriteInfo=None):
        self._loader.addImage(name, path, spriteInfo)


    # ========================================================================
    # PROGRAMS
    # ========================================================================
    # The first program to be added, is automatically selected
    def __addProgram(self, name, vertexStr="", geometryStr="", fragmentStr=""):
        # Create program from shader sources
        prog = self.ctx.program(vertex_shader=vertexStr,
                                geometry_shader=geometryStr,
                                fragment_shader=fragmentStr)
        # check this program name is not already used
        if name in self._programs:
            raise RuntimeError("[ERROR] loadProgram : {name} is already in the program list !")
        # Store new program
        self._programs[name] = prog
        # Select this program is this is the first one
        if len(self._programs) == 1:
            self.__selectProgram(name)

    # Select a program from the program list
    def __selectProgram(self, name):
        if name in self._programs:
            self._program = self._programs[name]


    # ========================================================================
    # GPU CONFIGURATION
    # ========================================================================
    def __prepareData(self):
        # -----------------------------------------------------------------
        # TEXTURE ATLAS
        # TODO create texture_array with (width,height,nbLayers)
        # -----------------------------------------------------------------
        # Set image directory
        image   = self._loader.getTextureImage()
        texture = self.ctx.texture(image.size, 4, image.tobytes())
        self._openGlData.set("textureAtlas", texture)

        # -----------------------------------------------------------------
        # ATLAS INFO
        # -----------------------------------------------------------------
        # Set texture to contain all texture info (needed to access atlas data)
        # Write Pyrogen Texture data (20 x 32bit values)
        # Pack values using the nb of components
        # e.g.  X,Y,W,H packed in a single RGBA value
        # texelFetch() function to get them from GPU side
        # texture.filter = moderngl.NEAREST, moderngl.NEAREST
        #
        # [FOR EACH TEXTURE]
        # > Diffuse data
        #    - (X,Y) top left position
        #    - (W,H) size
        # > Normal data
        #    - (X,Y) top left position
        #    - (W,H) size
        # > Specular Data
        #    - (X,Y) top left position
        #    - (W,H) size
        nbTextures       = self._loader.getNbTextures()
        nbDataPerTexture = 3
        nbDataPerHeader  = 0
        nbComponents     = 4
        width            = nbTextures*nbDataPerTexture
        nbTexels         = width * nbComponents
        overhead         = nbDataPerHeader * nbComponents # 3 values
        # Prepare texture
        texture = self.ctx.texture((width, 1), nbComponents, dtype="u4")
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # Write texture positions and sizes
        data = np.zeros(nbTexels+overhead, np.uint32)
        allIDs = self._loader.getAllIds()
        for id in allIDs:
            data[4*id+0] = self._loader.getTextureById(id)["x"]
            data[4*id+1] = self._loader.getTextureById(id)["y"]
            data[4*id+2] = self._loader.getTextureById(id)["w"]
            data[4*id+3] = self._loader.getTextureById(id)["h"]
        texture.write(data.tobytes())

        # Fill data structure
        self._openGlData.set("nbTextures", nbTextures)
        self._openGlData.set("atlasInfo" , texture   )

        # -----------------------------------------------------------------
        # LIGHT INFO (circular lights)
        # TODO
        # -----------------------------------------------------------------
        #
        # [ONCE]
        # > Header
        #    - nb registered lights
        #    - RFU
        #    - RFU
        #    - RFU
        #
        # [EACH LIGHT]
        # > Position and Z range
        #    - (X, Y)
        #    - (minZ, maxZ)
        # > Color
        #    - (R, G, B)
        #    - Radius
        nbComponents = 4
        nbLights = 2
        textureInfoSize = 2 * nbComponents  # 2 values (4 components)
        overhead = 1 * nbComponents  # 1 value
        texture = self.ctx.texture((nbLights * textureInfoSize + overhead, 1), nbComponents, dtype="u4")
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self._openGlData.set("nbLights", nbLights)
        self._openGlData.set("lightInfo", texture)

        # -----------------------------------------------------------------
        # SPRITE BUFFER (VERTEX)
        # -----------------------------------------------------------------
        # Create sprite information (input data)
        nbComponents = 4
        spriteInfoSize = (5 + 1) * nbComponents  # 6 values in vertex input
        nbMaxSprites = 100
        buffer = self.ctx.buffer(reserve=nbMaxSprites * spriteInfoSize)
        self._openGlData.set("spriteSize", spriteInfoSize)
        self._openGlData.set("nbSprites", nbMaxSprites)
        self._openGlData.set("spriteBuffer", buffer)

        # -----------------------------------------------------------------
        # VERTEX ARRAY OBJECT
        # -----------------------------------------------------------------
        # Create vertex array object
        vertexArray = self.ctx.vertex_array(
                        self._program,
                        [
                            (self._openGlData.get("spriteBuffer"),
                             "2f 2f 1f 1f",
                             "in_position",
                             "in_size",
                             "in_rotation",
                             "in_tex_id"),
                        ]
                    )
        self._openGlData.set("vao", vertexArray)


        # TODO                                               !!
        # TODO continue to get code from pyrogen_app.py file !!
        # TODO                                               !!





    # ========================================================
    # UPDATE METHOD
    # ========================================================
    def update(self, deltaTime):
        self.time += deltaTime


    # ========================================================
    # RENDER METHOD
    # ========================================================
    def on_draw(self):
        # Clear buffer with background color
        self.ctx.clear(
            (math.sin(self.time + 0) + 1.0) / 2,
            (math.sin(self.time + 2) + 1.0) / 2,
            (math.sin(self.time + 3) + 1.0) / 2,
        )

        # Set blitting mode
        # self.ctx.blend_equation  = moderngl.FUNC_SUBTRACT
        # self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        self.ctx.enable(moderngl.BLEND)

        # Set the atlas texture to an opengl channel
        # texture channels (up to 16 ?)
        # texture atlas (
        # texture arrays (several layers , same coords)
        # texture that stores information on atlas positions
        # warning take care of borders in case of 2d atlas !! :
        # Use atlas from pyglet (algo to make fits the better)
        # max dim 16k*16k
        # see ctx.info for info
        self._openGlData.get("atlasInfo").use(PyrogenApp3.CHANNEL_ATLAS_INFO)
        self._openGlData.get("textureAtlas").use(PyrogenApp3.CHANNEL_ATLAS_TEXTURE)
        self._openGlData.get("lightInfo").use(PyrogenApp3.CHANNEL_LIGHTS)





    # TODO
    # def on_resize(self, width, height):
    #    self.ctx.screen.viewport = 0, 0, *self.get_framebuffer_size()


    # ========================================================
    # MAIN LOOP
    # ========================================================
    def run(self):
        # compute image atlas from the resource loader
        # TODO use the GPU texture size property instead of hard-coded value
        self._loader.generateImageAtlas(768, 3)

        # Instanciate shader object and add program
        shader = SimpleShader()
        self.__addProgram("Program #1",
                          vertexStr=shader.getVertex(),
                          geometryStr=shader.getGeometry(),
                          fragmentStr=shader.getFragment())

        # Prepare GPU stuff
        self.__prepareData()
        # update loop interval
        pyglet.clock.schedule_interval(self.update, 1/60)
        # Start pyglet app
        pyglet.app.run()







if __name__ == '__main__':
    # instanciate Pyrogen application
    app = PyrogenApp3(width=1280, height=720)
    # and run it
    app.run()










