import array
import sys
from pathlib import Path

from PIL import Image, ImageFont, ImageDraw
from os.path import basename, exists

from os import stat
import hashlib

import pickle


# TODO : for each texture, if not requested, add a dummy "normal" and dummy "specular" texture
# In fact we could use small dummy "normal" and "specular" textures and reference them
# by default for ALL the sprites


# =====================================================================
# IMAGE / SPRITE SHEET
# =====================================================================
from pyrogen.src.pyrogen.rgrwindow.MAIN.gfx_components import Gfx


class ResourceImage():

    def __init__(self, name, filePath, id, spriteInfo=None, fontInfo=None):
        # ID
        self._id = id
        # Store base name
        self._name = name
        # Position
        self._x = 0
        self._y = 0

        # Create image from fontInfo
        if fontInfo != None:
            c = fontInfo["character"]
            x = fontInfo["x"]
            y = fontInfo["y"]
            w = fontInfo["w"]
            h = fontInfo["h"]
            # font info contains the box properties
            imgFont = Image.open(filePath)
            img = imgFont.crop( (x,y,x+w,y+h) )
            self._img = img
        else:
            # Load Pillow image into memory and set RGBA mode
            img = Image.open(filePath)
            self._img = img.convert("RGBA")
        # SpriteSheet config (by default only 1 sprite, full Size)
        self._nbSpriteX = 1
        self._nbSpriteY = 1
        self._spriteW   = self.width
        self._spriteH   = self.height
        # Configure the sprite sheet if requested
        if spriteInfo != None:
            self._nbSpriteX = spriteInfo[0]     # nb sprite frames along X-axis
            self._nbSpriteY = spriteInfo[1]     # nb sprite frames along Y-axis
            self._spriteW   = spriteInfo[2]     # Width of each sprite frame
            self._spriteH   = spriteInfo[3]     # Height of each sprite frame
        # Compute and store hash (based on file properties and image size
        st = stat(filePath)
        h = hashlib.sha256()
        h.update(name.encode()             )     # name
        h.update(filePath.encode()         )     # file path
        h.update(bytearray(st.st_size)     )     # file size
        h.update(str(st.st_mtime).encode() )     # last modification date
        h.update(bytearray(self.width)     )     # image width
        h.update(bytearray(self.height)    )     # image height
        h.update(bytearray(self._nbSpriteX))    # nb sprite frames along X-axis
        h.update(bytearray(self._nbSpriteY))    # nb sprite frames along Y-axis
        h.update(bytearray(self._spriteW  ))    # Width of each sprite frame
        h.update(bytearray(self._spriteH  ))    # Height of each sprite frame
        d = h.hexdigest()
        # keep only the 32 middle characters
        self._hash = d[16:48]

    @property
    def x0(self):
        return self._x
    @property
    def y0(self):
        return self._y
    @x0.setter
    def x0(self,v):
        self._x = v
    @y0.setter
    def y0(self,v):
        self._y = v

    @property
    def width(self):
        return self._img.size[0]
    @property
    def height(self):
        return self._img.size[1]
    @property
    def x1(self):
        return self.x0 + self.width -1
    @property
    def y1(self):
        return self.y0 + self.height -1

    @property
    def spriteWidth(self):
        return self._spriteW
    @property
    def spriteHeight(self):
        return self._spriteH


    @property
    def data(self):
        return self._img
    @property
    def name(self):
        return  self._name
    @property
    def hash(self):
        return self._hash
    @property
    def id(self):
        return self._id

    @property
    def nbSpriteX(self):
        return self._nbSpriteX
    @property
    def nbSpriteY(self):
        return self._nbSpriteY
    @property
    def spriteW(self):
        return self._spriteW
    @property
    def spriteH(self):
        return self._spriteH

    def __str__(self):
        return f"<Image id:{self.id} name:'{self.name}' - x:{self.x0} - y:{self.y0} - w:{self.width} - h:{self.height} - nbX:{self.nbSpriteX} - nbY:{self.nbSpriteY} - hash:'{self.hash}'>"



