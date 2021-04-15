import math
import random
from array import array
from pathlib import Path

import moderngl
import moderngl_window
from moderngl_window import settings, resources
from moderngl_window.meta import TextureDescription
from pyrr import Matrix44


class PyrogenApp():

    #========================================================================
    # EVENT CALLBACKS
    # TODO add missing ones :
    # - gamepads !!!
    # - self._winCfg.resize_func
    # - self._winCfg.iconify_func
    # - self._winCfg.unicode_char_entered_func
    #========================================================================
    def keyboardEvent(self, symbol, action, modifiers):
        isPressed = True if action==self._window.keys.ACTION_PRESS else False
        # if symbol == pyglet.window.key.A:
        print(f"key:{symbol} pressed:{isPressed} modifiers:{modifiers}")

    def mouseButtonPressed(self, x, y, button):
        print(f"Button {button} is pressed @{x}/{y}")

    def mouseButtonReleased(self, x, y, button):
        print(f"Button {button} is released @{x}/{y}")

    def mouseMoveEvent(self, x, y, dx, dy):
        print(f"Moving mouse @{x}/{y} with speed:{dx}/{dy}")

    def mouseDragEvent(self, x, y, dx, dy):
        print(f"Dragging mouse @{x}/{y} with speed:{dx}/{dy}")

    def mouseScrollEvent(self, dx, dy):
        print(f"Scrolling mouse with speed:{dx}/{dy}")


    #========================================================================
    # CONSTRUCTOR
    # TODO add icon when creating app
    #========================================================================
    def __init__(self):
        # Create a Pyglet window
        settings.WINDOW['class'] = 'moderngl_window.context.pyglet.Window'
        self._window             = moderngl_window.create_window_from_settings()
        # Store a list of different programs
        # Only one can be selected at a time
        #the selected program will be used in the prepareData method
        self._program            = None
        self._programs           = {}

        # structure to store all rendering information
        #(data given to the shaders)
        self.openGlData = { "staticAtlas": None,
                            "itemSize"   : None,
                            "nbItems"    : None,
                            "dataBuffer" : None,
                            "vao"        : None,
                            "projMatrix" : None,

                            }

        # Map callback functions
        self._window.key_event_func            = self.keyboardEvent
        self._window.mouse_press_event_func    = self.mouseButtonPressed
        self._window.mouse_release_event_func  = self.mouseButtonReleased
        self._window.mouse_position_event_func = self.mouseMoveEvent
        self._window.mouse_drag_event_func     = self.mouseDragEvent
        self._window.mouse_scroll_event_func   = self.mouseScrollEvent


    # ========================================================================
    # GETTERS
    # ========================================================================
    @property
    def window(self):
        return self._window
    @property
    def context(self):
        return self._window.ctx


    # ========================================================================
    # PUBLIC METHODS
    # ========================================================================
    # If this is the first program to be added, it is selected automatically
    def addProgram(self, name, vertexStr="", geometryStr="", fragmentStr=""):
        # Create program from shader sources
        prog = self._window.ctx.program(vertex_shader   = vertexStr,
                                        geometry_shader = geometryStr,
                                        fragment_shader = fragmentStr)
        # check this program name is not already used
        if name in self._programs:
            raise RuntimeError("[ERROR] loadProgram : {name} is already in the program list !")
        # Store new program
        self._programs[name] = prog
        # Select this program is this is the first one
        if len(self._programs)==1:
            self.selectProgram(name)

    # Select a program from the program list
    def selectProgram(self, name):
        if name in self._programs:
            self._program = self._programs[name]

    def prepareData(self):

        # Set atlas containing static sprites
        myPath = Path(__file__).parent.resolve()
        resources.register_dir(myPath)
        texture = resources.textures.load(TextureDescription(path="atlas.png"))
        self.openGlData["staticAtlas"] = texture

        # Create static sprite information
        itemSize = (5+4) * 4    # 5 x 32 bit floats
        nbItems  = 10000
        self.openGlData["itemSize"] = itemSize
        self.openGlData["nbItems"]  = nbItems
        self.openGlData["dataBuffer"] = self._window.ctx.buffer(reserve=nbItems * itemSize)

        # Create vertex array object
        self.openGlData["vao"]        = self._window.ctx.vertex_array(
            self._program,
            [
#               (self.openGlData["dataBuffer"], "2f 2f 1f", "in_position", "in_size", "in_rotation"),
                (self.openGlData["dataBuffer"], "2f 2f 1f 4f", "in_position", "in_size", "in_rotation", "in_atlas_pos"),
            ]
        )

        # Create projection matrix
        # TODO : use this to change viewport (position, size, zoom, rotation, ...)
        w, h = self._window.ctx.screen.size
        self.openGlData["projMatrix"] = Matrix44.orthogonal_projection(0, w, h, 0, 1, 0, dtype="f4")

        # TODO : TMP
        # fill static sprite information
        self.__configSprites(0, nbItems)



    def __configSprites(self,time, num_sprites):
        # Grab the size of the screen or current render target
        width, height = self._window.ctx.fbo.size
        # We just create a generator function instead of
        def gen_sprites(time):
            rot_step = math.pi * 2 / num_sprites
            for i in range(num_sprites):
                # Position
