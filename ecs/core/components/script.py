
## ============================================================
## IMPORTS
## ============================================================
from .component import Component



## ============================================================
## SCRIPT COMPONENT
## ============================================================

class Script(Component):

    # Constructor. Init the isActive flag
    def __init__(self, compName=None):
        if compName == None:
            compName = "SCRIPT"
        # Parent constructor
        super().__init__(compName)

    # method to get current type
    def getType(self):
        return Component.TYPE_SCRIPT

    # method to override in the idle components
    def updateScript(self, scriptName, deltaTime):
        raise ValueError("[ERR] updateScriptinterface method not implemented yet !")


