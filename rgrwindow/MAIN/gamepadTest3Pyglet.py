import cProfile
import math
import os
from array import array
import random
from time import time as tm

import numpy as np
import moderngl
import moderngl_window
import pyglet
from pyrr import Matrix44

from pyrogen.src.pyrogen.ecs.shaders.simple_shader import SimpleShader
from pyrogen.src.pyrogen.ecs.file_system.fsgpu_main import FsGpuMain
from pyrogen.src.pyrogen.rgrwindow.MAIN.gfx_components import GfxSprite, Gfx
from pyrogen.src.pyrogen.rgrwindow.MAIN.loader import ResourceLoader
from pyrogen.src.pyrogen.rgrwindow.MAIN.opengl_data import OpenGLData



# ========================================================
# DEBUG PARAMS
# 3000 sprites => 20fps
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
    CHANNEL_FILE_SYSTEM   = 5
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
            self._fsgpu.display()
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

        #for field in self.ctx.info:
        #    print(f"{field} : {self.ctx.info[field]}")

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
    def __setViewPort(self, x0, y0, x1, y1):
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
        spriteInfoSize = (1) * nbComponents  # 1 value in vertex input per sprite (the File System id)
        nbMaxSprites   = DEBUG_NB_SPRITES
        buffer = self.ctx.buffer(reserve=nbMaxSprites * spriteInfoSize)
        self._openGlData.set("spriteSize", spriteInfoSize)
        self._openGlData.set("nbSprites", nbMaxSprites)
        self._openGlData.set("vertexBuffer", buffer)

        # -----------------------------------------------------------------
        # VIEWPORT
        # -----------------------------------------------------------------
        # Change view port (for static sprites)
        w, h = self.ctx.screen.size
        self.__setViewPort(0, 0, w, h)

        # -----------------------------------------------------------------
        # VERTEX ARRAY OBJECT
        # -----------------------------------------------------------------
        # Create vertex array object
        vertexArray = self.ctx.vertex_array(
                        self._program,
                        [
                            (self._openGlData.get("vertexBuffer"),
                             "1u",
                             "blockID"),
                        ]
                    )
        self._openGlData.set("vao", vertexArray)


        # -----------------------------------------------------------------
        # UNIFORMS DATA
        # -----------------------------------------------------------------
        # Uniform data to know from which channel the data can be read
        # - atlas texture Information (where are located the sprites)
        # - atlas texture (sprites)
        self._program["atlasTextureChan"] = PyrogenApp3.CHANNEL_ATLAS_TEXTURE
        self._program["atlasInfoChan"   ] = PyrogenApp3.CHANNEL_ATLAS_INFO
        self._program["fsGpuChan"       ] = PyrogenApp3.CHANNEL_FILE_SYSTEM

        # -----------------------------------------------------------------
        # GPU FILE SYSTEM
        # -----------------------------------------------------------------
        # TODO : use the gpu device max texture size property instead of hard-coded size
        # the height indicates number of pages
        # the width the size of each 1-height FSGpuBuffer
        # the static sprites could be stored in the last pages
        # the dynamic ones could be stores in the first pages
        # -----------------------------------------------------------------
        # Data area = Width * Height * number of components (4 float)
        sizeW        =  1024
        sizeH        =  512
        # instanciate FsGpu
        print(f"Creating FS MAIN with size={sizeW}/{sizeH} 32-bit-float-values")
        self._fsgpu = FsGpuMain(self.ctx, sizeW, sizeH)
        self._openGlData.set("fsGpu", self._fsgpu.getTexture())

        # -----------------------------------------------------------------
        # PROFILING
        # -----------------------------------------------------------------
        # Query configuration for profiling
        self._query = self.ctx.query(samples=True, time=True, primitives=True)

        # -----------------------------------------------------------------
        # PREPARE SPRITE DATA
        # -----------------------------------------------------------------
        # Prepare sprites
        self._spriteMgr.createRandomSprites(self._loader, DEBUG_NB_SPRITES, self._fsgpu)
        vd = array("l", self._spriteMgr.genVertex())
        self._openGlData.set("vertexData", vd)
        # write into GPU for the first time
        self._openGlData.get("vertexBuffer").write(vd)


    # ========================================================
    # UPDATE METHOD
    # ========================================================
    def update(self, deltaTime):
        # increase current application time
        self.time += deltaTime

        # TODO ---------------- remove (DEBUG) --------------------------
        # update moving sprites if needed
        if DEBUG_MOVING_SPRITES:
            self._spriteMgr.updateMovingSprites(self.time, (self.width, self.height))

        # Process File system
        self._fsgpu.update(deltaTime)

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
            self.__setViewPort( x0, y0, x0+w, y0+h )

        # Process FPS
        self._FPS.append(deltaTime)
        if len(self._FPS)==60:
            print(f">>>>>>>>>>>>> FPS = {60/sum(self._FPS)} <<<<<<<<<<<<<<<<<<<<<<<")
            self._FPS = []


    # ========================================================
    # RENDER METHOD
    # ========================================================
    def on_draw(self):
        # update file system texture
        self._fsgpu.render()
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
        self._openGlData.get("atlasInfo"   ).use(PyrogenApp3.CHANNEL_ATLAS_INFO)
        self._openGlData.get("textureAtlas").use(PyrogenApp3.CHANNEL_ATLAS_TEXTURE)
        self._openGlData.get("fsGpu"       ).use(PyrogenApp3.CHANNEL_FILE_SYSTEM)
        self._openGlData.get("lightInfo"   ).use(PyrogenApp3.CHANNEL_LIGHTS)

        # Write sprite info into the vertex array
        # TODO :
        # next step when using the GPU File System, we will have only block IDs
        # in this vertexbuffer. So only when order modification occurs, it will be reloaded
        # into the GPU
        # The file system must be splitted in several "pages", so we can gather all
        # moving sprites in the same pages, it will reduce the number of writing operations
        # TODO : debug for the moment, just rewrite in case of MOVING SPRITES
        if DEBUG_MOVING_SPRITES:
            vd = array("l", self._spriteMgr.genVertex())
            self._openGlData.set("vertexData", vd)

        # In all cases, write vertex buffer to GPU
        vd = self._openGlData.get("vertexData")
        self._openGlData.get("vertexBuffer").write(vd)

        # Process rendering
        with self._query:
            # TODO | Since we overallocat the buffer we need to specify how many
            # TODO | we actually wantto render passing number of vertices.
            # TODO | Also the mode needs to be the same as the geometry shader input type (points!)
            self._openGlData.get("vao").render(mode=moderngl.POINTS, vertices=self._openGlData.get("nbSprites"))

            if self.ctx.error != "GL_NO_ERROR":
                print("[ERROR] during rendering...")
                print(self.ctx.error)
                exit()

        #print("============= RENDER =================")
        #print(f"GPU Render          = {round(1000*(lap2-lap1),2)}ms")
        #print(f"GL config 1         = {round(1000*(lap3-lap2),2)}ms")
        #print(f"Vertex array update = {round(1000*(lap4-lap3),2)}ms")
        #print(f"Render              = {round(1000*(lap5-lap4),2)}ms")

    # TODO
    # def on_resize(self, width, height):
    #    self.ctx.screen.viewport = 0, 0, *self.get_framebuffer_size()


    # ========================================================
    # MAIN LOOP
    # ========================================================
    def run(self):

