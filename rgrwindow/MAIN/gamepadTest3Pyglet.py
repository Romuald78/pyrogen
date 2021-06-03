import math
from array import array
from pathlib import Path
import random

import numpy as np
import moderngl
import moderngl_window
import pyglet
from pyrr import Matrix44

from pyrogen.src.pyrogen.ecs.shaders.simple_shader import SimpleShader
from pyrogen.src.pyrogen.rgrwindow.MAIN.fsgpu.fs_gpu import FsGpu
from pyrogen.src.pyrogen.rgrwindow.MAIN.fsgpu2.fsgpu_buffer import FsGpuBuffer
from pyrogen.src.pyrogen.rgrwindow.MAIN.fsgpu2.fsgpu_main import FsGpuMain
from pyrogen.src.pyrogen.rgrwindow.MAIN.gfx_components import GfxSprite, Gfx
from pyrogen.src.pyrogen.rgrwindow.MAIN.loader import ResourceLoader
from pyrogen.src.pyrogen.rgrwindow.MAIN.opengl_data import OpenGLData



# ========================================================
# DEBUG PARAMS
# ========================================================
DEBUG_NB_SPRITES     = 3000
DEBUG_MOVING_SPRITES = True
DEBUG_DISPLAY_QUERY  = False



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

        # Init sprite Manager (debug only for the moment)
        self._spriteMgr = SpriteMgr()

        # Profiling
        self._FPS = []


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
    # VIEWPORT CONFIGURATION
    # ========================================================================
    def _setViewPort(self, x0, y0, x1, y1):
        near = 1
        far  = 0
        matrix = Matrix44.orthogonal_projection(x0, x1, y1, y0, near, far, dtype="f4")
        self._openGlData.set("projMatrix", matrix)
        # CPU to GPU (uniform data)
        matrix = self._openGlData.get("projMatrix")
        self._program["projection"].write( matrix )


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
        nbMaxSprites = DEBUG_NB_SPRITES
        buffer = self.ctx.buffer(reserve=nbMaxSprites * spriteInfoSize)
        self._openGlData.set("spriteSize", spriteInfoSize)
        self._openGlData.set("nbSprites", nbMaxSprites)
        self._openGlData.set("vertexBuffer", buffer)

        # -----------------------------------------------------------------
        # VIEWPORT
        # -----------------------------------------------------------------
        # Change view port (for static sprites)
        w, h = self.ctx.screen.size
        self._setViewPort(0, 0, w, h)

        # -----------------------------------------------------------------
        # VERTEX ARRAY OBJECT
        # -----------------------------------------------------------------
        # Create vertex array object
        vertexArray = self.ctx.vertex_array(
                        self._program,
                        [
                            (self._openGlData.get("vertexBuffer"),
                             "2f 2f 1f 1f",
                             "in_position",
                             "in_size",
                             "in_rotation",
                             "in_tex_id"),
                        ]
                    )
        self._openGlData.set("vao", vertexArray)

        # -----------------------------------------------------------------
        # UNIFORMS DATA
        # -----------------------------------------------------------------
        # Uniform data to know from which channel the data can be read
        # - atlas texture Information (where are located the sprites)
        # - atlas texture (sprites)
        self._program["atlasTextureID"] = PyrogenApp3.CHANNEL_ATLAS_TEXTURE
        self._program["atlasInfoID"   ] = PyrogenApp3.CHANNEL_ATLAS_INFO

        # -----------------------------------------------------------------
        # PREPARE SPRITE DATA
        # -----------------------------------------------------------------
        # Prepare sprites
        self._spriteMgr.createRandomSprites(self._loader, DEBUG_NB_SPRITES, (self.width,self.height))
        vd = array("f", self._spriteMgr.genVertex())
        self._openGlData.set("vertexData", vd)
        # write into GPU for the first time
        self._openGlData.get("vertexBuffer").write(vd)

        # -----------------------------------------------------------------
        # PROFILING
        # -----------------------------------------------------------------
        # Query configuration for profiling
        self._query = self.ctx.query(samples=True, time=True, primitives=True)

        # -----------------------------------------------------------------
        # GPU FILE SYSTEM
        # -----------------------------------------------------------------
        # -----------------------------------------------------------------
        # FILE SYSTEM
        # TODO : use the gpu device max texture size property instead of hard-coded size
        # the height indicates number of pages
        # the width the size of each 1-height FSGpuBuffer
        # the static sprites could be stored in the last pages
        # the dynamic ones could be stores in the first pages
        # -----------------------------------------------------------------
        # Data area
        sizeW        = 32*1024
        sizeH        = 10
        nbComponents = 4
        texture = self.ctx.texture((sizeW, sizeH), nbComponents, dtype="f4")

        # instanciate FsGpu
        self._fsgpu = FsGpuMain(self.ctx, sizeW, sizeH)

        self._fsgpu.test002()

        exit()







    # ========================================================
    # UPDATE METHOD
    # ========================================================
    def update(self, deltaTime):
        self._FPS.append(deltaTime)
        if len(self._FPS)==60:
            print(60/sum(self._FPS))
            self._FPS = []
        self.time += deltaTime

        # update moving sprites if needed
        if DEBUG_MOVING_SPRITES:
            self._spriteMgr.updateMovingSprites(self.time, (self.width, self.height))

        # update viewport if not moving sprites
        if not DEBUG_MOVING_SPRITES:
            squareSize = int(round(math.sqrt(DEBUG_NB_SPRITES), 0))
            w, h = self.ctx.screen.size
            a = math.cos(self.time / 19) * math.cos(3 * self.time / 10)
            a = a * a
            zoom = 6 * a + 0.25  # zoom beween 0.25 and 6.25
            W2 = (squareSize*32) - w*zoom + 64
            H2 = (squareSize*32) - h*zoom + 64
            x0 = int((0.5*math.cos(self.time / 31) + 0.5) * W2) - 48
            y0 = int((0.5*math.sin(self.time / 29) + 0.5) * H2) - 48
            w   *= zoom
            h   *= zoom
            self._setViewPort( x0, y0, x0+w, y0+h )


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

        # Write sprite info into the vertex array
        # TODO :
        # next step when using the GPU File System, we will have only block IDs
        # in this vertexbuffer. So only when order modification occurs, it will be reloaded
        # into the GPU
        # The file system must be splitted in several "pages", so we can gather all
        # moving sprites in the same pages, it will reduce the number of writing operations
        # TODO : debug for the moment, just rewrite in case of MOVING SPRITES
        if DEBUG_MOVING_SPRITES:
            vd = array("f", self._spriteMgr.genVertex())
            self._openGlData.set("vertexData", vd)

        # In all cases, write vertex buffer to GPU
        vd = self._openGlData.get("vertexData")
        self._openGlData.get("vertexBuffer").write(vd)

        # Process rendering
        with self._query:
            # TODO | Since we overallocat the buffer (room for 1000 sprites) we
            # TODO | need to specify how many we actually want to render passing number of vertices.
            # TODO | Also the mode needs to be the same as the geometry shader input type (points!)
            self._openGlData.get("vao").render(mode=moderngl.POINTS, vertices=self._openGlData.get("nbSprites"))

            if self.ctx.error != "GL_NO_ERROR":
                print("[ERROR] during rendering...")
                print(self.ctx.error)
                exit()



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

        # Load the loader ref into the Gfx class (static member)
        Gfx.setLoader(self._loader)

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





