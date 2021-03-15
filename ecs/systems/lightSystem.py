
## ============================================================
## IMPORTS
## ============================================================



## ============================================================
## LIGHT MANAGER
## ============================================================
from arcade.experimental.lights import LightLayer

from ..components.light import LightFx


class LightSystem():

    ## -------------------------------------
    ## private methods
    ## -------------------------------------
    def __checkType(self, ref):
        if not isinstance(ref, LightFx):
            raise ValueError(f"[ERR] add Light : bad object type. It should be ScriptInterface !\n{ref}")

    ## -------------------------------------
    ## Constructor
    ## -------------------------------------
    def __init__(self, screenW, screenH):
        self._refList  = {}
        self._nameList = {}
        self._lightLayer = LightLayer(screenW, screenH)
        self._ambientColor = (255,255,255)


    def getLayer(self):
        return self._lightLayer

    ## -------------------------------------
    ## Modifying ambient_color
    ## -------------------------------------
    def setAmbient(self,newColor):
        self._ambientColor = newColor


    ## -------------------------------------
    ## Registering methods
    ## -------------------------------------
    def add(self, lightRef):
        # check type
        self.__checkType(lightRef)
        # get name
        lightName = lightRef.getName()
        # Add into name list
        if lightName not in self._nameList:
            self._nameList[lightName] = []
        if lightRef in self._nameList[lightName]:
            raise ValueError(f"[ERR] IDLE add : script already in the name list !")
        self._nameList[lightName].append(lightRef)
        # Add into ref list
        if lightRef in self._refList:
            raise ValueError(f"[ERR] IDLE add : script already in the ref list !")
        self._refList[lightRef] = lightName
        # Add it to the light layer
        self._lightLayer.add(lightRef.getFx())

    # FEATURE : add methods to improve lightSystem
    # e.g. : remove / getCompByName / hasComp / getNbComps / getAllComps / ...
    def remove(self,lightRef):
        self._lightLayer.remove(lightRef.getFx())


    def draw(self):
        self._lightLayer.draw(ambient_color=self._ambientColor)
