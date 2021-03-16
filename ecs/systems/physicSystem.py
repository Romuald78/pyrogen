

## ============================================================
## IMPORTS
## ============================================================
import pymunk

from ..components.physic import Physic, PhysicCollision


## ============================================================
## SCRIPT MANAGER
## ============================================================

class PhysicSystem():

    ## -------------------------------------
    ## PRIVATE METHODS
    ## -------------------------------------
    def __checkType(self, ref):
        if not isinstance(ref, Physic) and not isinstance(ref, PhysicCollision):
            raise ValueError(f"[ERR] add physic : bad object type. It should be Physic or PhysicCollision!\n{ref}")


    ## -------------------------------------
    ## CONSTRUCTOR
    ## -------------------------------------
    def __init__(self, gravity=(0,0), damping=0.01):
        # Create component dicts
        self._phyByName = {}
        self._phyByRef  = {}
        # Create physic environment
        self._space         = pymunk.Space()
        self._space.gravity = gravity
        self._space.damping = damping
        # Get debug info
        self._info = pymunk.SpaceDebugDrawOptions()


    ## -------------------------------------
    ## (UN)REGISTERING
    ## -------------------------------------
    def add(self, phyRef):
        # check type
        self.__checkType(phyRef)
        # Get script name
        scriptName = phyRef.getName()
        # Check if we have to add a physic body OR a physic collision handler
        if isinstance(phyRef, Physic):
            # Add script into name dict
            if scriptName not in self._phyByName:
                self._phyByName[scriptName] = []
            if phyRef in self._phyByName[scriptName]:
                raise ValueError("[ERR] physicSystem add : component is already in the name dict !")
            self._phyByName[scriptName].append(phyRef)
            # Add script into ref dict
            if phyRef in self._phyByRef:
                raise ValueError("[ERR] physicSystem add : component is already in the ref dict !")
            self._phyByRef[phyRef] = scriptName
            # Add the body into the physic space
            bdyList = phyRef.getBodyList()
            self._space.add(bdyList[0][0],bdyList[0][1])


    def remove(self, phyRef):
        # Remove from ref dict
        if phyRef in self._phyByRef:
            self._phyByRef.pop(phyRef)
        # Remove from name dict
        for nam in self._phyByName:
            if phyRef in self._phyByName[nam]:
                self._phyByName[nam].remove(phyRef)
        # Remove bodies from physic space
        bdyList = phyRef.getBodyList()
        self._space.remove(bdyList[0][0], bdyList[0][1])

    ## -------------------------------------
    ## UPDATE METHOD
    ## -------------------------------------
    def updatePhysicEngine(self, deltaTime, isOnPause):

        # update physic world (except if we are on pause)
        if not isOnPause:
            self._space.step(deltaTime)
            # display info
            # self._space.debug_draw(self._info)


    ## -------------------------------------
    ## DRAW DEBUG INFO
    ## -------------------------------------
    def drawDebug(self):
        for phyComp in self._phyByRef:
            phyComp.drawDebug()


    ## -------------------------------------
    ## PHYSIC WORLD
    ## -------------------------------------
    def addCollisionHandler(self, colType1, colType2, callbacks, data):
        # Create collision handler in physic world
        handler = self._space.add_collision_handler(colType1, colType2)
        # add all needed data for the current handler
        for entry in data:
            handler.data[entry] = data[entry]
        # Connect callbacks
        if "begin" in callbacks:
            handler.begin    = callbacks["begin"]
        if "separate" in callbacks:
            handler.separate = callbacks["separate"]



