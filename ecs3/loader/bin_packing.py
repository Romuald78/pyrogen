
class UniqueID():

    _uniqueID = 0
    @staticmethod
    def getID():
        res = UniqueID._uniqueID
        UniqueID._uniqueID += 1
        return res


class Box():

    def __init__(self, imgRsc, newId, index=0):
        # Prepare sub coords
        w = imgRsc.spriteW
        h = imgRsc.spriteH
        ix = index % imgRsc.nbSpriteX
        iy = index // imgRsc.nbSpriteX
        x0 = imgRsc.x0 + ix * w
        y0 = imgRsc.y0 + iy * h
        x1 = x0 + w
        y1 = y0 + h
        # Store box and image
        self._id = newId
        self._x = x0
        self._y = y0
        self._name = f"{imgRsc.name}"
        if imgRsc.nbSpriteX > 1 or imgRsc.nbSpriteY > 1:
            self._name += f"_{index}"
        self._img = imgRsc.data.crop((x0, y0, x1, y1))

    @property
    def x0(self):
        return self._x

    @property
    def y0(self):
        return self._y

    @x0.setter
    def x0(self, v):
        self._x = v

    @y0.setter
    def y0(self, v):
        self._y = v

    @property
    def width(self):
        return self._img.size[0]

    @property
    def height(self):
        return self._img.size[1]

    @property
    def x1(self):
        return self.x0 + self.width - 1

    @property
    def y1(self):
        return self.y0 + self.height - 1

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._img

    def isOverlapping(self, other):
        return self.x0 <= other.x1 and self.x1 >= other.x0 and self.y0 <= other.y1 and self.y1 >= other.y0

    def __str__(self):
        return f"<Box id:{self.id} name:'{self.name}' - x:{self.x0} - y:{self.y0} - w:{self.width} - h:{self.height}>"


class Surface():

    def __init__(self, x0, y0, w, h):
        self._x0 = x0
        self._y0 = y0
        self._w  = w
        self._h  = h
        self._children = []

    @property
    def width(self):
        return self._w
    @property
    def height(self):
        return self._h
    @property
    def x0(self):
        return self._x0
    @property
    def y0(self):
        return self._y0
    @property
    def x1(self):
        return self.x0 + self.width - 1
    @property
    def y1(self):
        return self.y0 + self.height - 1
    @property
    def hasChildren(self):
        return len(self._children) > 0

    def __str__(self):
        return f"<SURFACE : {self.x0}/{self.y0}/{self.width}/{self.height}>"

    def increaseSize(self, oldMaxSize, newMaxSize):
        # Get X1 and Y1 limits
        oldX = oldMaxSize[0] - 1
        oldY = oldMaxSize[1] - 1
        newX = newMaxSize[0] - 1
        newY = newMaxSize[1] - 1
        # check if we have to stretch this surface
        if self.x1 == oldX:
            self._w += newX - oldX
        if self.y1 == oldY:
            self._h += newX - oldX
        # Do the same for child areas
        if self.hasChildren:
            self._children[0].increaseSize(oldMaxSize, newMaxSize)
            self._children[1].increaseSize(oldMaxSize, newMaxSize)

    def insertBox(self, box, border=1):
        # Get full box area
        boxW = box.width + 2 * border
        boxH = box.height + 2 * border
        # check if box fits into surface
        if self.width >= boxW and self.height >= boxH and not self.hasChildren:
            # Split surface and add children
            sB = Surface(self.x0, self.y0 + boxH, boxW, self.height - boxH)
            sR = Surface(self.x0 + boxW, self.y0, self.width - boxW, self.height)
            self._children.append(sR)
            self._children.append(sB)
            # Set position for the current box
            box.x0 = self.x0 + border
            box.y0 = self.y0 + border
            # Return OK
            return True
        elif self.hasChildren :
            # Check first child
            res1 = False
            res2 = False
            res1 = self._children[1].insertBox(box, border)
            if not res1:
                res2 = self._children[0].insertBox(box, border)
            return res1 or res2
        else:
            # no available surface
            return False



class BinPacking():

    # -----------------------------------------------------------------
    # Create box information from image list
    # -----------------------------------------------------------------
    def _createBoxes(self, imgList):
        #self._processInternal( (0,0,self._size-1, self._size-1) )
        boxes = []
        while len(imgList) > 0:
            # Get next image from list
            img     = imgList[0]
            imgList = imgList[1:]
            if img.nbSpriteX==1 and img.nbSpriteY==1:
                box = Box(img, 0)
                boxes.append(box)
            else:
                # Create new images and add them into the atlas
                for y in range(img.nbSpriteY):
                    for x in range(img.nbSpriteX):
                        idx = y*img.nbSpriteX + x
                        box = Box(img, UniqueID.getID(), idx)
                        boxes.append(box)
        return boxes

    # -----------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------
    def __init__(self, squareSize, maxSize, imgBorder, resImgList):
        self._size   = squareSize
        self._border = imgBorder
        self._boxes  = self._createBoxes(resImgList)
        self._out = []
        self._surface = Surface(0, 0, self._size, self._size)
        self._maxSize = maxSize

    def _processInternal3(self):
        while len(self._boxes) > 0:
            # take first box
            box = self._boxes[0]
            # Split surfaces with current box
            isOK = self._surface.insertBox(box, self._border)
            if isOK:
                # Add new box in output
                self._out.append(box)
                # Remove box from TODO list
                self._boxes = self._boxes[1:]
            else:
#                print( f"Impossible to add box {box}")
#                print( "Increase squareSize")
#                print(f"old surface {self._surface.width}-{self._surface.height}")
                addS = max(box.width, box.height)
                oldS = (self._surface.width, self._surface.height)
                newS = (int(self._surface.width  + addS + 2*self._border),
                        int(self._surface.height + addS + 2*self._border))
                self._surface.increaseSize(oldS, newS)
#                print(f"new surface {self._surface.width}-{self._surface.height}")
                if self._surface.width > self._maxSize:
                    return False
        return True


    def process(self):
        self._out = []
        res = self._processInternal3()
        return res, self._out, max(self._surface.width, self._surface.height)


