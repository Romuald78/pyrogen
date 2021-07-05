import array


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
class Gfx():
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # ------------------------------------
    #  CONSTANTS
    # ------------------------------------
    HEADER_SIZE    = 16
    TYPE_SPRITE    = 1
    TYPE_TEXT      = 2
    TYPE_RECTANGLE = 3
    TYPE_OVAL      = 4
    TYPE_FONT      = 5

    # ------------------------------------
    #  LOADER
    # ------------------------------------
    _loader = None

    @staticmethod
    def setLoader(loader):
        Gfx._loader = loader

    # ------------------------------------
    #  SLOTS
    # ------------------------------------
    __slots__ = ['_fsgpu',
                 '_blockID',
                 '_writeToFS',
                 '_data',
                ]

    # ------------------------------------
    #  CONSTRUCTOR
    # ------------------------------------
    def __init__(self,
                 width,
                 height,
                 scale=1.0,
                 x=0.0,
                 y=0.0,
                 angle=0.0,
                 filterColor=(255,255,255),
                 visOn  = 1.0,
                 visTot = 1.0,
                 autoRotate=0.0,
                 anchorX=0.0,
                 anchorY=0.0,
                 fsgpu=None,
                 dataSize=HEADER_SIZE,
                 gfxType=TYPE_SPRITE,
                 blockID=0
                 ):
        self._fsgpu     = fsgpu
        self._blockID   = blockID
        self._writeToFS = True

        # > Buffer is array.array
        self._data = array.array("f", [0.0, ] * int(dataSize))

        # id = 0-1-2-3 for R-G-B-A
        self.setColor(filterColor)
        # id = 4-5-6-7 for X-Y-W-H
        self.setX(x)
        self.setY(y)
        self.setW(width)
        self.setH(height)
        # id = 8-9-10-11 for SCALE-ANGLE-VISIBILITY ON/TOTAL
        self.setScale(scale)
        self.setAngle(angle)
        self.setVisibility(visOn, visTot)
        # id = 12 for angle auto-rotation
        self.setAutoRotate(autoRotate)
        # id = 13 for GFX type
        self._data[13] = gfxType
        # id = 14-15 for ANCHOR Horizontal-Vertical
        # The anchor is the sprite position origin (x/y), and from the rotation is performed
        # Both (anchorX and anchorY) are values in pixels
        # These values can exceed the sprite size : that means the anchor
        # point will be outside the texture rectangle area
        self.setAnchor(anchorX, anchorY)

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
    #  POSITION (in pixels)
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
    #  DIMENSIONS (in pixels, cannotbe modified directly)
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
    #  FILTER COLOR (0-255 values)
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
    #  SCALE
    # ------------------------------------
    def getScale(self):
        return self._data[8]
    def setScale(self, v):
        self._data[8] = v
        self._writeToFS = True

    # ------------------------------------
    #  ANGLE (in degrees)
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
    #  VISIBILITY (ON period and TOTAL period)
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
    #  ANCHOR
    # ------------------------------------
    def getAnchor(self):
        return (self._data[14], self._data[15])
    def getanchorX(self):
        return self._data[14]
    def getanchorY(self):
        return self._data[15]
    def setAnchor(self, x, y):
        self._data[14] = x
        self._data[15] = y
        self._writeToFS = True
    def setAnchorX(self, v):
        self._data[14] = v
        self._writeToFS = True
    def setAnchorY(self, v):
        self._data[15] = v
    def setAnchorLeft(self):
        self._data[14] = -1
        self._writeToFS = True
    def setAnchorCenterX(self):
        self._data[14] = 0
        self._writeToFS = True
    def setAnchorRight(self):
        self._data[14] = 1
        self._writeToFS = True
    def setAnchorTop(self):
        self._data[15] = -1
        self._writeToFS = True
    def setAnchorCenterY(self):
        self._data[15] = 0
        self._writeToFS = True
    def setAnchorBottom(self):
        self._data[15] = 1
        self._writeToFS = True
    def setAnchorCenter(self):
        self._data[14] = 0
        self._data[15] = 0
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



# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
class GfxSprite(Gfx):
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # ------------------------------------
    #  SLOTS
    # ------------------------------------
    __slots__ = ['_blockID',
                 '_fsgpu',
                 ]

    # ------------------------------------
    #  CONSTRUCTOR
    # ------------------------------------
    def __init__(self,
                 textureName,
                 width=-1, height=-1,
                 x=0.0,
                 y=0.0,
                 angle=0.0,
                 visOn=1.0,
                 visTot=1.0,
                 autoRotate=0.0,
                 filterColor=(255,255,255),
                 anchorX=0.0,
                 anchorY=0.0,
                 fsgpu=None):
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
        super().__init__(w, h,
                         x=x,
                         y=y,
                         angle=angle,
                         filterColor=filterColor,
                         visOn=visOn,
                         visTot=visTot,
                         autoRotate=autoRotate,
                         anchorX=anchorX,
                         anchorY=anchorY,
                         fsgpu=fsgpu,
                         dataSize=NB_VALUES,
                         gfxType=Gfx.TYPE_SPRITE,
                         blockID=self._blockID)

        # Store specific information for this Sprite
        self.setTextureID(textureID)
        # Update the first time it is created
        self.update(1/60)

    # ------------------------------------
    #  TEXTURE ID
    # ------------------------------------
    def getTextureID(self):
        return self._data[Gfx.HEADER_SIZE + 0]
    def setTextureID(self, v):
        self._data[Gfx.HEADER_SIZE + 0]  = v
        self._writeToFS = True



# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
class GfxBox(Gfx):
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # ------------------------------------
    #  SLOTS
    # ------------------------------------
    __slots__ = ['_blockID',
                 '_fsgpu',
                 ]

    # ------------------------------------
    #  CONSTRUCTOR
    # ------------------------------------
    def __init__(self,
                 inClr=(0,0,0,0),
                 width=-1,
                 height=-1,
                 x=0.0,
                 y=0.0,
                 angle=0.0,
                 visOn=1.0,
                 visTot=1.0,
                 autoRotate=0.0,
                 filterColor=(255, 255, 255),
                 anchorX=0.0,
                 anchorY=0.0,
                 fsgpu=None):
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
        super().__init__(w, h,
                         x=x,
                         y=y,
                         angle=angle,
                         filterColor=filterColor,
                         visOn=visOn,
                         visTot=visTot,
                         autoRotate=autoRotate,
                         anchorX=anchorX,
                         anchorY=anchorY,
                         fsgpu=fsgpu,
                         dataSize=NB_VALUES,
                         gfxType=Gfx.TYPE_RECTANGLE,
                         blockID=self._blockID)
        # Store specific information for this Sprite (colors)
        self.setInColor(inClr)
        # Update the first time it is created
        self.update(1 / 60)

    # ------------------------------------
    #  INNER COLOR
    # ------------------------------------
    def getInColor(self):
        return (self._data[Gfx.HEADER_SIZE + 0],
                self._data[Gfx.HEADER_SIZE + 1],
                self._data[Gfx.HEADER_SIZE + 2],
                self._data[Gfx.HEADER_SIZE + 3])
    def setInColor(self, v):
        alpha = 255
        if len(v) >= 4:
            alpha = v[3]
        self._data[Gfx.HEADER_SIZE + 0]   = v[0]
        self._data[Gfx.HEADER_SIZE + 1]   = v[1]
        self._data[Gfx.HEADER_SIZE + 2]   = v[2]
        self._data[Gfx.HEADER_SIZE + 3]   = alpha
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




