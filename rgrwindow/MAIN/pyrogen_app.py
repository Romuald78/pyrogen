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
        self.openGlData = {
                            # Atlas texture
                            "diffuseAtlas" : None,  # ALL sprite texture (sprite/diffuse)
                            "normalAtlas"  : None,  # ALL sprite texture (normal)
                            "specularAtlas": None,  # ALL sprite texture (specular)

                            "nbTextures"   : None,  # integer
                            "atlasInfo"    : None,  # Texture containing all texture information

                            "nbLights"     : None,  # integer
                            "lightInfo"    : None,  # Texture containing all light information

                            "nbSprites"    : None,  # integer (number of vertices)
                            "spriteSize"   : None,  # integer (data size for one vertex)
                            "spriteBuffer" : None,  # vertex buffer

                            "vao"          : None,  # Vertex array object
                            "projMatrix"   : None,  # Projection matrix (used for camera feature)
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
        # -----------------------------------------------------------------
        # TEXTURE ATLAS
        # TODO create texture_array with (width,height,nbLayers)
        # -----------------------------------------------------------------
        # Set image directory
        myPath = Path(__file__).parent.resolve()
        resources.register_dir(myPath)
        # DIFFUSE atlas
        texture = resources.textures.load(TextureDescription(path="atlas.png"))
        self.openGlData["diffuseAtlas"] = texture
        # NORMAL atlas
        texture = resources.textures.load(TextureDescription(path="atlas.png"))
        self.openGlData["normalAtlas"] = texture
        # SPECULAR atlas
        texture = resources.textures.load(TextureDescription(path="atlas.png"))
        self.openGlData["specularAtlas"] = texture


        # -----------------------------------------------------------------
        # ATLAS INFO
        # -----------------------------------------------------------------
        # Set texture to contain all texture info (needed to access atlas data)
        # Write Pyrogen Texture data (20 x 32bit values)
        # Pack values using the nb of components
        # e.g.  X,Y,W,H packed in a single RGBA value
        # texelFecth() function to get them from GPU side
        # texture.filter = moderngl.NEAREST, moderngl.NEAREST
        #
        # [ONCE]
        # > Diffuse info
        #    - channelID
        #    - samplerID
        #    - array Index (0 for the moment)
        #    - RFU
        # > Normal info
        #    - channelID
        #    - samplerID
        #    - array Index
        #    - RFU
        # > Specular info
        #    - channelID
        #    - samplerID
        #    - array Index
        #    - RFU
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
        nbTextures       = 2
        nbDataPerTexture = 3
        nbDataPerHeader  = 3
        nbComponents     = 4
        width            = nbTextures*nbDataPerTexture
        nbBytes          = width * nbComponents
        overhead         = nbDataPerHeader * nbComponents # 3 values
        texture = self.context.texture((width+nbDataPerHeader, 1), nbComponents, dtype="u4")
        buffer  = self.context.buffer(reserve=nbBytes+overhead)

   ### TODO !!     texture.write(buffer)

        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.openGlData["nbTextures"] = nbTextures
        self.openGlData["atlasInfo" ] = texture


        # -----------------------------------------------------------------
        # LIGHT INFO (circular lights)
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
        nbComponents    = 4
        nbLights        = 2
        textureInfoSize = 2 * nbComponents # 2 values (4 components)
        overhead        = 1 * nbComponents # 1 value
        texture = self.context.texture((nbLights*textureInfoSize + overhead, 1), nbComponents, dtype="u4")

        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.openGlData["nbLights"]  = nbLights
        self.openGlData["lightInfo"] = texture


        # -----------------------------------------------------------------
        # SPRITE BUFFER (VERTEX)
        # -----------------------------------------------------------------
        # Create sprite information (input data)
        nbComponents   = 4
        spriteInfoSize = (5+4) * nbComponents # 9 values in vertex input
        nbMaxSprites   = 1000
        self.openGlData["spriteSize"  ] = spriteInfoSize
        self.openGlData["nbSprites"   ] = nbMaxSprites
        self.openGlData["spriteBuffer"] = self._window.ctx.buffer(reserve=nbMaxSprites * spriteInfoSize)


        # -----------------------------------------------------------------
        # VERTEX ARRAY OBJECT
        # -----------------------------------------------------------------
        # Create vertex array object
        self.openGlData["vao"]        = self._window.ctx.vertex_array(
            self._program,
            [
                (self.openGlData["spriteBuffer"], "2f 2f 1f 4f", "in_position", "in_size", "in_rotation", "in_atlas_pos"),
            ]
        )


        # -----------------------------------------------------------------
        # PROJECTION MATRIX
        # TODO : use this to change viewport (position, size, zoom, rotation, ...)
        # -----------------------------------------------------------------
        # Create projection matrix
        w, h = self._window.ctx.screen.size
        border = 100
        xMin = 0-border
        xMax = w+border
        yMin = 0-border
        yMax = h+border
        near = 1
        far  = 0
        self.openGlData["projMatrix"] = Matrix44.orthogonal_projection(xMin, xMax, yMax, yMin, near, far, dtype="f4")





        # TODO : TMP : fill the vertex buffer once at startup
        # fill static sprite information
        self.__configSprites(0, nbMaxSprites)



    def __configSprites(self,time, num_sprites):
        # Grab the size of the screen or current render target
        width, height = self._window.ctx.fbo.size
        # We just create a generator function instead of
        def gen_sprites(time):
            rot_step = math.pi * 2 / num_sprites
            for i in range(num_sprites):
                spriteID = random.randint(0,1)
                # Position
#                yield width / 2 + math.sin(time + rot_step * i) * 600
#                yield height / 2 + math.cos(time + rot_step * i) * 300
                yield random.randint(50,width-50)
                yield random.randint(50,height-50)
                # size
                yield 250
                yield 250
                # rotation
                yield math.sin(time + i) * 100
                # Texture position (X,Y,W,H)  (top left corner)
                yield [32,2 ][spriteID]
                yield [32,2 ][spriteID]
                yield [64,27][spriteID]
                yield [64,27][spriteID]

        # TODO : use numpy to improve perfs ?
        # This step is copying data from CPU side to GPU side
        # struct/array python
        self.openGlData["spriteBuffer"].write(array("f", gen_sprites(time)))

        ## calculate some offset. We truncate to intergers here.
        ## This depends what "look" you want for your game.
        #scroll_x, scroll_y = int(math.sin(time) * 100), int(math.cos(time) * 100)
        # Grab the size of the screen or current render target
        #width, height = self._window.ctx.fbo.size
        # Let's also modify the viewport to scroll the entire screen.
        #self.projection = Matrix44.orthogonal_projection(
        #    scroll_x,  # left
        #    width + scroll_x,  # right
        #    height + scroll_y,  # top
        #    scroll_y,  # bottom
        #    1,  # near
        #    -1,  # far
        #    dtype="f4",  # ensure we create 32 bit value (64 bit is default)
        #)

        # CPU to GPU (uniform data)
        self._program["projection"].write(self.openGlData["projMatrix"])

        #TODO : remove it definitely and read the atlasInfo to know from where getting textures
        self._program["sprite_texture"] = 1



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
        self.openGlData["atlasInfo"    ].use(0)
        self.openGlData["diffuseAtlas" ].use(1)
        self.openGlData["normalAtlas"  ].use(2)
        self.openGlData["specularAtlas"].use(3)
        self.openGlData["lightInfo"    ].use(4)

        # Since we have overallocated the buffer (room for 1000 sprites) we
        # need to specify how many we actually want to render passing number of vertices.
        # Also the mode needs to be the same as the geometry shader input type (points!)
        self.openGlData["vao"].render(mode=moderngl.POINTS, vertices=self.openGlData["nbSprites"])

        if self._window.ctx.error != "GL_NO_ERROR":
            print("[ERROR] during rendering...")
            print(self._window.ctx.error)
            exit()
