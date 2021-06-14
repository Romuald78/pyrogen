

class Gfx():

    _loader = None

    @staticmethod
    def setLoader(loader):
        Gfx._loader = loader

    __slots__ = ['_x', '_y',
                 '_width', '_height',
                 '_scale', '_angle',
                 '_color',
                 '_fsgpu',
                 '_writeToFS'
                ]

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
        self._x        = x
        self._y        = y
        self._width    = width
        self._height   = height
        self._scale    = scale
        self._angle    = angle
        self._color    = filterColor
        self._fsgpu    = fsgpu
        self._writeToFS= True

    # ------------------------------------
    #  Position (in pixels)
    # ------------------------------------
    def getX(self):
        return self._x
    def getY(self):
        return self._y
    def setX(self, v):
        self._x = v
        self._writeToFS = True
    def setY(self, v):
        self._y = v
        self._writeToFS = True

    # ------------------------------------
    #  Dimensions (in pixels, cannotbe modified directly)
    # ------------------------------------
    def getW(self):
        return self._width*self._scale
    def getH(self):
        return self._height*self._scale

    # ------------------------------------
    # Scale (used to modify dimensions)
    # initial ratio is kept
    # ------------------------------------
    def getScale(self):
        return self._scale
    def setScale(self, v):
        self._scale = v
        self._writeToFS = True

    # ------------------------------------
    #  Filter Color (0-255 values)
    # ------------------------------------
    def getColor(self):
        return self._color
    def setColor(self, v):
        self._color = v
        self._writeToFS = True

    # ------------------------------------
    #  Angle (in degrees)
    # ------------------------------------
    def getAngle(self):
        return self._angle
    def setAngle(self, v):
        self._angle = v
        self._writeToFS = True

    # ------------------------------------
    #  FS GPU
    # ------------------------------------
    def getFsGpu(self):
        return self._fsgpu
    def getWriteToFS(self):
        return self._writeToFS
    def setWriteToFS(self, value):
        self._writeToFS = value



    def __str__(self):
        return f"x={self._x} y={self._y} w={self._width*self._scale} h={self._height*self._scale} scale={self._scale} angle={self._angle} filterColor={self._color}"



class GfxSprite(Gfx):

    __slots__ = ['_textureID',
                 '_blockID'
                ]

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
        self._blockID = self._fsgpu.alloc(12, 1)     # TODO : 1 = TYPE SPRITE
        # Update the first time it is created
        self.update(1/60)

    def getTextureID(self):
        return self._textureID

    def getBlockID(self):
        return self._blockID

    def update(self, deltaTime):
        # update data into FS if needed
        if self.getWriteToFS():
            # print(f"Writing {self} into FS")
            alpha = 255
            if len(self._color) >= 4:
                alpha = self._color[3]
            data = [self._color[0], self._color[1] , self._color[2], alpha,
                    self._x       , self._y        , self._width   , self._height  ,
                    self._angle   , self._textureID, 0             , 0
                   ]
            self._fsgpu.writeBlock(self.getBlockID(), data)
            self.setWriteToFS(False)

    def __str__(self):
        return f"<GfxSprite textureId={self.getTextureID()} blockID={self.getBlockID()} {super().__str__()}/>"