# =====================================================================
# ATLAS CREATION ALGORITHM
# =====================================================================
class Box():

    def __init__(self, imgRsc, newId, index=0):
        # Prepare sub coords
        w = imgRsc.spriteW
        h = imgRsc.spriteH
        ix = index %  imgRsc.nbSpriteX
        iy = index // imgRsc.nbSpriteX
        x0 = imgRsc.x0 + ix*w
        y0 = imgRsc.y0 + iy*h
        x1 = x0 + w
        y1 = y0 + h
        # Store box and image
        self._id   = newId
        self._x    = x0
        self._y    = y0
        self._name = f"{imgRsc.name}"
        if imgRsc.nbSpriteX > 1 or imgRsc.nbSpriteY > 1:
            self._name += f"_{index}"
        self._img  = imgRsc.data.crop( (x0,y0,x1,y1) )

    @property
    def x0(self):
        return self._x
    @property
    def y0(self):
        return self._y
    @x0.setter
    def x0(self,v):
        self._x = v
    @y0.setter
    def y0(self,v):
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
    def hasChildren(self):
        return len(self._children) > 0

    def __str__(self):
        return f"<SURFACE : {self.x0}/{self.y0}/{self.width}/{self.height}>"

    def insertBox(self, box, border=3):
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
                        box = Box(img, ResourceLoader.getUniqueID(), idx)
                        boxes.append(box)
        return boxes

    # -----------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------
    def __init__(self, squareSize, imgBorder, resImgList):
        self._size   = squareSize
        self._border = imgBorder
        self._boxes  = self._createBoxes(resImgList)
        self._out = []
        self._surface = Surface(0, 0, self._size, self._size)

    def _processInternal3(self):
        while len(self._boxes) > 0:
            # take first box
            box = self._boxes[0]
            self._boxes = self._boxes[1:]
            # Split surfaces with current box
            isOK = self._surface.insertBox(box, self._border)
            if isOK:
                self._out.append(box)
            else:
                print(f"Impossible to add box {box}")
                return False
        return True


    def process(self):
        self._out = []
        res = self._processInternal3()
        return res, self._out


