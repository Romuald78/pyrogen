

class Component():

    TYPE_GFX          = 1
    TYPE_SCRIPT       = 2
    TYPE_KEY          = 3
    TYPE_PAD_BUTTON   = 4
    TYPE_MOUSE_BUTTON = 5
    TYPE_PAD_AXIS     = 6


    # ------------------------------------
    #  SLOTS
    # ------------------------------------
    __slots__ = ['_name',
                 '_type',
                 '_entity'
                ]

    def __init__(self, type, name="Component"):
        self._entity = None
        self._name   = name
        self._type   = type

    def getName(self):
        return self._name

    def getType(self):
        return self._type

    def getPriority(self):
        return 0

    # ------------------------------------
    #  ENTITY LINK
    # ------------------------------------
    def setEntity(self, ent):
        if self._entity != None:
            raise RuntimeError(f"[ERROR] Impossible to make a link between this component {self} and another entity !")
        self._entity = ent

    def resetEntity(self, ent):
        if self._entity != ent:
            raise RuntimeError(f"[ERROR] Impossible to remove a link between this component {self} and its entity !")
        self._entity = None

    # ------------------------------------
    #  SCENE LINK
    # ------------------------------------
    def getScene(self):
        res = None
        if self._entity != None:
            res = self._entity.getScene()
        return res
