

class OpenGLData():

    def __init__(self):
        self._data = {
            # Atlas texture
            "textureAtlas" : None,  # ALL sprite texture (albedo, diffuse, specular)

            "nbTextures"   : None,  # integer
            "atlasInfo"    : None,  # Texture containing all texture information

            "nbLights"     : None,  # integer
            "lightInfo"    : None,  # Texture containing all light information

            "nbSprites"    : None,  # integer (number of vertices)
            "spriteSize"   : None,  # integer (data size for one vertex)
            "vertexBuffer" : None,  # vertex buffer
            "vertexData"   : None,  # vertex data copied to the vertex buffer

            "fsTable"      : None,  # Texture buffer used to store the FS allocation table
            "fsData"       : None,  # Texture buffer used to store the FS data

            "vao"          : None,  # Vertex array object
            "projMatrix"   : None,  # Projection matrix (used for camera feature)
        }

    def get(self,name):
        if name not in self._data:
            raise ValueError(f"[ERROR][OpenGlData] get field '{name}' is not correct ")
        return self._data[name]

    def set(self, name, value):
        if name not in self._data:
            raise ValueError(f"[ERROR][OpenGlData] set field '{name}' is not correct ")
        self._data[name] = value

