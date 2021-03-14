# FEATURE enable or disable (or enable during pause) Entities : that would be useful
# to handle these states by entity instead of by component (keep by component anyway)

class Entity():

    #---------------------------------------------
    # COMPONENT ID
    #---------------------------------------------
    # Static field
    _maxEntID = 0
    @staticmethod
    def getNewID():
        Entity._maxEntID += 1
        return Entity._maxEntID


    ## -------------------------------------
    ## CONSTRUCTOR
    ## -------------------------------------
    def __init__(self, entName=None):
        self._ID = Entity.getNewID()
        if entName == None:
            entName = "ENTITY"
        self._name      = entName
        self._debugName = f"e_{entName}_{self._ID}"
        # init component list
        self._compByName = {}
        self._compByRef  = {}
        self._scene      = None


    ## -------------------------------------
    ## SCENE LINK
    ## -------------------------------------
    def linkToScene(self, scn):
        self._scene = scn
    def getScene(self):
        return self._scene
    def destroy(self):
        # notify Scene that this entity must be removed
        if self._scene == None:
            raise ValueError("[ERR] component destroy request : no scene linked !")
        # Destroy all components FIRST
        keys = list(self._compByRef.keys())
        # But first we have to disable all of them in order to avoid script problems
        for ref in keys:
            ref.disable()
        # then destroy all components
        for i in range(len(keys)):
            ref = keys[i]
            self.removeComponent(ref)
        # Clean entity dicts
        self._compByName = {}
        self._compByRef  = {}
        # Then ask scene to destroy entity
        self._scene.removeEntity(self)


    # ---------------------------------------------
    # ENTITY INFORMATION
    # ---------------------------------------------
    def getName(self):
        return self._name
    def getDebugName(self):
        return self._debugName
    # Unique ID
    def getID(self):
        return self._ID


    ## -------------------------------------
    ## COMPONENT MANAGEMENT
    ## -------------------------------------
    def addComponent(self, cmpRef):
        # Get name of this component
        cmpName = cmpRef.getName()
        # Add ref into NAME dict
        if cmpName not in self._compByName:
            self._compByName[cmpName] = []
        if cmpRef in self._compByName[cmpName]:
            raise ValueError("[ERR] addComponent : ref is already in the name dict !")
        self._compByName[cmpName].append(cmpRef)
        # Add name into REF dict
        if cmpRef in self._compByRef:
            raise ValueError("[ERR] addComponent : ref is already in the ref dict !")
        self._compByRef[cmpRef] = cmpName
        # Link this comp to current entity
        cmpRef.linkToEntity(self)
        # If there is already a scene, register this new component
        # to the scene NOW, because all others components have been
        # registered when the Entity-Scene link has been established
        if self._scene != None:
            self._scene.notifyAddComponent(cmpRef)

    def removeComponent(self, cmpRef):
        # empty names to clean
        emptyNames = []
        # remove from name dict
        for compName in self._compByName:
            if cmpRef in self._compByName[compName]:
                self._compByName[compName].remove(cmpRef)
            if len(self._compByName[compName]) == 0:
                emptyNames.append(compName)
        # clean empty names
        for nam in emptyNames:
            if nam in self._compByName:
                del self._compByName[nam]
        # remove from ref dict
        if cmpRef in self._compByRef:
            del self._compByRef[cmpRef]
        # notify the scene this component is no more (if this entity is linked to a scene)
        if self._scene != None:
            self.getScene().notifyRemoveComponent(cmpRef)

    def getNbComponents(self):
        return len(self._compByRef)

    def getComponentsByName(self, cmpName):
        res = []
        if cmpName in self._compByName:
            res = self._compByName[cmpName]
        return res

    def getFirstComponentByName(self, cmpName):
        res = self.getComponentsByName(cmpName)
        if len(res)>=1:
            res = res[0]
        return res

    def hasComponent(self, cmpRef):
        return cmpRef in self._compByRef

    def getComponentList(self):
        return list(self._compByRef.keys())

