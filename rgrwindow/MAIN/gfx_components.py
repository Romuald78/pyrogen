from array import array


class Gfx():

    # ------------------------------------
    # STATIC references (textures and filesystem)
    # ------------------------------------
    _loader = None
    _fsgpu  = None

    @staticmethod
    def setLoader(loader):
        Gfx._loader = loader

    @staticmethod
    def setFileSystem(fsgpu):
        Gfx._fsgpu = fsgpu

    # ------------------------------------
    # Data Offsets (MUST be coherent with buffer filling)
    # ------------------------------------
    OFFSET_X      = 0
    OFFSET_Y      = 1
    OFFSET_Z      = 2
    OFFSET_RFU1   = 2

    OFFSET_WIDTH  = 4
    OFFSET_HEIGHT = 5
    OFFSET_SCALE  = 6
    OFFSET_ANGLE  = 7

    OFFSET_RED    = 8
    OFFSET_GREEN  = 9
    OFFSET_BLUE   = 10
    OFFSET_ALPHA  = 11

    # ------------------------------------
    #  Constructor
    # ------------------------------------
    def __init__(self,
                 x=0.0,
                 y=0.0,
                 width=-1,
                 height=-1,
                 angle=0.0,
                 scale=1.0,
                 filterColor=(255,255,255,255),
                 depth = 0,):

        # Create array
        self._buffer = array('f',[])
        # fill array with Gfx Common Data (MUST be coherent with offsets)
        self._buffer.append(x     )         # index 0
        self._buffer.append(y     )         #       1
        self._buffer.append(depth )         #       2
        self._buffer.append(0     )         #       3

        self._buffer.append(width )         #       4
        self._buffer.append(height)         #       5
        self._buffer.append(scale )         #       6
        self._buffer.append(angle )         #       7

        self._buffer.append(filterColor[0]) #       8
        self._buffer.append(filterColor[1]) #       9
        self._buffer.append(filterColor[2]) #       10
        self._buffer.append(filterColor[3]) #       11

        # Header size
        self._headerSize = len(self._buffer)

        # Set this buffer has been modified and must be copied into the FileSystem again
        self._modified = True

        # Store depth value
        self._depth = depth

        # File system : Allocation table ID
        self._fsID = None

    # ------------------------------------
    #  File System allocation
    # ------------------------------------
    def allocate(self, gfxType):
        # allocate a block size according to current buffer size
        self._fsID = Gfx._fsgpu.reserve(self.dataSize, gfxType)

    # ------------------------------------
    #  Update method
    # ------------------------------------
    def update(self):
        # if needed, the buffer will be copied to the Gpu
        if self.modified:
            Gfx._fsgpu.writeBlock(self._fsID, self._buffer)
            # This Gfx element is up to date now
            self._modified = False

    # ------------------------------------
    #  Data Buffer
    # ------------------------------------
    @property
    def dataSize(self):
        return len(self._buffer)
    @property
    def headerSize(self):
        return self._headerSize
    @property
    def modified(self):
        return self._modified
#
    def readData(self, index):
        return self._buffer[index]
    def writeData(self, index, value):
        self._buffer[index] = value
        self._modified = True
    def appendData(self, floatValue):
        self._buffer.append(floatValue)
        self._modified = True

    # ------------------------------------
    #  Position (in pixels)
    # ------------------------------------
    @property
    def x(self):
        return self.readData(Gfx.OFFSET_X)
    @property
    def y(self):
        return self.readData(Gfx.OFFSET_Y)
    @property
    def z(self):
        return self.readData(Gfx.OFFSET_Z)
    @x.setter
    def x(self, v):
        self.writeData(Gfx.OFFSET_X, v)
        self._modified = True
    @y.setter
    def y(self, v):
        self.writeData(Gfx.OFFSET_Y, v)
        self._modified = True
    @z.setter
    def z(self, v):
        self.writeData(Gfx.OFFSET_Z, v)
        self._modified = True

    # ------------------------------------
    #  Dimensions (in pixels, cannotbe modified directly)
    # ------------------------------------
    @property
    def width(self):
        return self.readData(Gfx.OFFSET_WIDTH) * self.readData(Gfx.OFFSET_SCALE)
    @property
    def height(self):
        return self.readData(Gfx.OFFSET_HEIGHT) * self.readData(Gfx.OFFSET_SCALE)

    # ------------------------------------
    # Scale (used to modify dimensions)
    # initial ratio is kept
    # ------------------------------------
    @property
    def scale(self):
        return self.readData(Gfx.OFFSET_SCALE)
    @scale.setter
    def scale(self, v):
        self.writeData(Gfx.OFFSET_SCALE, v)
        self._modified = True

    # ------------------------------------
    #  Filter Color (0-255 values)
    # ------------------------------------
    @property
    def color(self):
        return (self.readData(Gfx.OFFSET_RED  ),
                self.readData(Gfx.OFFSET_GREEN),
                self.readData(Gfx.OFFSET_BLUE ),
                self.readData(Gfx.OFFSET_ALPHA)
                )
    @color.setter
    def color(self, v):
        self.writeData(Gfx.OFFSET_RED  , v[0])
        self.writeData(Gfx.OFFSET_GREEN, v[1])
        self.writeData(Gfx.OFFSET_BLUE , v[2])
        self.writeData(Gfx.OFFSET_ALPHA, 1.0 )
        if len(v) > 3:
            self.writeData(Gfx.OFFSET_ALPHA, v[3])
        self._modified = True

    # ------------------------------------
    #  Angle (in degrees)
    # ------------------------------------
    @property
    def angle(self):
        return self._buffer[Gfx.OFFSET_ANGLE]
    @angle.setter
    def angle(self, v):
        self._buffer[Gfx.OFFSET_ANGLE] = v
        self._updated = True

    # ------------------------------------
    #  Debug Display
    # ------------------------------------
    def __str__(self):
        return f"x={self.x} y={self.y} w={self.width} h={self.height} scale={self.scale} angle={self.angle} filterColor={self.color}/>"



class GfxSprite(Gfx):

    def __init__(self, textureName, width=-1, height=-1, x=0.0, y=0.0, angle=0.0, scale=1.0, filterColor=(255,255,255,255)):
        # Get texture info from loader
        tex = Gfx._loader.getTextureByName(textureName)
        id  = tex["id"]
        w   = tex["w" ]
        h   = tex["h" ]
        # if width or height is not filled, use the texture ones
        if width > 0:
            w = width
        if height > 0:
            h = height
        # instanciate Gfx parent class
        super().__init__(x, y, w, h, angle, scale, filterColor)
        # Store specific information for this Sprite
        self.appendData(id)     # ID
        self.appendData(0 )     # RFU1
        self.appendData(0 )     # RFU2
        self.appendData(0 )     # RFU3
        # Now parent class will allocate space in the File System
        self.allocate(1)

    @property
    def textureID(self):
        return self.readData(self.headerSize + 0)

    def __str__(self):
        return f"<GfxSprite textureId={self.textureID} {super().__str__()}/>"




