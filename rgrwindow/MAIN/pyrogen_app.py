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

from pyrogen.src.pyrogen.rgrwindow.MAIN.gfx_components import Gfx, GfxSprite
from .opengl_data import OpenGLData


# -----------------------------------
# STATIC SPRITES
# -----------------------------------
#DEBUG_SIZE           = 1024
#DEBUG_NB_SPRITES     = DEBUG_SIZE * DEBUG_SIZE
#DEBUG_MOVING_SPRITES = False
#DEBUG_DISPLAY_QUERY  = False


# -----------------------------------
# DYNAMIC SPRITES
# -----------------------------------
DEBUG_SIZE           = 55
DEBUG_NB_SPRITES     = DEBUG_SIZE * DEBUG_SIZE
DEBUG_MOVING_SPRITES = True
DEBUG_DISPLAY_QUERY  = False


# TODO -----------------------------------------------------------------
# TODO : is there a duplication between spriteBuffer and vertexData ????
# TODO -----------------------------------------------------------------


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
    def __init__(self, loader, size=(1280,720)):
        # Create a Pyglet window
        settings.WINDOW['class'] = 'moderngl_window.context.pyglet.Window'
        settings.WINDOW['vsync'] = not DEBUG_DISPLAY_QUERY
        settings.WINDOW['size' ] = size
        self._window             = moderngl_window.create_window_from_settings()
        print(self._window.ctx.info)