# =====================================================================
# RESOURCE LOADER
# =====================================================================
class ResourceLoader():

    _uniqueID = 0
    @staticmethod
    def getUniqueID():
        res = ResourceLoader._uniqueID
        ResourceLoader._uniqueID += 1
        return res

    def _drawAtlas(self, size, packedImgList):
        im1 = Image.new("RGBA",(size,size))
        for p in packedImgList:
            im1.paste(p.data, (p.x0,p.y0))
        return im1

    def _dumpData(self, boxList, dumpPath):
        objList = []
        i = 0
        for box in boxList:
            obj = {'id'  : i,
                   'name': box.name,
                   'x'   : box.x0,
                   'y'   : box.y0,
                   'w'   : box.width,
                   'h'   : box.height,
                   }
            objList.append(obj)
            i += 1
        fp = open(dumpPath, "wb")
        pickle.dump(objList, fp)
        fp.close()
    def _loadData(self, loadPath):
        fp = open(loadPath, "rb")
        objList = pickle.load(fp)
        fp.close()
        return objList

    def __init__(self):
        self._fonts         = []
        self._images        = {}
        self._textureByName = {}
        self._textureByID   = {}

    def addImage(self, name, imgPath, spriteInfo=None):
        id     = ResourceLoader.getUniqueID()
        imgRef = ResourceImage(name, imgPath, id, spriteInfo)
        #print(f"[LOADER][ADD] {imgRef}")
        if name in self._images:
            raise RuntimeError("ERROR: ResourceLoader - addImage - {name} is already registered")
        self._images[name] = imgRef

    # TODO do not regenerate font png file if already exists and not modified
    def addFont(self, name, fontPath, size=128, border=5, color=(255,255,255,255)):
        fontAtlasPath = f"atlas/font_{name}.png"
        fontDataPath  = f"atlas/font_{name}.dat"
        if not exists(fontAtlasPath) or not exists(fontDataPath):
            # prepare char dimensions
            chars = {}
            # Open font using PIL
            fnt = ImageFont.truetype(fontPath, size)
            # For each ascii value (one byte length) check the width and height
            maxW = 0
            maxH = 0
            asciiMin = 32
            asciiMax = 128
            for ascii in range(asciiMin, asciiMax):
                v = ascii
                c = chr(ascii)
                # real size of the char
                dw, dh   = fnt.getsize(c)
                ofx, ofy = fnt.getoffset(c)
                chars[v] = {"char":c,
                            "size":size,
                            "width":dw,
                            "height":dh,
                            "offX":ofx,
                            "offY":ofy,
                            }
                maxW = max(maxW, dw)
                maxH = max(maxH, dh)
            maxW += 2*border
            maxH += 2*border
            # Here we have the maximum size of one character for the entire font
            # and we have a dictionary containing all character sizes
            # Create image and draw font characters
            N = 10
            W = N * maxW
            H = N * maxH
            im1 = Image.new("RGBA", (W,H), (0,0,0,0))
            dr1 = ImageDraw.Draw(im1)
            xRef = border
            yRef = border
            # prepare output
            OUT = {}
            for ascii in range(asciiMin, asciiMax):
                # Local data
                v   = ascii
                c   = chars[v]["char"]
                dw  = chars[v]["width"]
                dh  = chars[v]["height"]
                ofx = chars[v]["offX"]
                ofy = chars[v]["offY"]
                # Update position
                if xRef+dw+border >= W:
                    xRef  = border
                    yRef += maxH
                # Fill output
                OUT[v] = {"character":c,
                          "x":xRef,
                          "y":yRef,
                          "w":dw,
                          "h":dh}
                # Draw character at the right place
                # Y offset seems to ne used only to align characters correctly
                # So it seems useless to use it in the following code lines
                #dr1.rectangle((xRef,yRef,xRef+dw,yRef+dh),outline=color)
                #dr1.rectangle((xRef-border,yRef-border,xRef+dw+border,yRef+dh+border),outline=color)
                dr1 = ImageDraw.Draw(im1)
                dr1.text((xRef-ofx,yRef), c, font=fnt, fill=color)
                # Step to next estimated character position
                xRef += dw + 2*border
            # Save font image
            im1.save(fontAtlasPath)
            # Save font data
            fp = open(fontDataPath, "wb")
            pickle.dump(OUT, fp)
            fp.close()
        # Add font to list
        self._fonts.append(name)


    def generateImageAtlas(self, squareSize, border, force=False):
        # Browse all images and get their hash, in order to create the atlas hash
        h = hashlib.sha256()
        h.update(str(squareSize).encode())
        h.update(str(border).encode())
        for name in self._images:
            img = self._images[name]
            h.update(img.hash.encode())
        # Browse all fonts too
        for name in self._fonts:
            h.update(name.encode())
        d = h.hexdigest()
        atlasHash = d[16:48]
        atlasPath = f"atlas/atlas_{atlasHash}.png"
        dumpPath  = f"atlas/atlas_{atlasHash}.dat"

        # If the hash version of the atlas is not already generated,
        # We have to recreate it from scratch
        if not exists(atlasPath) or not exists(dumpPath) or force:
            print(f"\nGenerate new atlas (hash={atlasHash}) - side = {squareSize}")

            # Add images from fonts
            for name in self._fonts:
                # open data for this font
                fp = open(f"atlas/font_{name}.dat", "rb")
                fontData = pickle.load(fp)
                fp.close()
                # for each character, create an image
                for ch in fontData:
                    id = ch
                    info = fontData[ch]
                    charImg = ResourceImage(f"{name}_{id}", f"atlas/font_{name}.png", id, fontInfo=info)
                    self._images[f"{name}_{id}"] = charImg

            # First sort images by biggest width then biggest height
            lst = self._images.values()
            lst = sorted(lst, key=lambda x:(-x.spriteWidth,-x.spriteHeight))

            # For each image, make it fit into a squareSize structure
            binPacking   = BinPacking(squareSize, border, lst)
            res, boxList = binPacking.process()

            # Create atlasInfo Data (JSON format)
            self._dumpData(boxList, dumpPath)

            # when the structure is ready, use PILLOW to create the final atals
            # copy and paste images into it : Add a 2-pixel border with full transparency
            # in order to avoid texture bleeding during rendering
            im1 = self._drawAtlas(squareSize, boxList)
            im1.save(atlasPath)
            if not res:
                raise RuntimeError("Impossible to finish the Atlas generation !")
        else:
            print(f"\nRestore previous atlas (hash={atlasHash}) - size = {squareSize}")

        # Open json file and store atlas information
        textureList = self._loadData(dumpPath)
        for texture in textureList:
            id   = texture["id"]
            name = texture["name"]
            self._textureByID[id]     = texture
            self._textureByName[name] = texture

        self._atlasPath  = atlasPath


    def storeFonts(self, fsgpu):
        fonts = {}
        for f in self._fonts:
            minAscii = 32
            maxAscii = 127
            # Create block in the gpu
            # create it in the last part of the memory, as these data will not be modified,
            # it is better to put it far away from the modified areas (Sprites, ...)
            # because it will avoid updating data pages for nothing
            dataSize = maxAscii-minAscii+1
            blockID = fsgpu.alloc(dataSize, Gfx.TYPE_FONT, searchFromEnd=True)
            # Create array.array buffer in order to store font data
            data = array.array("f", [0.0, ] * int(dataSize))
            # store each texture ID related to each character ascii value
            i = 0
            for ascii in range(minAscii, maxAscii+1):
                name = f"{f}_{ascii}"
                charTex = self.getTextureByName(name)
                data[i] = charTex["id"]
                i += 1
            # copy the data into the FS GPU once for all
            fsgpu.write2Texture(blockID, data)
            # Store the blockID for this font
            fonts[f] = blockID
        # Store new list of fonts
        self._fonts = fonts

    def getNbTextures(self):
        if len(self._textureByName) != len(self._textureByID):
            print(self._textureByName,file=sys.stderr)
            print(self._textureByID, file=sys.stderr)
            raise RuntimeError("[ERROR] Difference between texture dicts !")
        return len(self._textureByName)

    def getTextureByName(self, name):
        if name not in self._textureByName:
            raise RuntimeError(f"[ERROR] name:{name} not in texture dict !")
        return self._textureByName[name]

    def getTextureById(self, id):
        if id not in self._textureByID:
            raise RuntimeError(f"[ERROR] id:{id} not in texture dict !")
        return self._textureByID[id]

    def getAllIds(self):
        return list(self._textureByID.keys())

    def getTextureAtlasPath(self):
        return self._atlasPath

    def getTextureImage(self):
        dirPath  = Path(__file__).parent.resolve()
        filePath = self.getTextureAtlasPath()
        image = Image.open(f"{dirPath}/{filePath}").convert("RGBA")
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        return image

    def getFontIDFromName(self, fontName):
        return self._fonts[fontName]