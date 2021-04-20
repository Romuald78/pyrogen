import math
import random
from array import array
from pathlib import Path
import numpy as np

import moderngl
import moderngl_window
from moderngl_window import settings, resources
from moderngl_window.meta import TextureDescription
from pyrr import Matrix44

from .opengl_data import OpenGLData




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
        settings.WINDOW['vsync'] = True
        self._window             = moderngl_window.create_window_from_settings()
        print(self._window.ctx.info)

        # Store a list of different programs
        # Only one can be selected at a time
        #the selected program will be used in the prepareData method
        self._program            = None
        self._programs           = {}

        # structure to store all rendering information
        self._openGlData = OpenGLData()

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

    def prepareData(self, loader):
        # -----------------------------------------------------------------
        # TEXTURE ATLAS
        # TODO create texture_array with (width,height,nbLayers)
        # -----------------------------------------------------------------
        # Set image directory
        myPath = Path(__file__).parent.resolve()
        resources.register_dir(myPath)
        # DIFFUSE atlas
        texture = resources.textures.load(TextureDescription(path=loader.getDiffuseAtlasPath()))
        self._openGlData.set("diffuseAtlas", texture)
        # NORMAL atlas
        texture = resources.textures.load(TextureDescription(path=loader.getNormalAtlasPath()))
        self._openGlData.set("normalAtlas", texture)
        # SPECULAR atlas
        texture = resources.textures.load(TextureDescription(path=loader.getSpecularAtlasPath()))
        self._openGlData.set("specularAtlas", texture)


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
        nbTextures       = loader.getNbTextures()
        nbDataPerTexture = 3
        nbDataPerHeader  = 0
        nbComponents     = 4
        width            = nbTextures*nbDataPerTexture
        nbTexels         = width * nbComponents
        overhead         = nbDataPerHeader * nbComponents # 3 values
        # Prepare texture
        texture = self.context.texture((width, 1), nbComponents, dtype="u4")
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # Write texture positions and sizes
        data = np.zeros(nbTexels+overhead, np.uint32)
        i = 0
        allIDs = loader.getAllIds()
        for id in allIDs:
            data[4*id+0] = loader.getTextureById(id)["x"]
            data[4*id+1] = loader.getTextureById(id)["y"]
            data[4*id+2] = loader.getTextureById(id)["w"]
            data[4*id+3] = loader.getTextureById(id)["h"]
        texture.write(data.tobytes())

        # Fill data structure
        self._openGlData.set("nbTextures", nbTextures)
        self._openGlData.set("atlasInfo" , texture   )


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
        self._openGlData.set("nbLights" , nbLights)
        self._openGlData.set("lightInfo", texture )


        # -----------------------------------------------------------------
        # SPRITE BUFFER (VERTEX)
        # -----------------------------------------------------------------
        # Create sprite information (input data)
        nbComponents   = 4
        spriteInfoSize = (5+1) * nbComponents # 6 values in vertex input
        nbMaxSprites   = 185000
        buffer         = self._window.ctx.buffer(reserve=nbMaxSprites * spriteInfoSize)
        self._openGlData.set("spriteSize"  , spriteInfoSize)
        self._openGlData.set("nbSprites"   , nbMaxSprites  )
        self._openGlData.set("spriteBuffer", buffer        )


        # -----------------------------------------------------------------
        # VERTEX ARRAY OBJECT
        # -----------------------------------------------------------------
        # Create vertex array object
        vertexArray = self._window.ctx.vertex_array(
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


        # -----------------------------------------------------------------
        # PROJECTION MATRIX
        # TODO : use this to change viewport (position, size, zoom, rotation, ...)
        # -----------------------------------------------------------------
        # Create projection matrix
        w, h = self._window.ctx.screen.size
        xMin = 0
        xMax = w
        yMin = 0
        yMax = h
        near = 1
        far  = 0
        matrix = Matrix44.orthogonal_projection(xMin, xMax, yMax, yMin, near, far, dtype="f4")
        self._openGlData.set("projMatrix", matrix)


        # TODO : TMP : fill the vertex buffer once at startup
        # fill static sprite information
        self.__configSprites(0, nbMaxSprites, loader)


    def __configSprites(self,time, num_sprites, loader):
        # Grab the size of the screen or current render target
        width, height = self._window.ctx.fbo.size
        # We just create a generator function instead of
        def gen_sprites(time):
            for i in range(num_sprites):
                allIDs = loader.getAllIds()
                spriteID = random.choice(allIDs)
                texture  = loader.getTextureById(spriteID)
                # Position
                yield random.randint(0,width)
                yield random.randint(0,height)
                # size
                yield texture["w"]
                yield texture["h"]
                # rotation
                yield math.sin(time + i) * 100
                # Texture ID (from it, in the ATLAS INFO we can retrieve (X,Y,W,H)
                yield spriteID


        # TODO : use numpy to improve perfs ?
        # This step is copying data from CPU side to GPU side
        # struct/array python
        self._openGlData.get("spriteBuffer").write(array("f", gen_sprites(time)))

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
        matrix = self._openGlData.get("projMatrix")
        self._program["projection"].write( matrix )

        #TODO : remove it definitely and read the atlasInfo to know from where getting textures
        self._program["atlasDataID"] = [2,3,4]
        self._program["atlasInfoID"] = 0



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
        self._openGlData.get("atlasInfo"    ).use(0)
        self._openGlData.get("lightInfo"    ).use(1)
        self._openGlData.get("diffuseAtlas" ).use(2)
        self._openGlData.get("normalAtlas"  ).use(3)
        self._openGlData.get("specularAtlas").use(4)

        # Since we have overallocated the buffer (room for 1000 sprites) we
        # need to specify how many we actually want to render passing number of vertices.
        # Also the mode needs to be the same as the geometry shader input type (points!)
        self._openGlData.get("vao").render(mode=moderngl.POINTS, vertices=self._openGlData.get("nbSprites"))

        if self._window.ctx.error != "GL_NO_ERROR":
            print("[ERROR] during rendering...")
            print(self._window.ctx.error)
            exit()
