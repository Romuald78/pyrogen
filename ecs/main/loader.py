import arcade
import sys


class ResourceLoader():

    _textures = {}

    ## -------------------------------------
    ## DEBUG
    ## -------------------------------------
    @staticmethod
    def getMemoryInfo():
        res = {
            "LoaderTex":f"{sys.getsizeof(ResourceLoader._textures)}/{len(ResourceLoader._textures)}",
        }
        return res


    @staticmethod
    def hasTexture(name):
        return name in ResourceLoader._textures

    @staticmethod
    def getTexture(name):
        if name not in ResourceLoader._textures:
            raise ValueError(f"[ERR] Resource Loader : impossible to retrieve the required texture {name}")
        return ResourceLoader._textures[name]

    @staticmethod
    def addTexture(name, path, xRef, yRef, w, h, flipH, flipV, hitAlgo):
        if name not in ResourceLoader._textures:
            tex = arcade.load_texture( path,
                                       xRef, yRef, w, h,
                                       flipped_horizontally=flipH,
                                       flipped_vertically=flipV,
                                       hit_box_algorithm=hitAlgo )
            ResourceLoader._textures[name] = tex
        else:
            raise ValueError(f"[ERR] Resource Loader : texture name is already used {name} !")
