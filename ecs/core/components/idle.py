
## ============================================================
## IMPORTS
## ============================================================
from .component import Component



## ============================================================
## SCRIPT COMPONENT
## ============================================================

class Idle(Component):

    # constructor
    def __init__(self, compName=None):
        if compName == None :
            compName = "USER"
        super().__init__(compName)

    # method to get current type
    def getType(self):
        return Component.TYPE_IDLE

