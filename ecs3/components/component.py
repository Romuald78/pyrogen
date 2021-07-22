

class Component():

    TYPE_GFX = 1

    # ------------------------------------
    #  SLOTS
    # ------------------------------------
    __slots__ = ['_name',
                 '_type',
                ]

    def __init__(self, type, name="Component"):
        self._name = name
        self._type = type

    def getName(self):
        return self._name

    def getType(self):
        return self._type

