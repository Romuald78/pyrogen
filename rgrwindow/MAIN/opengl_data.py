

class OpenGLData():

    def __init__(self):
        self._data = {
            # Atlas texture
            "diffuseAtlas" : None,  # ALL sprite texture (sprite/diffuse)
            "normalAtlas"  : None,  # ALL sprite texture (normal)
            "specularAtlas": None,  # ALL sprite texture (specular)

            "nbTextures"   : None,  # integer
            "atlasInfo"    : None,  # Texture containing all texture information

            "nbLights"     : None,  # integer
            "lightInfo"    : None,  # Texture containing all light information

            "nbSprites"    : None,  # integer (number of vertices)
            "spriteSize"   : None,  # integer (data size for one vertex)
            "spriteBuffer" : None,  # vertex buffer
            "vertexData"   : None,  # vertex data copied to the vertex buffer

            "vao"          : None,  # Vertex array object
            "projMatrix"   : None,  # Projection matrix (used for camera feature)
        }

    def get(self,name):
        return self._data[name]

    def set(self, name, value):
        self._data[name] = value