class SpriteMgr():

    def __init__(self):
        self._sprites = []

    def createRandomSprites(self, loader, N, winSize):
        squareSize = int(round(math.sqrt(DEBUG_NB_SPRITES),0))
        for i in range(N):
            allIDs  = loader.getAllIds()
            id      = random.choice(allIDs)
            texture = loader.getTextureById(id)
            # -----------------------------
            # Name
            name = texture["name"]
            # Position
            x = (i  % squareSize) * 32
            y = (i // squareSize) * 32
            # rotation
            angle = 0
            #Sprite creation
            sprite  = GfxSprite(name,x=x, y=y, angle=angle)
            self._sprites.append(sprite)

    def updateMovingSprites(self, time, winSize):
        seed = 123456789
        random.seed(seed)
        for i in range(len(self._sprites)):
            randI = (i+1)/len(self._sprites)
            spr = self._sprites[i]
            # Position...
            spr.x = (math.cos(time*randI*4) * randI * winSize[0]/2) + (winSize[0]/2)
            spr.y = (math.sin(time*randI*4) * randI * winSize[1]/2) + (winSize[1]/2)
            # ...and scale (for moving sprites)
            spr.scale = randI*1.25 + 0.25
            # rotation
            spr.angle = math.sin(time + i) * 180

    def genVertex(self):
        for i in range(len(self._sprites)):
            spr = self._sprites[i]
            yield spr.x
            yield spr.y
            yield spr.width
            yield spr.height
            yield spr.angle
            yield spr.textureID





if __name__ == '__main__':
    # instanciate Pyrogen application
    app = PyrogenApp3(width=1280, height=720)
    # and run it
    app.run()










