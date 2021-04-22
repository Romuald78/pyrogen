

class Gfx():

    _loader = None

    @staticmethod
    def setLoader(loader):
        Gfx._loader = loader



class GfxSprite():

    def __init__(self, textureName, width=-1, height=-1, x=0.0, y=0.0, angle=0.0, scale=1.0, filterColor=(255,255,255)):
        # Get texture info from loader
        tex = Gfx._loader.getTextureByName(textureName)
        id  = tex["id"]
        w   = tex["w"]
        h   = tex["h"]
        # if width or height is not filled, use the texture ones
        if width > 0:
            w = width
        if height > 0:
            h = height
        # Store information for this gfx component
        self._id     = id
        self._xc     = x
        self._yc     = y
        self._width  = w
        self._height = h
        self._angle  = angle
        self._color  = filterColor
        self._scale  = scale

    @property
    def textureID(self):
        return self._id
    @property
    def color(self):
        return self._color

    @property
    def centerX(self):
        return self._xc
    @property
    def centerY(self):
        return self._yc

    @property
    def width(self):
        return self._width*self._scale
    @property
    def height(self):
        return self._height*self._scale

    @property
    def angle(self):
        return self._angle
    @property
    def scale(self):
        return self._scale

    @color.setter
    def color(self, v):
        self._color = v

    @centerX.setter
    def centerX(self, v):
        self._xc = v
    @centerY.setter
    def centerY(self, v):
        self._yc = v

    @angle.setter
    def angle(self, v):
        self._angle = v
    @scale.setter
    def scale(self, v):
        self._scale = v

    def __str__(self):
        return f"<GfxSprite : id={self.textureID} x={self.centerX} y={self.centerY} w={self.width} h={self.height} scale={self.scale} />"


