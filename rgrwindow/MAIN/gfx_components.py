import array


class Gfx():

    HEADER_SIZE    = 16
    TYPE_SPRITE    = 1
    TYPE_TEXT      = 2
    TYPE_RECTANGLE = 3
    TYPE_OVAL      = 4

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
                 visOn  = 1.0,
                 visTot = 1.0,
                 autoRotate=0.0,
                 fsgpu=None,
                 dataSize=HEADER_SIZE,
                 gfxType=TYPE_SPRITE,
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
        # id = 10-11 for visibility ON-TOTAL
        self.setVisibility(visOn, visTot)
        # id = 12 for angle auto-rotation
        self.setAutoRotate(autoRotate)
        # id = 13 for GFX type
        self._data[13] = gfxType

        # remaining ids = 14-15
        # TODO : highlight border (thickness, color, ...) ?


    # ------------------------------------
    #  FS GPU
    # ------------------------------------
    def getBlockID(self):
        return self._blockID
    def getFsGpu(self):
        return self._fsgpu
    def getType(self):
        return self._data[13]


    # ------------------------------------
    #  Position (in pixels)
    # ------------------------------------
    def getX(self):
        return self._data[4]
    def getY(self):
        return self._data[4]
    def getPosition(self):
        return (self._data[4], self._data[5])
    def getTransform(self):
        return (self._data[4], self._data[5], self._data[9])
    def setX(self, v):
        self._data[4] = v
        self._writeToFS = True
    def setY(self, v):
        self._data[5] = v
        self._writeToFS = True
    def setPosition(self, x, y):
        self._data[4] = x
        self._data[5] = y
        self._writeToFS = True
    def setTransform(self, x, y, ang):
        self._data[4] = x
        self._data[5] = y
        self._data[9] = ang
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
    def getAutoRotate(self):
        return self._data[12]
    def setAngle(self, v):
        self._data[9] = v
        self._writeToFS = True
    def setAutoRotate(self, v):
        self._data[12] = v
        self._writeToFS = True


    # ------------------------------------
    #  Visibility (ON period and TOTAL period)
    # ------------------------------------
    def getVisibility(self):
        return (self._data[10], self._data[11])
    def setVisibility(self, on, total):
        self._data[10] = on
        self._data[11] = total
        self._writeToFS = True
    def show(self):
        self._data[10] = self._data[11]
        self._writeToFS = True
    def hide(self):
        self._data[10] = 0
        self._writeToFS = True


    # ------------------------------------
    #  UPDATE (copy buffer into the GPU texture
    # ------------------------------------
    def update(self, deltaTime):
        pass
        # update data into FS if needed
        if self._writeToFS:
            #print(f"Writing {self._data} into FS")
            self._fsgpu.write2Texture(self._blockID, self._data)
            self._writeToFS = False



class GfxSprite(Gfx):

    __slots__ = ['_blockID',
                 '_fsgpu',
                ]

    def __init__(self, textureName, width=-1, height=-1, x=0.0, y=0.0, angle=0.0, scale=1.0, visOn=1.0, visTot=1.0, autoRotate=0.0, filterColor=(255,255,255), fsgpu=None):
        NB_VALUES = Gfx.HEADER_SIZE + 4
        # Get texture info from loader
        texture   = Gfx._loader.getTextureByName(textureName)
        textureID = texture["id"]
        w         = texture["w"]
        h         = texture["h"]
        # if width or height is not filled, use the texture dimensions
        if width > 0:
            w = width
        if height > 0:
            h = height
        # Allocate buffer in the file system for it
        self._blockID = fsgpu.alloc(NB_VALUES, Gfx.TYPE_SPRITE)
        # Call parent constructor
        super().__init__(x, y,
                         w, h,
                         angle, scale,
                         filterColor,
                         visOn, visTot,
                         autoRotate,
                         fsgpu,NB_VALUES,
                         Gfx.TYPE_SPRITE,
                         self._blockID)
        # Store specific information for this Sprite (id 10 for textureID)
        self.setTextureID(textureID)
        # Update the first time it is created
        self.update(1/60)

    def getTextureID(self):
        return self._data[16]
    def setTextureID(self, v):
        self._data[16]  = v
        self._writeToFS = True





