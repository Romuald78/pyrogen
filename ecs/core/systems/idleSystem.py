
## ============================================================
## IMPORTS
## ============================================================



## ============================================================
## IDLE MANAGER
## ============================================================
from ..components.idle import Idle


class IdleSystem():

    ## -------------------------------------
    ## private methods
    ## -------------------------------------
    def __checkType(self, ref):
        if not isinstance(ref, Idle):
            raise ValueError(f"[ERR] add idle : bad object type. It should be ScriptInterface !\n{ref}")

    ## -------------------------------------
    ## Constructor
    ## -------------------------------------
    def __init__(self):
        self._refList  = {}
        self._nameList = {}


    ## -------------------------------------
    ## Registering methods
    ## -------------------------------------
    def add(self, idleRef):
        # check type
        self.__checkType(idleRef)
        # get name
        idleName = idleRef.getName()
        # Add into name list
        if idleName not in self._nameList:
            self._nameList[idleName] = []
        if idleRef in self._nameList[idleName]:
            raise ValueError(f"[ERR] IDLE add : script already in the name list !")
        self._nameList[idleName].append(idleRef)
        # Add into ref list
        if idleRef in self._refList:
            raise ValueError(f"[ERR] IDLE add : script already in the ref list !")
        self._refList[idleRef] = idleName

    # FEATURE : add methods to improve IdleSystem
    # e.g. : remove / getCompByName / hasComp / getNbComps / getAllComps / ...

