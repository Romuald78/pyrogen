

class Gfx():

    _loader = None

    @staticmethod
    def setLoader(loader):
        Gfx._loader = loader

    def __init__(self,
                 x=0.0,
                 y=0.0,
                 width=-1,
                 height=-1,
                 angle=0.0,
                 scale=1.0,
                 filterColor=(255,255,255),
                 fsgpu=None,
                 ):
        self._x      = x
        self._y      = y
        self._width  = width
        self._height = height
        self._scale  = scale
        self._angle  = angle
        self._color  = filterColor
        self._fsgpu  = fsgpu

    # ------------------------------------
    #  Position (in pixels)
    # ------------------------------------
    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
    @x.setter
    def x(self, v):
        self._x = v
    @y.setter
    def y(self, v):
        self._y = v

    # ------------------------------------
    #  Dimensions (in pixels, cannotbe modified directly)
    # ------------------------------------
    @property
    def width(self):
        return self._width*self._scale
    @property
    def height(self):
        return self._height*self._scale

    # ------------------------------------
    # Scale (used to modify dimensions)
    # initial ratio is kept
    # ------------------------------------
    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self, v):
        self._scale = v

    # ------------------------------------
    #  Filter Color (0-255 values)
    # ------------------------------------
    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, v):
        self._color = v

    # ------------------------------------
    #  Angle (in degrees)
    # ------------------------------------
    @property
    def angle(self):
        return self._angle
    @angle.setter
    def angle(self, v):
        self._angle = v

    # ------------------------------------
    #  FS GPU
    # ------------------------------------
    @property
    def fsgpu(self):
        return self._fsgpu


    def __str__(self):
        return f"x={self.x} y={self.y} w={self.width} h={self.height} scale={self.scale} angle={self.angle} filterColor={self.color}/>"



class GfxSprite(Gfx):

    def _updateFS(self):
        alpha = 255
        if len(self.color) >= 4:
            alpha = self.color[3]
        data = [self.color[0], self.color[1] , self.color[2], alpha,
                self.x       , self.y        , self.width   , self.height  ,
                self.angle   , self.textureID, 0            , 0
               ]
        self.fsgpu.writeBlock(self.blockID, data)

    def __init__(self, textureName, width=-1, height=-1, x=0.0, y=0.0, angle=0.0, scale=1.0, filterColor=(255,255,255), fsgpu=None):
        # Get texture info from loader
        texture   = Gfx._loader.getTextureByName(textureName)
        textureID = texture["id"]
        w   = texture["w"]
        h   = texture["h"]
        # if width or height is not filled, use the texture ones
        if width > 0:
            w = width
        if height > 0:
            h = height
        super().__init__(x, y, w, h, angle, scale, filterColor, fsgpu)
        # Store specific information for this Sprite
        self._textureID = textureID
        # Allocate buffer in the file system for it
        self._blockID = self.fsgpu.alloc(12, 1)     # TODO : 1 = TYPE SPRITE
        # And first update into file system
        self._updateFS()


    @property
    def textureID(self):
        return self._textureID
    @property
    def blockID(self):
        return self._blockID


    def __str__(self):
        return f"<GfxSprite textureId={self.textureID} {super().__str__()}/>"




