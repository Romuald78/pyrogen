
## ============================================================
## IMPORTS
## ============================================================
import arcade.experimental.lights as arcade
from .component import Component



## ============================================================
## SCRIPT COMPONENT
## ============================================================

class LightFx(Component):

    # constructor
    def __init__(self, position, radius, color, mode, compName=None):
        if compName == None :
            compName = "USER"
        super().__init__(compName)
        self._light = arcade.Light(position[0], position[1],radius, color, mode)

    # method to get current type
    def getType(self):
        return Component.TYPE_LIGHT

    # Get internal light object
    def getFx(self):
        return self._light

    # position
    def getPosition(self):
        return self._light.position
    def setPosition(self, newPos):
        self._light.position = newPos
    def move(self,dx, dy):
        oldPos = self._light.position
        self._light.position = (oldPos[0]+dx, oldPos[1]+dy)

    # radius
    def getRadius(self):
        return self._light.radius
    def setRadius(self, newRad):
        self._light.radius = newRad

