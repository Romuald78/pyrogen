from .component import Component

class Script(Component):

    def __init__(self, priority=0, name="Script"):
        super().__init__(Component.TYPE_SCRIPT, name)
        # Store priority value
        self._priority = priority

    def updateScript(self, deltaTime, systemTime):
        raise RuntimeError("[ERROR] updateScript() method has not been implemented yet !")

    def setPriority(self, newP):
        self._priority = newP

    def getPriority(self):
        return self._priority