#                yield width / 2 + math.sin(time + rot_step * i) * 600
#                yield height / 2 + math.cos(time + rot_step * i) * 300
                yield random.randint(50,width-50)
                yield random.randint(50,height-50)
                # size
                yield 100
                yield 100
                # rotation
                yield math.sin(time + i) * 200
                # Texture position (X,Y,W,H)  (top left corner)
                yield 32
                yield 32
                yield 64
                yield 64

        # TODO : use numpy to improve perfs ?
        # This step is copying data from CPU side to GPU side
        # struct/array python
        self.openGlData["dataBuffer"].write(array("f", gen_sprites(time)))

        # calculate some offset. We truncate to intergers here.
        # This depends what "look" you want for your game.
        scroll_x, scroll_y = int(math.sin(time) * 100), int(math.cos(time) * 100)

        # Grab the size of the screen or current render target
        width, height = self._window.ctx.fbo.size
        # Let's also modify the viewport to scroll the entire screen.
        self.projection = Matrix44.orthogonal_projection(
            scroll_x,  # left
            width + scroll_x,  # right
            height + scroll_y,  # top
            scroll_y,  # bottom
            1,  # near
            -1,  # far
            dtype="f4",  # ensure we create 32 bit value (64 bit is default)
        )

        # CPU to GPU (uniform data)
        self._program["projection"].write(self.openGlData["projMatrix"])
        self._program["sprite_texture"] = 0



    def render(self, time, frame_time):

        #TODO lights
        # uniform buffer objects (for lights ?)
        # lights could be in a texture buffer and we could update this texture buffer ?

        # Clear buffer with background color
        self._window.ctx.clear(
            (math.sin(time + 0) + 1.0) / 2,
            (math.sin(time + 2) + 1.0) / 2,
            (math.sin(time + 3) + 1.0) / 2,
        )

        # Set blitting mode
        # self.ctx.blend_equation  = moderngl.FUNC_SUBTRACT
        # self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        self._window.ctx.enable(moderngl.BLEND)

        # Set the atlas texture to an opengl channel
        # texture channels (up to 16 ?)
        # texture atlas (
        # texture arrays (several layers , same coords)
        # texture that stores information on atlas positions
        # warning take care of borders in case of 2d atlas !! :
        # Use atlas from pyglet (algo to make fits the better)
        # max dim 16k*16k
        # see ctx.info for info
        self.openGlData["staticAtlas"].use(0)

        # Since we have overallocated the buffer (room for 1000 sprites) we
        # need to specify how many we actually want to render passing number of vertices.
        # Also the mode needs to be the same as the geometry shader input type (points!)
        self.openGlData["vao"].render(mode=moderngl.POINTS, vertices=self.openGlData["nbItems"])

        if self._window.ctx.error != "GL_NO_ERROR":
            print(self._window.ctx.error)
            exit()