#        # BUFFER DEBUG PERF TEST
#        perfTest()
#        exit()

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

        # Start pyglet app and profile it
        # cProfile.runctx('pyglet.app.run()', globals(), None)
        cpr = cProfile.Profile()
        cpr.enable()
        pyglet.app.run()
        cpr.disable()

        # List methods under supervision
        watchMethods = [
                    "render",
                    "update",
                    "updateMovingSprites",
                    "write",
                    "_write",
                    "_verifCHK",
                    "_computeCHK",
                    "_explodeID",
                    "genVertex",
                    "writeBlock",
                    "getData",
                    "on_draw"
                    ]
        watchFiles = ["gfx_components",
        ]

        # Get stats of execution : parse them
        st = cpr.getstats()
        out = []
        for row in st:
            # Prepare data
            code   = str(row[0])
            code   = code.replace("code object ","")
            code   = code.replace("built-in ","")
            code   = code.replace("method ","")
            code   = code.replace(" objects","")
            code   = code.replace("<","")
            code   = code.replace(">","")
            code   = code.split(",")
            method = code[0].split(" ")[0]
            file   = code[1] if len(code)>1 else ""
            file   = file.replace("file", "")
            file   = file.replace("\"","")
#            file   = os.path.basename(file).split(".")[0]
            line   = code[2] if len(code)>2 else ""
            line   = line.lower().replace("line ","")
            # store data
            toBeStored = False
            for w in method.split(" "):
                if w in watchMethods:
                    toBeStored = True
                    break
            if file in watchFiles:
                toBeStored = True

            toBeStored = True

            if toBeStored:
                out.append( {"method"    : method,
                             "file"      : file,
                             "line"      : line,
                             "ncalls"    : str(row[1]).replace(".",","),
                             "tottime"   : str(1000*row[4]).replace(".",","),
                             "totpercall": str(1000*row[4] / row[1]).replace(".",","),
                             "cumtime"   : str(1000*row[3]).replace(".",","),
                             "cumpercall": str(1000*row[3] / row[1]).replace(".",","),
                             } )

        out = sorted( out, key=lambda x:(x["file"],x["method"]) )
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



