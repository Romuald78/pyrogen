

class Component():

    TYPE_GFX    = 1
    TYPE_SCRIPT = 2

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

