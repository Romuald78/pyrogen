


class Entity():

    def __init__(self, name="Entity"):
        self._name = name
        self._scene = None
        self._componentsByName = {}
        self._componentsByRef  = []

    def setScene(self, scn):
        if self._scene != None:
            raise RuntimeError("[ERROR] Impossible to attach a scene to this entity !")
        self._scene = scn
        # Register components if some have already been added
        for c in self._componentsByRef:
            self._scene.registerComponent(c)

    def resetScene(self, scn):
        if self._scene != scn:
            raise RuntimeError("[ERROR] Impossible to remove a scene link !")
        self._scene = None
        # Unregister components if needed
        for c in self._componentsByRef:
            self._scene.unregisterComponent(c)

    def getName(self):
        return self._name

    def getScene(self):
        return self._scene

    def destroy(self):
        # Remove all components
        for c in self._componentsByRef:
            self.removeComponent(c)
        # Remove the entity from the scene (if needed)


    def addComponent(self, ref):
        if ref in self._componentsByRef:
            raise RuntimeError("[ERROR] Impossible to add a component into this entity !")
        # Add component
        self._componentsByRef.append(ref)
        self._componentsByName[ref.getName()] = ref
        # Create link between component and entity
        ref.setEntity(self)
        # Register this component if a scene has been already attached
        if self._scene != None:
            self._scene.registerComponent(ref)

    def removeComponent(self, ref):
        if ref not in self._componentsByRef:
            raise RuntimeError("[ERROR] Impossible to remove a component from this entity !")
        # Unregister from the scene (if needed)
        if self._scene != None:
            self._scene.unregisterComponent(ref)
        # Remove link between component and entity
        ref.resetEntity(self)
        # Forget Component
        self._componentsByRef.remove(ref)
        del self._componentsByName[ref.getName()]


    def getNbComponents(self):
        return len(self._componentsByRef)

    def getComponentsByName(self, name):
        out = None
        if name in self._componentsByName:
            out = self._componentsByName[name]
        return out

    def getComponentsByType(self, type):
        out = []
        for c in self._componentsByRef:
            if c.getType() == type:
                out.append(c)
        return out
