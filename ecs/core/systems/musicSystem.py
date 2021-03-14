

## ============================================================
## IMPORTS
## ============================================================
from ..components.sfx import Music
import sys


## ============================================================
## SCRIPT MANAGER
## ============================================================

class MusicSystem():

    ## -------------------------------------
    ## private methods
    ## -------------------------------------
    def __checkType(self, ref):
        if not isinstance(ref, Music):
            raise ValueError(f"[ERR] add script : bad object type. It should be Sfx !\n{ref}")


    ## -------------------------------------
    ## Constructor
    ## -------------------------------------
    def __init__(self):
        self._musicByName = {}
        self._musicByRef  = {}


    ## -------------------------------------
    ## DEBUG
    ## -------------------------------------
    def getMemoryInfo(self):
        res = {
            "musicRef":f"{sys.getsizeof(self._musicByRef)}/{len(self._musicByRef)}",
            "musicNam":f"{sys.getsizeof(self._musicByName)}/{len(self._musicByName)}"
        }
        return res


    ## -------------------------------------
    ## Registering methods
    ## -------------------------------------
    def add(self, musicRef):
        # check type
        self.__checkType(musicRef)
        # Get script name
        scriptName = musicRef.getName()
        # Add script into name dict
        if scriptName not in self._musicByName:
            self._musicByName[scriptName] = []
        if musicRef in self._musicByName[scriptName]:
            raise ValueError("[ERR] scriptSystem add : component is already in the name dict !")
        self._musicByName[scriptName].append(musicRef)
        # Add script into ref dict
        if musicRef in self._musicByRef:
            raise ValueError("[ERR] scriptSystem add : component is already in the ref dict !")
        self._musicByRef[musicRef] = scriptName

    def removeMusic(self, musicRef):
        # empty names to clean
        emptyNames = []
        # remove from name dict
        for compName in self._musicByName:
            if musicRef in self._musicByName[compName]:
                self._musicByName[compName].remove(musicRef)
            if len(self._musicByName[compName]) == 0:
                emptyNames.append(compName)
        # clean empty names
        for nam in emptyNames:
            if nam in self._musicByName:
                del self._musicByName[nam]
        # remove from ref dict
        if musicRef in self._musicByRef:
            del self._musicByRef[musicRef]
        # Stop playing
        musicRef.stop()

    ## -------------------------------------
    ## Main method
    ## -------------------------------------
    def updateAllMusics(self, deltaTime, isOnPause):
        # Browse all scripts
        keys = list(self._musicByRef.keys())
        for i in range(len(keys)):
            ref = keys[i]
            # check if this component is enabled
            if ref.isEnabled():
                #check if this component is enabled during pause or it is not the pause
                if ref.isEnabledOnPause() or (not isOnPause):
                    # update process for Music objects
                    ref.updateMusic(deltaTime)