
## ============================================================
## IMPORTS
## ============================================================
from ..components.script import Script
import sys


## ============================================================
## SCRIPT MANAGER
## ============================================================

class ScriptSystem():

    ## -------------------------------------
    ## private methods
    ## -------------------------------------
    def __checkType(self, ref):
        if not isinstance(ref, Script):
            raise ValueError(f"[ERR] add script : bad object type. It should be ScriptInterface !\n{ref}")

    ## -------------------------------------
    ## Constructor
    ## -------------------------------------
    def __init__(self):
        self._scrByName = {}
        self._scrByRef  = {}


    ## -------------------------------------
    ## DEBUG
    ## -------------------------------------
    def getMemoryInfo(self):
        res = {
            "scrRef":f"{sys.getsizeof(self._scrByRef)}/{len(self._scrByRef)}",
            "scrNam":f"{sys.getsizeof(self._scrByName)}/{len(self._scrByName)}"
        }
        return res


    ## -------------------------------------
    ## Registering methods
    ## -------------------------------------
    def add(self, scriptRef):
        # check type
        self.__checkType(scriptRef)
        # Get script name
        scriptName = scriptRef.getName()
        # Add script into name dict
        if scriptName not in self._scrByName:
            self._scrByName[scriptName] = []
        if scriptRef in self._scrByName[scriptName]:
            raise ValueError("[ERR] scriptSystem add : component is already in the name dict !")
        self._scrByName[scriptName].append(scriptRef)
        # Add script into ref dict
        if scriptRef in self._scrByRef:
            raise ValueError("[ERR] scriptSystem add : component is already in the ref dict !")
        self._scrByRef[scriptRef] = scriptName

    def removeScript(self, scriptRef):
        # empty names to clean
        emptyNames = []
        # remove from name dict
        for compName in self._scrByName:
            if scriptRef in self._scrByName[compName]:
                self._scrByName[compName].remove(scriptRef)
            if len(self._scrByName[compName]) == 0:
                emptyNames.append(compName)
        # clean empty names
        for nam in emptyNames:
            if nam in self._scrByName:
                del self._scrByName[nam]
        # remove from ref dict
        if scriptRef in self._scrByRef:
            del self._scrByRef[scriptRef]


    ## -------------------------------------
    ## Main method
    ## -------------------------------------
    def updateAllScripts(self, deltaTime, isOnPause):
        # Browse all scripts
        keys = list(self._scrByRef.keys())
        for i in range(len(keys)):
            ref = keys[i]
        #for ref in self._scrByRef:
            # check if this component is enabled
            if ref.isEnabled():
                #check if this component is enabled during pause or it is not the pause
                if ref.isEnabledOnPause() or (not isOnPause):
                    ref.updateScript(ref.getName(), deltaTime)


