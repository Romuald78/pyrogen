from .component import Component

class Script(Component):

    __slots__ = ["_priority",]

    def __init__(self, priority=0, name="Script"):
        super().__init__(Component.TYPE_SCRIPT, name)
        # Store priority value
        self._priority = priority

    def updateScript(self, deltaTime, systemTime):
        raise RuntimeError("[ERROR] updateScript() method has not been implemented yet !")

    def setPriority(self, newP):
        self._priority = newP
        scn = self.getScene()
        if scn != None:
            scn.notifyChangeScriptPriority(self)

    def getPriority(self):
        return self._priority

