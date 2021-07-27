import math

from ....ecs3.components.script import Script


class MoveCircle(Script):

    def __init__(self, gfx, center, radius, speed, keyboard, name="MoveCircle"):
        super().__init__(1, name)
        self._gfx    = gfx
        self._center = [ center[0], center[1] ]
        self._radius = radius
        self._speed  = speed    # degrees per second
        self._key    = keyboard

    def updateScript(self, deltaTime, systemTime):
        # Move center according to pressed keys
        if self._key.isPressed("moveUp"):
            self._center[1] -= 20 * 60 * deltaTime
        if self._key.isPressed("moveDown"):
            self._center[1] += 20 * 60 * deltaTime

        # Set the position according to the speed and system time
        x = math.cos(self._speed*systemTime*2*math.pi/360) * self._radius + self._center[0]
        y = math.sin(self._speed*systemTime*2*math.pi/360) * self._radius + self._center[1]

        self._gfx.setX(x)
        self._gfx.setY(y)



class MoveSquare(Script):

    def __init__(self, gfx, center, radius, speed, keyboard, name="MoveCircle"):
        super().__init__(1, name)
        self._gfx    = gfx
        self._center = [ center[0], center[1] ]
        self._radius = radius
        self._speed  = speed    # degrees per second
        self._key    = keyboard

    def updateScript(self, deltaTime, systemTime):
        # Move center according to pressed keys
        if self._key.isPressed("moveLeft"):
            self._center[0] -= 20 * 60 * deltaTime
        if self._key.isPressed("moveRight"):
            self._center[0] += 20 * 60 * deltaTime

        # Set the position according to the speed and system time
        ratio = self._speed*systemTime/360
        while ratio < 0.0:
            ratio += 1.0
        while ratio > 1.0:
            ratio -= 1.0
        if ratio <0.25:
            x = 2*self._radius * ratio *4 - self._radius + self._center[0]
            y = - self._radius + self._center[1]
        elif ratio < 0.5:
            y = 2 * self._radius * (ratio-0.25) * 4 - self._radius + self._center[1]
            x = self._radius + self._center[0]
        elif ratio < 0.75:
            y = self._radius + self._center[1]
            x = - 2*self._radius * (ratio-0.5) *4 + self._radius + self._center[0]
        else:
            x = - self._radius + self._center[0]
            y = - 2 * self._radius * (ratio-0.75) * 4 + self._radius + self._center[1]

        self._gfx.setX(x)
        self._gfx.setY(y)

