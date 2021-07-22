import math
from array import array

import moderngl
import moderngl_window
import pyglet
from pyrr import Matrix44

from pyrogen.src.pyrogen.ecs3.components.gfx import Gfx
from pyrogen.src.pyrogen.ecs3.gpu.fsgpu_main import FsGpuMain
from pyrogen.src.pyrogen.ecs3.shaders.simple_shader import SimpleShader
from pyrogen.src.pyrogen.ecs3.systems.gfx_system import GfxSystem


class OpenGLData():

    # ========================================================
    #  PARAMETERS
    # ========================================================
    DEBUG_DISPLAY_QUERY   = False
    DEBUG_DISPLAY_FSGPU   = False
    CHANNEL_ATLAS_INFO    = 0
    CHANNEL_ATLAS_TEXTURE = 1
    CHANNEL_FILE_SYSTEM   = 2


    # ========================================================================
    #  PRIVATE METHODS
    # ========================================================================
    def _initCfg(self):
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
        self.ctx = moderngl.create_context(require=330)
        moderngl_window.activate_context(ctx=self.ctx)
        # the selected program will be used in the prepareData method
        self._program = None
        self._programs = {}
        # elapsed time
        self._elapsedTime = 0
        # TODO : remove this line when moderngl is 5.7.0
        self.ctx.info["GL_MAX_GEOMETRY_OUTPUT_VERTICES"] = 256
        # Display minimal information on GL Device
        print("\nYou are using the following GL device :")
        for field in ["GL_VENDOR",
                      "GL_RENDERER",
                      "GL_VERSION",
                      "GL_MAX_TEXTURE_SIZE",
                      "GL_MAX_GEOMETRY_OUTPUT_VERTICES",
                      ]:
            hardCoded = ""
            if field == "GL_MAX_GEOMETRY_OUTPUT_VERTICES":
                hardCoded = "(/!\ HARD-CODED /!\)"
            print(f"    - {field} : {self.ctx.info[field]} {hardCoded}")
        print()

    def _initFsGPU(self, fsGpuMemSize):

        # -----------------------------------------------------------------
        # SHADERS
        # -----------------------------------------------------------------
        # Instanciate shader object and add program
        shader = SimpleShader()
        self.addProgram(
                "Program #1",
                vertexStr=shader.getVertex(),
                geometryStr=shader.getGeometry(),
                fragmentStr=shader.getFragment()  )

        # -----------------------------------------------------------------
        # GPU FILE SYSTEM
        # -----------------------------------------------------------------
        # the height indicates number of pages
        # the width the size of each 1-height FSGpuBuffer
        # Using the start/end allocation mode, the static sprites could be
        # stored in the last pages, while the dynamic ones could be stored
        # in the first pages. So that would lead to save some page update
        # adn though less writing operations
        # -----------------------------------------------------------------
        # Data area = Width * Height (will be multiplied by number of components (four 32-bit float values))
        # That means sizeW and sizeH represent the number of pixel of the texture.
        # for one pixel, there are values, related to RGBA layers, and each value
        # is a 32-bit float
        sizeW = min(16 * 1024, self.ctx.info["GL_MAX_TEXTURE_SIZE"])
        sizeH = fsGpuMemSize // (sizeW * 4)
        # instanciate FsGpu
        print(f"\nCreating FsGPU texture : size={sizeW} x {sizeH} x 4 components (32-bit float values)")
        self._fsgpu = FsGpuMain(self.ctx, sizeW, sizeH)

        # -----------------------------------------------------------------
        # SPRITE BUFFER (VERTEX)
        # -----------------------------------------------------------------
        # Create sprite information (input data)
        nbComponents = 4
        spriteInfoSize = (1) * nbComponents  # 1 value in vertex input per sprite (the File System id)
        # Maximum set to 1 million gfx elements
        nbMaxSprites   = 1000000
        self._vertexBuffer = self.ctx.buffer(reserve=nbMaxSprites * spriteInfoSize)
        # Number of useful data in the vertex buffer
        self._nbSprites = 0

        # -----------------------------------------------------------------
        # VIEWPORT
        # -----------------------------------------------------------------
        # Change view port (for static sprites)
        w, h = self.ctx.screen.size
        self.setViewPort(0, 0, w, h)

        # -----------------------------------------------------------------
        # VERTEX ARRAY OBJECT
        # -----------------------------------------------------------------
        # Create vertex array object
        self._vao = self.ctx.vertex_array(
                        self._program,
                        [
                            (self._vertexBuffer,
                             "1u",
                             "blockID"),
                        ]
                    )

        # -----------------------------------------------------------------
        # UNIFORMS DATA
        # -----------------------------------------------------------------
        # Uniform data to know from which channel the data can be read
        # - texture atlas Information (where are located the textures)
        # - texture atlas
        # - gpu file system
        # - system time (start at 0)
        self._program["atlasTextureChan"] = OpenGLData.CHANNEL_ATLAS_TEXTURE
        self._program["atlasInfoChan"   ] = OpenGLData.CHANNEL_ATLAS_INFO
        self._program["fsGpuChan"       ] = OpenGLData.CHANNEL_FILE_SYSTEM
        self._program["systemTime"      ] = 0

        # -----------------------------------------------------------------
        # PROFILING
        # -----------------------------------------------------------------
        # Query configuration for profiling
        if OpenGLData.DEBUG_DISPLAY_QUERY:
            self._query = self.ctx.query(samples=True, time=True, primitives=True)

        # -----------------------------------------------------------------
        # GFX
        # -----------------------------------------------------------------
        Gfx.setLoader(self._loader)
        Gfx.setFsGPU(self._fsgpu)
        GfxSystem.setOpenGlData(self)

    def _loadAtlas(self):
        # -----------------------------------------------------------------
        # IMAGE ATLAS
        # -----------------------------------------------------------------
        # compute image atlas from the resource loader
        maxSide  = self.ctx.info["GL_MAX_TEXTURE_SIZE"]
        sizeSide = min(128, maxSide)
        self._loader.generateImageAtlas(sizeSide, maxSide, border=1)
        # Load fonts into the GPU File System
        self._loader.storeFonts(self._fsgpu)
        # Create atlas texture
        image = self._loader.getTextureImage()
        self._atlasImages = self.ctx.texture(image.size, 4, image.tobytes())

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
        width            = nbTextures * nbDataPerTexture
        nbTexels         = width * nbComponents
        overhead         = nbDataPerHeader * nbComponents # 3 values
        # Prepare texture
        self._atlasInfo = self.ctx.texture((width, 1), nbComponents, dtype="u4")
        self._atlasInfo.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # Write texture positions and sizes
        data = array("L", [0,] * (nbTexels+overhead) )
        allIDs = self._loader.getAllIds()
        for id in allIDs:
            data[4*id+0] = self._loader.getTextureById(id)["x"]
            data[4*id+1] = self._loader.getTextureById(id)["y"]
            data[4*id+2] = self._loader.getTextureById(id)["w"]
            data[4*id+3] = self._loader.getTextureById(id)["h"]
        self._atlasInfo.write(data.tobytes())


    # ========================================================================
    #  CONSTRUCTOR
    # ========================================================================
    def __init__(self, loader, fsGpuMemSize):
        # Create window and context
        self._initCfg()
        # Store resource loader reference
        self._loader = loader
        # Init GPU
        self._initFsGPU(fsGpuMemSize)

    def createAtlas(self):
        self._loadAtlas()

    def update(self, deltaTime):
        # update elapsed time and copy it into the uniform var
        self._elapsedTime += deltaTime
        self._program["systemTime"] = self._elapsedTime

        # Process File system
        self._fsgpu.update(deltaTime)

    def render(self):
        # update file system texture
        self._fsgpu.render()

        # Clear buffer with background color
        self.ctx.clear(
            (math.sin(self._elapsedTime + 0) + 1.0) / 4 + 0.5,
            (math.sin(self._elapsedTime + 2) + 1.0) / 4 + 0.5,
            (math.sin(self._elapsedTime + 3) + 1.0) / 4 + 0.5,
        )

        # Set blitting mode
        # self.ctx.blend_equation  = moderngl.FUNC_SUBTRACT
        # self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        self.ctx.enable(moderngl.BLEND)

        # Set the atlas texture to an opengl channel
        self._atlasInfo.use(OpenGLData.CHANNEL_ATLAS_INFO)
        self._atlasImages.use(OpenGLData.CHANNEL_ATLAS_TEXTURE)
        self._fsgpu.getTexture().use(OpenGLData.CHANNEL_FILE_SYSTEM)

        # Process rendering
        if not OpenGLData.DEBUG_DISPLAY_QUERY:
            self._vao.render(mode=moderngl.POINTS, vertices=self._nbSprites)
        else:
            with self._query:
                self._vao.render(mode=moderngl.POINTS, vertices=self._nbSprites)
                if self.ctx.error != "GL_NO_ERROR":
                    print("[ERROR] during rendering...")
                    print(self.ctx.error)
                    exit()


    # ========================================================================
    #  VIEWPORT CONFIGURATION
    # ========================================================================
    def setViewPort(self, x0, y0, x1, y1):
        near = 1
        far  = 0
        matrix = Matrix44.orthogonal_projection(x0, x1, y1, y0, near, far, dtype="f4")
        self._program["projection"].write(matrix)


    # ========================================================================
    #  VIEWPORT CONFIGURATION
    # ========================================================================
    def updateVertexBuffer(self, data, nbSprites):
        self._vertexBuffer.write(data)
        self._nbSprites = nbSprites


    # ========================================================================
    #  SHADER PROGRAMS
    # ========================================================================
    # The first program to be added, is automatically selected
    def addProgram(self, name, vertexStr="", geometryStr="", fragmentStr=""):
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
            self.selectProgram(name)

    # Select a program from the program list
    def selectProgram(self, name):
        if name in self._programs:
            self._program = self._programs[name]


    # ========================================================================
    #  DEBUG
    # ========================================================================
    def displayFS(self):
        if OpenGLData.DEBUG_DISPLAY_FSGPU:
            self._fsgpu.display()