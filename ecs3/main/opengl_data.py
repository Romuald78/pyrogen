

class OpenGLData():

    def __init__(self):
        self._data = {
            # TEXTURE ATLAS
            "textureAtlas" : None,  # ALL sprite texture (albedo, diffuse, specular)
            "nbTextures"   : None,  # integer
            "atlasInfo"    : None,  # Texture containing all texture information

            # LIGHTS
            "nbLights"     : None,  # integer
            "lightInfo"    : None,  # Texture containing all light information

            # VERTEX
            "nbSprites"    : None,  # integer (number of vertices)
            "spriteSize"   : None,  # integer (data size for one vertex)
            "vertexBuffer" : None,  # vertex buffer
            "vertexData"   : None,  # vertex data copied to the vertex buffer
            "vao"          : None,  # Vertex array object

            # FILE SYSTEM
            "fsGpu"        : None,  # Texture used to store the FS in GPU

            # PROJECTION MATRIX
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

