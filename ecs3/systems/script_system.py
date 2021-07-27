from .base_system import BaseSystem

class ScriptSystem(BaseSystem):

    def __init__(self):
        super().__init__()

    def notifyChangeScriptPriority(self, ref):
        # Remove the component and add it once again
        self.removeComponent(ref)
        self.addComponent(ref)

    def updateScripts(self, deltaTime, systemTime):
        # Update all the Script components
        for c in self._compByRef:
            c.updateScript(deltaTime, systemTime)