class SpriteMgr():

    __slots__ = ["_sprites",
                 "_dbgTime",
                 "_N",
                 ]

    def __init__(self):
        self._sprites = []

    def createRandomSprites(self, loader, N, fsgpu):
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
            angle = random.randint(0,360)
            #Sprite creation
            sprite  = GfxSprite(name,x=x, y=y, angle=angle, fsgpu=fsgpu)
            self._sprites.append(sprite)
        self._dbgTime = 0
        self._N = 0

    def updateMovingSprites(self, currentTime, winSize):
        i = 0
        L = len(self._sprites)
        for spr in self._sprites:
            # init vars
            randI = (i+1)/L
            hw = winSize[0]/2
            hh = winSize[1]/2
            t  = currentTime * randI * 4

            # Position...
            x   = (math.cos(t) * randI * hw) + hw
            y   = (math.sin(t) * randI * hh) + hh
            #x = 32 * (i%33)
            #y = 32 * (i//33)
            spr.setX( x )
            spr.setY( y )

            # ...and scale (for moving sprites)
            scl = randI * 1.25 + 0.25
            spr.setScale( scl )

            # rotation
            ang =  math.sin(currentTime + i) * 180
            spr.setAngle( ang )

            # update sprite (that will generate a writing to the FS
            spr.update(1/60)
            # increase i
            i += 1

    def genVertex(self):
        for i in range(len(self._sprites)):
            spr = self._sprites[i]
            yield spr.getBlockID()





def perfTest():

    # array write time measurement
    # Big buffer, small writing operation
    BUFF_SIZE = 1000000
    DATA_SIZE = 16
    NB_TESTS  = 1000000
    # Create data to copy
    DATA = [10.1+x for x in range(DATA_SIZE)]
    print(f"NB TESTS           = {NB_TESTS}")

    # Test buffer numpy
    buffer1 = np.zeros(BUFF_SIZE, np.float32)
    time1 = 0
    for n in range(NB_TESTS):
        # Random offset for the buffer writing
        start = random.randint(0,BUFF_SIZE-DATA_SIZE)
        end   = start + DATA_SIZE
        # Writing operation
        lap1 = tm()
        buffer1[start:end] = DATA
        lap2 = tm()
        # Compute time
        time1 += lap2 - lap1
    print(f"TOTAL TIME (numpy) = {time1}")

    # Test buffer (python list)
    buffer1 = [0.0,] * DATA_SIZE
    time1 = 0
    for n in range(NB_TESTS):
        # Random offset for the buffer writing
        start = random.randint(0,BUFF_SIZE-DATA_SIZE)
        end   = start + DATA_SIZE
        # Writing operation
        lap1 = tm()
        buffer1[start:end] = DATA
        lap2 = tm()
        # Compute time
        time1 += lap2 - lap1
    print(f"TOTAL TIME (list)  = {time1}")