#        self._window.fullscreen = True

        # Store resource loader
        self._loader = loader

        # Store static loader ref in Gfx class
        Gfx.setLoader(self._loader)


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

    def prepareData(self):
        # -----------------------------------------------------------------
        # TEXTURE ATLAS
        # TODO create texture_array with (width,height,nbLayers)
        # -----------------------------------------------------------------
        # Set image directory
        myPath = Path(__file__).parent.resolve()
        resources.register_dir(myPath)
        # DIFFUSE atlas
        texture = resources.textures.load(TextureDescription(path=self._loader.getDiffuseAtlasPath()))
        self._openGlData.set("diffuseAtlas", texture)
        # NORMAL atlas
        texture = resources.textures.load(TextureDescription(path=self._loader.getNormalAtlasPath()))
        self._openGlData.set("normalAtlas", texture)
        # SPECULAR atlas
        texture = resources.textures.load(TextureDescription(path=self._loader.getSpecularAtlasPath()))
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
        nbTextures       = self._loader.getNbTextures()
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
        nbMaxSprites   = DEBUG_NB_SPRITES
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



        # CREATE SPRITE LIST
        self._createSprites(nbMaxSprites, self._loader)


        # CREATE SPRITE VERTEX ARRAY
        # This step is filling the array
        # and copying it from CPU side to GPU side
        # TODO : use numpy to improve perfs instead of shapely array?
        vertexData = array("f", self._genVertex())
        self._openGlData.set("vertexData", vertexData)
        self._openGlData.get("spriteBuffer").write(self._openGlData.get("vertexData"))



        # -----------------------------------------------------------------
        # PROJECTION MATRIX
        # TODO : use this to change viewport (position, size, zoom, rotation, ...)
        # TODO : handle rotation
        # -----------------------------------------------------------------
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
        # Create projection matrix (and set uniform data)
        w, h = self._window.ctx.screen.size
        xMin = 0
        xMax = w
        yMin = 0
        yMax = h
        self.setViewPort(xMin, yMin, xMax, yMax)



        # -----------------------------------------------------------------
        # UNIFORMS DATA
        # -----------------------------------------------------------------
        # Uniform data to know from which channel the atlas can be read
        self._program["atlasDataID"] = [2,3,4]
        self._program["atlasInfoID"] = 0



        # Query configuration for profiling
        self._query = self._window.ctx.query(samples=True, time=True, primitives=True)






    def setViewPort(self, x0, y0, x1, y1):
        near = 1
        far  = 0
        matrix = Matrix44.orthogonal_projection(x0, x1, y0, y1, near, far, dtype="f4")
        self._openGlData.set("projMatrix", matrix)
        # CPU to GPU (uniform data)
        matrix = self._openGlData.get("projMatrix")
        self._program["projection"].write( matrix )


    def _createSprites(self, nbSprites, loader):
        self._sprites = []
        for i in range(nbSprites):
            randI   = (i + 1) / nbSprites
            allIDs  = loader.getAllIds()
            id      = random.choice(allIDs)
            texture = loader.getTextureById(id)
            # -----------------------------
            # Name
            name = texture["name"]
            # Position
            if not DEBUG_MOVING_SPRITES:
                x = (i  % DEBUG_SIZE) * 32
                y = (i // DEBUG_SIZE) * 32
            else:
                x = (math.cos(0) * randI * 16 * DEBUG_SIZE) + (32 * DEBUG_SIZE / 2)
                y = (math.sin(0) * randI * 16 * DEBUG_SIZE) + (32 * DEBUG_SIZE / 2)
            # rotation
            angle = math.sin(0 + i) * 180
            #Sprite creation
            sprite  = GfxSprite(name,x=x, y=y, angle=angle)
            self._sprites.append(sprite)

        # Update vertexData for all sprites
        self._openGlData.set("vertexData", array("f", self._genVertex()) )



    def _updateSprites(self, time):

        seed = 123456789
        random.seed(seed)

        for i in range(len(self._sprites)):
            randI = (i+1)/len(self._sprites)
            spr = self._sprites[i]
            # Position
            if not DEBUG_MOVING_SPRITES:
                spr.centerX = (i %  DEBUG_SIZE) * 32
                spr.centerY = (i // DEBUG_SIZE) * 32
            else:
                spr.centerX = (math.cos(time*randI*4) * randI * 16 * DEBUG_SIZE) + (self._window.width//2 )
                spr.centerY = (math.sin(time*randI*4) * randI * 8 * DEBUG_SIZE ) + (self._window.height//2)
            # size/scale
            # ...
            # rotation
            spr.angle = math.sin(time + i) * 180

        # Update vertexData for all sprites
        self._openGlData.set("vertexData", array("f", self._genVertex()) )


    def _genVertex(self):

        for i in range(len(self._sprites)):
            spr = self._sprites[i]
            yield spr.centerX
            yield spr.centerY
            yield spr.width
            yield spr.height
            yield spr.angle
            yield spr.textureID


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



        # Update all sprites once again (update method)
        if DEBUG_MOVING_SPRITES:
            self._updateSprites(time)


        # Write all sprite data
        self._openGlData.get("spriteBuffer").write(self._openGlData.get("vertexData"))


        # Change view port (for static sprites)
        w, h = self._window.ctx.screen.size
        zoom = 1.0
        x0 = -16
        y0 = -16
        if not DEBUG_MOVING_SPRITES:
            a = math.cos(time / 10) * math.cos(3 * time / 10)
            b = a * a
            zoom = 6 * b + 0.25  # zoom beween 0.25 and 6.25
            x0   = int( (0.5 * math.cos(time / 40) + 0.5) * 32 * DEBUG_SIZE ) - 16 - zoom * (w // 2)
            y0   = int( (0.5 * math.sin(time / 40) + 0.5) * 32 * DEBUG_SIZE ) - 16 - zoom * (h // 2)
        w   *= zoom
        h   *= zoom
        self.setViewPort( x0, y0, x0+w, y0+h )





        with self._query:

            # Since we have overallocated the buffer (room for 1000 sprites) we
            # need to specify how many we actually want to render passing number of vertices.
            # Also the mode needs to be the same as the geometry shader input type (points!)
            self._openGlData.get("vao").render(mode=moderngl.POINTS, vertices=self._openGlData.get("nbSprites"))

            if self._window.ctx.error != "GL_NO_ERROR":
                print("[ERROR] during rendering...")
                print(self._window.ctx.error)
                exit()


        if DEBUG_DISPLAY_QUERY:
            print()
            print(f"{self._query.elapsed/1000} usec.")
            print(f"{self._query.samples} samples")
            print(f"{self._query.primitives} primitives")
            fillRatio = self._query.samples/(self._window.width*self._window.height*4)
            print(f"ratio={fillRatio}")
