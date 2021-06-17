import array


class Gfx():

    _loader = None

    @staticmethod
    def setLoader(loader):
        Gfx._loader = loader

    __slots__ = ['_fsgpu',
                 '_blockID',
                 '_writeToFS',
                 '_data',
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
                 dataSize=12,
                 blockID=0
                 ):
        self._fsgpu    = fsgpu
        self._blockID  = blockID
        self._writeToFS= True

        # > Buffer is array.array
        self._data = array.array("f", [0.0, ] * int(dataSize))

        # id = 0-1-2-3 for R-G-B-A
        self.setColor(filterColor)
        # id = 4-5-6-7 for X-Y-W-H
        self.setX(x)
        self.setY(y)
        self.setW(width)
        self.setH(height)
        # id = 8-9 for SCALE-ANGLE
        self.setScale(scale)
        self.setAngle(angle)
        # id 10-11 for future use !!
        # --------------------------

    # ------------------------------------
    #  FS GPU
    # ------------------------------------
    def getBlockID(self):
        return self._blockID
    def getFsGpu(self):
        return self._fsgpu

    # ------------------------------------
    #  Position (in pixels)
    # ------------------------------------
    def getX(self):
        return self._data[4]
    def getY(self):
        return self._data[4]
    def setX(self, v):
        self._data[4] = v
        self._writeToFS = True
    def setY(self, v):
        self._data[5] = v
        self._writeToFS = True

    # ------------------------------------
    #  Dimensions (in pixels, cannotbe modified directly)
    # ------------------------------------
    def getW(self):
        return self._data[6]
    def getH(self):
        return self._data[7]
    def setW(self, v):
        self._data[6] = v
        self._writeToFS = True
    def setH(self, v):
        self._data[7] = v
        self._writeToFS = True

    # ------------------------------------
    # Scale (used to modify dimensions)
    # initial ratio is kept
    # ------------------------------------
    def getScale(self):
        return self._data[8]
    def setScale(self, v):
        self._data[8] = v
        self._writeToFS = True

    # ------------------------------------
    #  Filter Color (0-255 values)
    # ------------------------------------
    def getColor(self):
        return (self._data[0], self._data[1], self._data[2], self._data[3])
    def setColor(self, v):
        alpha = 255
        if len(v) >= 4:
            alpha = v[3]
        self._data[0]   = v[0]
        self._data[1]   = v[1]
        self._data[2]   = v[2]
        self._data[3]   = alpha
        self._writeToFS = True


    # ------------------------------------
    #  Angle (in degrees)
    # ------------------------------------
    def getAngle(self):
        return self._data[9]
    def setAngle(self, v):
        self._data[9] = v
        self._writeToFS = True



    def update(self, deltaTime):
        pass
        # update data into FS if needed
        if self._writeToFS:
            # print(f"Writing {self} into FS")
            self._fsgpu.write2Texture(self._blockID, self._data)
            self._writeToFS = False



class GfxSprite(Gfx):

    __slots__ = ['_blockID',
                 '_fsgpu',
                ]

    def __init__(self, textureName, width=-1, height=-1, x=0.0, y=0.0, angle=0.0, scale=1.0, filterColor=(255,255,255), fsgpu=None):
        NB_VALUES = 12
        # Get texture info from loader
        texture   = Gfx._loader.getTextureByName(textureName)
        textureID = texture["id"]
        w         = texture["w"]
        h         = texture["h"]
        # if width or height is not filled, use the texture ones
        if width > 0:
            w = width
        if height > 0:
            h = height
        # Allocate buffer in the file system for it
        self._blockID = fsgpu.alloc(NB_VALUES, 1)     # TODO : 1 = TYPE SPRITE
        # Call parent constructor
        super().__init__(x, y, w, h, angle, scale, filterColor, fsgpu, NB_VALUES, self._blockID)
        # Store specific information for this Sprite (id 10 for textureID)
        self.setTextureID(textureID)
        # Update the first time it is created
        self.update(1/60)

    def getTextureID(self):
        return self._data[10]
    def setTextureID(self, v):
        self._data[10]  = v
        self._writeToFS = True
#        self._fsgpu.writeBlock1(self._blockID, v, 10)


    def __str__(self):
        return f"<GfxSprite textureId={self.getTextureID()} blockID={self.getBlockID()} {super().__str__()}/>"




