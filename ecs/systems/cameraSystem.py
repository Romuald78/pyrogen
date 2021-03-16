
## ============================================================
## IMPORTS
## ============================================================



## ============================================================
## IDLE MANAGER
## ============================================================
from ..components.camera import Camera


class CameraSystem():


    ## -------------------------------------
    ## private methods
    ## -------------------------------------
    def __checkType(self, ref):
        if not isinstance(ref, Camera):
            raise ValueError(f"[ERR] add camera : bad object type. It should be Camera !\n{ref}")


    ## -------------------------------------
    ## Constructor
    ## -------------------------------------
    def __init__(self, scene):
        self._scene        = scene
        self._refList      = {}
        self._nameList     = {}
        self._activeCamera = None


    ## -------------------------------------
    ## Registering methods
    ## -------------------------------------
    def add(self, camRef):
        # check type
        self.__checkType(camRef)
        # get name
        camName = camRef.getName()
        # Add into name list
        if camName not in self._nameList:
            self._nameList[camName] = []
        if camRef in self._nameList[camName]:
            raise ValueError(f"[ERR] CAMERA add : script already in the name list !")
        self._nameList[camName].append(camRef)
        # Add into ref list
        if camRef in self._refList:
            raise ValueError(f"[ERR] CAMERA add : script already in the ref list !")
        self._refList[camRef] = camName
        # Now the component is added, check if there was a camera bound with the system
        if self._activeCamera == None:
            self._activeCamera = camRef


    ## -------------------------------------
    ## Setter methods
    ## -------------------------------------
    def setActiveCamera(self, camRef):
        if camRef not in self._refList:
            raise RuntimeError("[ERROR] setActiveCamera : camera reference is not registered in the list !")
        self._activeCamera = camRef


    ## -------------------------------------
    ## Main process methods
    ## -------------------------------------
    def update(self, deltaTime):
        # update all cameras info
        for camRef in self._refList:
            camRef.update(deltaTime)

        # check if there is an active camera (else keep the last viewport)
        if self._activeCamera != None:
            # Get application
            application = self._scene.getApplication()
            # Get scene dimension (either full screen or window)
            sceneW, sceneH = application.get_size()
            # Get camera lookat position
            camX, camY = self._activeCamera.center
            camW, camH = self._activeCamera.size
            # Get cam real dimensions according to screen size
            xr = camW / sceneW
            yr = camH / sceneH
            ratio = max(xr, yr)
            # final dimensions and offset
            finalW = int(ratio * sceneW)
            finalH = int(ratio * sceneH)
            refX   = int(camX - (finalW / 2))
            refY   = int(camY - (finalH / 2))
            # Set the viewport according to
            #print(camX, camY, camW, camH, sceneW, sceneH, refX, refY, finalW, finalH)
            application.set_viewport(refX, refX+finalW, refY, refY+finalH)