class GfxBox(Gfx):

    __slots__ = ['_blockID',
                 '_fsgpu',
                 ]

    def __init__(self, inClr=(0,0,0,0), width=-1, height=-1, x=0.0, y=0.0, angle=0.0, scale=1.0, visOn=1.0, visTot=1.0,
                 autoRotate=0.0, filterColor=(255, 255, 255), fsgpu=None):
        # We need to add
        NB_VALUES = Gfx.HEADER_SIZE + 4
        # if width or height is not filled, use default dimensions
        w = 16
        h = 16
        if width > 0:
            w = width
        if height > 0:
            h = height
        # Allocate buffer in the file system for it
        self._blockID = fsgpu.alloc(NB_VALUES, Gfx.TYPE_RECTANGLE)
        # Call parent constructor
        super().__init__(x, y,
                         w, h,
                         angle, scale,
                         filterColor,
                         visOn, visTot,
                         autoRotate,
                         fsgpu, NB_VALUES,
                         Gfx.TYPE_RECTANGLE,
                         self._blockID)
        # Store specific information for this Sprite (colors)
        self.setInColor(inClr)
        # Update the first time it is created
        self.update(1 / 60)

    def getInColor(self):
        return (self._data[16],self._data[17],self._data[18],self._data[19])
    def setInColor(self, v):
        alpha = 255
        if len(v) >= 4:
            alpha = v[3]
        self._data[16]   = v[0]
        self._data[17]   = v[1]
        self._data[18]   = v[2]
        self._data[19]   = alpha
        self._writeToFS = True






#class GfxText(Gfx):
#
#    __slots__ = ['_blockID',
#                 '_fsgpu',
#                 '_message',
#                ]
#
#    def __init__(self, message, width=-1, height=-1, x=0.0, y=0.0, angle=0.0, scale=1.0, visOn=1.0, visTot=1.0,
#        autoRotate=0.0, filterColor=(255, 255, 255), fsgpu=None):
#        # We need to add specific data
#        NB_VALUES = Gfx.HEADER_SIZE + 4
#        # if width or height is not filled, use default dimensions
#        w = 16
#        h = 16
#        if width > 0:
#            w = width
#        if height > 0:
#            h = height
#        # Allocate buffer in the file system for it
#        self._blockID = fsgpu.alloc(NB_VALUES, Gfx.TYPE_TEXT)
#        # Call parent constructor
#        super().__init__(x, y,
#                         w, h,
#                         angle, scale,
#                         filterColor,
#                         visOn, visTot,
#                         autoRotate,
#                         fsgpu, NB_VALUES,
#                         Gfx.TYPE_RECTANGLE,
#                         self._blockID)
#        # Store specific information for this Sprite (colors)
#        self.setMessage(message)
#        # Update the first time it is created
#        self.update(1 / 60)
#
#    def setMessage(self, msg):
#        self._message = msg


#   def __init__(self, message, fontName, size=12, x=0.0, y=0.0, angle=0.0, scale=1.0, visOn=1.0, visTot=1.0, autoRotate=0.0, filterColor=(255,255,255), fsgpu=None):
#        # Specific Data for text element
#        # - font id (1)
#        # - font size (1)
#        # - message length (1)
#        # - message data (ascii) (L)
#        # TODO : if message data is too small to contain the new message, re-allocate a new block
#        # TODO : and free this one : do not forget to update the blockID property (add a setter for it ?)
#
#        # Get message length
#        L = len(message)
#        NB_VALUES = Gfx.HEADER_SIZE + 3 + L


#        # Get texture info from loader
#
#        # Allocate buffer in the file system for it
#        self._blockID = fsgpu.alloc(NB_VALUES, 1)     # TODO : 1 = TYPE SPRITE
#        # Call parent constructor
#        super().__init__(x, y, w, h, angle, scale, filterColor, visOn, visTot, autoRotate, fsgpu, NB_VALUES, self._blockID)
#        # Store specific information for this Sprite (id 10 for textureID)
#        self.setTextureID(textureID)
#        # Update the first time it is created
#        self.update(1/60)

#    def getTextureID(self):
#        return self._data[16]
#    def setTextureID(self, v):
#        self._data[16]  = v
#        self._writeToFS = True
#        self._fsgpu.writeBlock1(self._blockID, v, 10)
#    def __str__(self):
#        return f"<GfxSprite textureId={self.getTextureID()} blockID={self.getBlockID()} {super().__str__()}/>"




