
## ============================================================
## IMPORTS
## ============================================================
import math

from .component import Component



## ============================================================
## SCRIPT COMPONENT
## ============================================================


class Transform(Component):


    # constructor
    def __init__(self, compName=None):
        if compName == None :
            compName = "TRANSFORM"
        super().__init__(compName)
        # Create position
        self._x  = 0
        self._y  = 0
        self._z  = 0
        # Create rotation
        self._rx = 0
        self._ry = 0
        self._rz = 0


    # method to get current type
    def getType(self):
        return Component.TYPE_TRANSFORM


    # ----------------------------------------
    # MOVE AND ROTATE
    # ----------------------------------------
    # Move center position according to rotation and anchor point
    def _rotateAnchorZ(self, rotZ, anchorPos):
        # Set angle to radians
        rotZ *= math.pi/180.0
        # get relative position
        x0, y0, z0 = anchorPos
        x1, y1, z1 = self.position
        x1 -= x0
        y1 -= y0
        z1 -= z0
        # Create rotation matrix elements
        c = math.cos(rotZ)
        s = math.sin(rotZ)
        # Rotate
        x2, y2, z2 = ( x1*c-y1*s, +x1*s+y1*c, z1 )
        # get absolute position now
        x2 += x0
        y2 += y0
        z2 += z0
        self.position = (x2,y2,z2)
    # Set angle between -180°/+180°
    def _saturateAngle(self, ang):
        return ((ang+360000)%360)
    # Translate position
    def translateTo(self, position):
        self._x  = position[0]
        self._y  = position[1]
        self._z  = position[2]
    def translate(self, position):
        self._x += position[0]
        self._y += position[1]
        self._z += position[2]
    # rotate on Z-axis
    def rotateZTo(self, rotZ, anchorPos=None):
        self._rx  = 0
        self._ry  = 0
        self._rz  = self._saturateAngle(rotZ)
        if anchorPos != None:
            self._rotateAnchorZ(rotZ, anchorPos)
    def rotateZ(self, rotZ, anchorPos=None):
        self._rx += 0
        self._ry += 0
        self._rz += self._saturateAngle(rotZ)
        print(self._rz)
        if anchorPos != None:
            self._rotateAnchorZ(rotZ, anchorPos)



    # ----------------------------------------
    # POSITION GETTERS
    # ----------------------------------------
    @property
    def position(self):
        return (self._x,self._y,self._z)
    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
    @property
    def z(self):
        return self._z


    # ----------------------------------------
    # ROTATION GETTERS
    # ----------------------------------------
    @property
    def rotation(self):
        return (self._rx, self._ry, self._rz)
    @property
    def rx(self):
        return self._rx
    @property
    def ry(self):
        return self._ry
    @property
    def rz(self):
        return self._rz


    # ----------------------------------------
    # POSITION SETTERS
    # ----------------------------------------
    @position.setter
    def position(self, newPos):
        if len(newPos) != 3:
            raise RuntimeError(f"[ERROR] setting new transform position : position length does not fit {newPos}")
        self._x = newPos[0]
        self._y = newPos[1]
        self._z = newPos[2]
    @x.setter
    def x(self, newX):
        self._x = newX
    @y.setter
    def y(self, newY):
        self._y = newY
    @z.setter
    def z(self, newZ):
        self._z = newZ


    # ----------------------------------------
    # ROTATION SETTERS
    # ----------------------------------------
    @rotation.setter
    def rotation(self, newRot):
        if len(newRot) != 3:
            raise RuntimeError(f"[ERROR] setting new transform rotation : rotation length does not fit {newRot}")
        self._rx = newRot[0]
        self._ry = newRot[1]
        self._rz = newRot[2]
    @rx.setter
    def rx(self, newRX):
        self._rx = newRX
    @ry.setter
    def ry(self, newRY):
        self._ry = newRY
    @rz.setter
    def rz(self, newRZ):
        self._rz = newRZ


