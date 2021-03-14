import math

from .component import Component


class Camera(Component):

    # FEATURE : handle 3d coordinates to handle zoom with a focal field ?
    # TODO    : For the moment keep only the 2 first coordinates

    def __init__(self, center, size, compName="Camera"):
        # Get parameters
        center    = list(center)
        size      = size

        super().__init__(compName)
        self._center     = center
        self._size       = size
        self._moveTarget = self._center
        self._moveSpeed  = 0
        self._minMove    = 0
        self._moving     = False
        self._mode       = "linear"
        self._zoom       = 1.0

    def getType(self):
        return Component.TYPE_CAMERA

    def getRelativePosition(self,absolutePosition):
        x, y = absolutePosition
        x -= self.x + self.w/2
        y -= self.y + self.h/2
        return (x,y)

    @property
    def center(self):
        return self._center
    @property
    def x(self):
        return self._center[0]
    @property
    def y(self):
        return self._center[1]
    @property
    def size(self):
        siz = (self._size[0]/self._zoom, self._size[1]/self._zoom)
        return siz
    @property
    def w(self):
        return self._size[0]
    @property
    def h(self):
        return self._size[1]
    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self,newZoom):
        if newZoom > 0:
            self._zoom = newZoom

    def moveTo(self, targetPos, speed, minMoveDist, mode="linear"):
        self._moveSpeed  = speed
        self._mode       = mode
        self._moveTarget = targetPos
        self._minMove    = minMoveDist

    def update(self, deltaTime):
        # Get distance to target
        dx  = self._moveTarget[0] - self._center[0]
        dy  = self._moveTarget[1] - self._center[1]
        dx2 = dx * dx
        dy2 = dy * dy
        # If the distance is too big : start moving camera
        if not self._moving:
            if dx2 + dy2 >= self._minMove*self._minMove:
                self._moving = True

        # If the distance is too smal : fix the camera centered to the target
        if self._moving :
            limit2 = 9
            if self._mode == "linear":
                limit2 = self._moveSpeed*self._moveSpeed
            if dx2 + dy2 <= limit2:
                self._moving = False
                self._center[0] = self._moveTarget[0]
                self._center[1] = self._moveTarget[1]

        # Move camera center if needed
        if self._moving:
            if self._mode == "linear":
                ang  = math.atan2(dy,dx)
                self._center[0] += math.cos(ang) * self._moveSpeed * 60 * deltaTime
                self._center[1] += math.sin(ang) * self._moveSpeed * 60 * deltaTime
            elif self._mode == "log":
                self._center[0] += dx / self._moveSpeed
                self._center[1] += dy / self._moveSpeed
            elif self._mode == "teleport":
                self._center[0] = self._moveTarget[0]
                self._center[1] = self._moveTarget[1]



